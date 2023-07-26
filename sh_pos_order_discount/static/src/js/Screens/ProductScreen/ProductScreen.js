odoo.define("sh_pos_order_discount.ProductScreen", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const NumpadWidget = require("point_of_sale.NumpadWidget");
    const ProductScreen = require("point_of_sale.ProductScreen");
    const OrderWidget = require("point_of_sale.OrderWidget");

    const ShProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            _setValue(val) {
                super._setValue(val);

                var mode = this.state.numpadMode;
                var order = this.env.pos.get_order();
                if (order.get_selected_orderline()) {
                    if (mode == "discount") {
                        order.get_selected_orderline().set_discount(0);
                        var sh_dic =order.get_selected_orderline().get_global_discount()
                        sh_dic = parseFloat(sh_dic).toFixed(2)
                        order.get_selected_orderline().set_discount(sh_dic);

                        var price = order.get_selected_orderline().get_display_price();
                        var current_price = (price * val) / 100;
                        var discount = ((order.get_selected_orderline().get_display_price() * order.get_selected_orderline().quantity - current_price) / (order.get_selected_orderline().price * order.get_selected_orderline().quantity)) * 100;
                        discount = discount.toFixed(2)
                        order.get_selected_orderline().set_discount(discount);
                    }
                }
            }
            
        };
    Registries.Component.extend(ProductScreen, ShProductScreen);
});
