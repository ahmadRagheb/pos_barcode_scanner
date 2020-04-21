
from __future__ import unicode_literals
import frappe, json
from frappe.utils.nestedset import get_root_of
from frappe.utils import cint
from erpnext.accounts.doctype.pos_profile.pos_profile import get_item_groups
from erpnext.selling.page.point_of_sale.point_of_sale import search_serial_or_batch_or_barcode_number

@frappe.whitelist()
def get_items(start, page_length, price_list, item_group, search_value="", pos_profile=None):

	data = dict()
	warehouse = ""
	display_items_in_stock = 0
	search_by_barcode = 0
	
	if pos_profile:
		search_by_barcode, warehouse, display_items_in_stock = frappe.db.get_value('POS Profile', pos_profile, ['search_by_barcode_only', 'warehouse', 'display_items_in_stock'])

	if not frappe.db.exists('Item Group', item_group):
		item_group = get_root_of('Item Group')
	
	
	if search_value:
		if search_by_barcode:
			data = search_barcode_number(search_value)
		else:
			data = search_serial_or_batch_or_barcode_number(search_value)
	
	if search_by_barcode:
		item_code = data.get("item_code") if data.get("item_code") else ""
		barcode = data.get("barcode") if data.get("barcode") else search_value
	else:
		item_code = data.get("item_code") if data.get("item_code") else search_value
		barcode = data.get("barcode") if data.get("barcode") else ""

	serial_no = data.get("serial_no") if data.get("serial_no") else ""
	batch_no = data.get("batch_no") if data.get("batch_no") else ""
	
	
	# items_code = items_contain_barcode(search_value)

	condition = get_conditions(item_code, serial_no, batch_no, barcode)

	if pos_profile:
		condition += get_item_group_condition(pos_profile)

	lft, rgt = frappe.db.get_value('Item Group', item_group, ['lft', 'rgt'])
	# locate function is used to sort by closest match from the beginning of the value


	result = []

	items_data = frappe.db.sql(""" SELECT name as item_code,
			item_name, image as item_image, idx as idx,is_stock_item
		FROM
			`tabItem`
		WHERE
			disabled = 0 and has_variants = 0 and is_sales_item = 1
			and item_group in (select name from `tabItem Group` where lft >= {lft} and rgt <= {rgt})
			and {condition} order by idx desc limit {start}, {page_length}"""
		.format(
			start=start, page_length=page_length,
			lft=lft, rgt=rgt,
			condition=condition,
		), as_dict=1)

	if items_data:
		items = [d.item_code for d in items_data]
		item_prices_data = frappe.get_all("Item Price",
			fields = ["item_code", "price_list_rate", "currency"],
			filters = {'price_list': price_list, 'item_code': ['in', items]})

		item_prices, bin_data = {}, {}
		for d in item_prices_data:
			item_prices[d.item_code] = d


		if display_items_in_stock:
			filters = {'actual_qty': [">", 0], 'item_code': ['in', items]}

			if warehouse:
				filters['warehouse'] = warehouse

			bin_data = frappe._dict(
				frappe.get_all("Bin", fields = ["item_code", "sum(actual_qty) as actual_qty"],
				filters = filters, group_by = "item_code")
			)

		for item in items_data:
			row = {}

			row.update(item)
			item_price = item_prices.get(item.item_code) or {}
			row.update({
				'price_list_rate': item_price.get('price_list_rate'),
				'currency': item_price.get('currency'),
				'actual_qty': bin_data.get('actual_qty')
			})

			result.append(row)

	res = {
		'items': result
	}

	if serial_no:
		res.update({
			'serial_no': serial_no
		})

	if batch_no:
		res.update({
			'batch_no': batch_no
		})

	if barcode:
		res.update({
			'barcode': barcode
		})

	return res


def search_barcode_number(search_value):
	# search barcode no
	barcode_data = frappe.db.get_value('Item Barcode', {'barcode': search_value}, ['barcode', 'parent as item_code'], as_dict=True)
	if barcode_data:
		return barcode_data

	return {}

def items_contain_barcode(search_value):
	items_code = []
	if search_value:
		items_code = frappe.db.sql("""SELECT DISTINCT parent FROM `tabItem Barcode` where barcode like {barcode}""".format(barcode = frappe.db.escape('%' + search_value + '%')), as_dict=1)
	
	condition = []
	for ic in items_code:
		condition.append("item_code like '%s'"%(ic.parent))
	if condition:
		return " or {}".format((" or ".join(condition)))
	return ""

	
def get_conditions(item_code, serial_no, batch_no, barcode):
	if serial_no or batch_no or barcode:
		return "name like {0}".format(frappe.db.escape(item_code))

	return """(name like {item_code} or item_name like {item_code})""".format(item_code = frappe.db.escape('%' + item_code + '%'))
    
def get_item_group_condition(pos_profile):
	cond = "and 1=1"
	item_groups = get_item_groups(pos_profile)
	if item_groups:
		cond = "and item_group in (%s)"%(', '.join(['%s']*len(item_groups)))

	return cond % tuple(item_groups)