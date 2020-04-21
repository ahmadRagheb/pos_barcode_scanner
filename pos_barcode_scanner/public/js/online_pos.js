POSItems.prototype.get_items = function ({ start = 0, page_length = 40, search_value = '', item_group = this.parent_item_group } = {}) {
    const price_list = this.frm.doc.selling_price_list;
    return new Promise(res => {
        frappe.call({
            method: "pos_barcode_scanner.api.get_items",
            freeze: true,
            args: {
                start,
                page_length,
                price_list,
                item_group,
                search_value,
                pos_profile: this.frm.doc.pos_profile
            }
        }).then(r => {
            // const { items, serial_no, batch_no } = r.message;

            // this.serial_no = serial_no || "";
            res(r.message);
        });
    });
}

POSItems.prototype.set_item_in_the_cart = function (items, serial_no, batch_no, barcode) {
    // if (serial_no) {
    //     this.events.update_cart(items[0].item_code,
    //         'serial_no', serial_no);
    //     this.reset_search_field();
    //     return;
    // }

    // if (batch_no) {
    //     this.events.update_cart(items[0].item_code,
    //         'batch_no', batch_no);
    //     this.reset_search_field();
    //     return;
    // }

    if (items.length === 1 && barcode) {
        this.events.update_cart(items[0].item_code, 'qty', '+1');
    }
}