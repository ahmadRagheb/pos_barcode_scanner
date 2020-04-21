erpnext.pos.PointOfSale.prototype.get_items = function (item_code) {
    // To search item as per the key enter

    var me = this;
    this.item_serial_no = {};
    this.item_batch_no = {};

    if (item_code) {
        return $.grep(this.item_data, function (item) {
            if (item.item_code == item_code) {
                return true
            }
        })
    }
    this.items_list = this.apply_category();

    key = this.search_item.$input.val().toLowerCase().replace(/[&\/\\#,+()\[\]$~.'":*?<>{}]/g, '\\$&');
    var re = new RegExp('%', 'g');
    var reg = new RegExp(key.replace(re, '[\\w*\\s*[a-zA-Z0-9]*]*'))
    search_status = true

    if (key && this.pos_profile_data['search_by_barcode_only']) {
        return $.grep(this.items_list, function (item) {
            if (search_status) {
                if (me.barcode_data[item.item_code] &&
                    in_list(me.barcode_data[item.item_code], me.search_item.$input.val())) {
                    search_status = false;
                    return true;
                }
            }
        })

    } else if (key) {
        return $.grep(this.items_list, function (item) {
            if (search_status) {
                if (me.batch_no_data[item.item_code] &&
                    in_list(me.batch_no_data[item.item_code], me.search_item.$input.val())) {
                    search_status = false;
                    return me.item_batch_no[item.item_code] = me.search_item.$input.val()
                } else if (me.serial_no_data[item.item_code]
                    && in_list(Object.keys(me.serial_no_data[item.item_code]), me.search_item.$input.val())) {
                    search_status = false;
                    me.item_serial_no[item.item_code] = [me.search_item.$input.val(), me.serial_no_data[item.item_code][me.search_item.$input.val()]]
                    return true
                } else if (me.barcode_data[item.item_code] &&
                    in_list(me.barcode_data[item.item_code], me.search_item.$input.val())) {
                    search_status = false;
                    return true;
                } else if (reg.test(item.item_code.toLowerCase()) || (item.description && reg.test(item.description.toLowerCase())) ||
                    reg.test(item.item_name.toLowerCase()) || reg.test(item.item_group.toLowerCase())) {
                    return true
                }
            }
        })
    }
    else {
        return this.items_list;
    }
}