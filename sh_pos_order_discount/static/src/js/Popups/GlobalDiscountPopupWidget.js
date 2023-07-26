odoo.define("sh_pos_order_discount.GlobalDiscountPopupWidget", function (require) {
    
    const Registries = require("point_of_sale.Registries");
    const AbstractAwaitablePopup = require("point_of_sale.AbstractAwaitablePopup");
    var field_utils = require("web.field_utils");

    class GlobalDiscountPopupWidget extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
        }
        mounted(){
            super.mounted()
            $(".sh_discount_value").focus()
        }
        async confirm() {
            var self = this;
            this.props.resolve({ confirmed: true, payload: await this.getPayload() });

            if (!$(".sh_discount_value").val()) {
                alert("Enter amount of discount.");
                $(".sh_discount_value").addClass("invalid_number");
            } else if (
                ($(".sh_discount_value").val() && parseFloat($(".sh_discount_value").val()) > 100 && document.getElementById("discount_percentage_radio") && document.getElementById("discount_percentage_radio").checked) ||
                ($(".sh_discount_value").val() && parseFloat($(".sh_discount_value").val()) < 0) ||
                !/^\d*\.?\d*$/.test(parseFloat($(".sh_discount_value").val()))
            ) {
                $(".sh_discount_value").addClass("invalid_number");
                $(".sh_discount_value").val(" ");
                $(".sh_discount_value").focus();
            } else {
                var value = $(".sh_discount_value").val();
                value = !isNaN(value) ?
                    value :
                    isNaN(parseFloat(value)) ? 0 : field_utils.parse.float('' + value)
                if (document.getElementById("discount_fixed_radio") && document.getElementById("discount_fixed_radio").checked) {
                    if (self.env.pos.is_global_discount) {

                        var total_before = self.env.pos.get_order().get_total_with_tax()                        
                        var orderlines = self.env.pos.get_order().get_orderlines();
                        _.each(orderlines, function (each_order_line) {
                            each_order_line.set_discount(0);
                        });
                        var total_after = self.env.pos.get_order().get_total_with_tax()
                        if(total_after != total_before){
                            value = parseFloat(value) + parseFloat(( total_after - total_before).toFixed(2))
                        }
                        
                        var percentage = (value / self.env.pos.get_order().get_total_with_tax()) * 100;
                        _.each(orderlines, function (each_order_line) {
                            each_order_line.set_custom_discount(parseFloat(percentage));
                        });
                        self.env.pos.get_order().set_order_global_discount(value)

                    } else {
                        var selected_orderline = self.env.pos.get_order().get_selected_orderline();
                        if (selected_orderline) {
                            if (selected_orderline.get_discount()) {
                                var price = selected_orderline.get_display_price();
                                var current_price = price - value;
                                var discount = ((selected_orderline.price * selected_orderline.quantity - current_price) / (selected_orderline.price * selected_orderline.quantity)) * 100;
                                if (selected_orderline.get_fix_discount()) {
                                    selected_orderline.set_total_discount(selected_orderline.get_total_discount() + parseFloat(value));
                                    selected_orderline.set_fix_discount(selected_orderline.get_fix_discount() + parseFloat(value));
                                } else {
                                    selected_orderline.set_total_discount(parseFloat(value));
                                    selected_orderline.set_fix_discount(parseFloat(value));
                                }
                                selected_orderline.set_global_discount(discount);
                                selected_orderline.set_custom_discount(discount);
                            } else {
                                var apply_disc_percen = (value * 100) / selected_orderline.get_display_price();
                                selected_orderline.set_total_discount(parseFloat(value));
                                selected_orderline.set_fix_discount(parseFloat(value));
                                selected_orderline.set_global_discount(apply_disc_percen);
                                selected_orderline.set_custom_discount(apply_disc_percen)
                            }
                        }
                    }
                }
                if (document.getElementById("discount_percentage_radio") && document.getElementById("discount_percentage_radio").checked) {
                    if (self.env.pos.is_global_discount) {
                        var orderlines = self.env.pos.get_order().get_orderlines();

                        if (self.env.pos.get_order().get_order_global_discount()) {
                            self.env.pos.get_order().set_order_global_discount(self.env.pos.get_order().get_order_global_discount() + parseFloat(value));
                        } else {
                            self.env.pos.get_order().set_order_global_discount(parseFloat(value));
                        }
                        _.each(orderlines, function (each_order_line) {
                            if (each_order_line.get_discount()) {
                                var price = each_order_line.get_display_price();
                                var current_price = price - (price * value) / 100;
                                var discount = ((each_order_line.price * each_order_line.quantity - current_price) / (each_order_line.price * each_order_line.quantity)) * 100;
                                each_order_line.set_global_discount(discount);
                                each_order_line.set_custom_discount(parseFloat(discount.toFixed(2)));
                                each_order_line.set_total_discount(parseFloat(each_order_line.price) - parseFloat(each_order_line.get_display_price()));
                            } else {
                                each_order_line.set_global_discount(parseFloat(value));
                                each_order_line.set_custom_discount(parseFloat(value));
                                each_order_line.set_total_discount(parseFloat(each_order_line.price) - parseFloat(each_order_line.get_display_price()));
                            }
                        });
                    } else {
                        var selected_orderline = self.env.pos.get_order().get_selected_orderline();
                        if (selected_orderline) {
                            if (selected_orderline.get_discount()) {
                                var price = selected_orderline.get_display_price();

                                var current_price = price - (price * value) / 100;
                                var discount = ((selected_orderline.price * selected_orderline.quantity - current_price) / (selected_orderline.price * selected_orderline.quantity)) * 100;

                                selected_orderline.set_global_discount(discount);
                                selected_orderline.set_custom_discount(discount);
                                selected_orderline.set_total_discount(parseFloat(selected_orderline.price) - parseFloat(selected_orderline.get_display_price()));
                            } else {
                                selected_orderline.set_global_discount(parseFloat(value));
                                selected_orderline.set_custom_discount(parseFloat(value));
                                selected_orderline.set_total_discount(parseFloat(selected_orderline.price) - parseFloat(selected_orderline.get_display_price()));
                            }
                        }
                    }
                }
                self.cancel()
            }
        }
    }

    GlobalDiscountPopupWidget.template = "GlobalDiscountPopupWidget";
    Registries.Component.add(GlobalDiscountPopupWidget);
});
