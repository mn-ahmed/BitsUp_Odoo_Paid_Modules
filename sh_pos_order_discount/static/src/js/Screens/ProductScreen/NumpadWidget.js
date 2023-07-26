odoo.define("sh_pos_order_discount.NumpadWidget", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const NumpadWidget = require("point_of_sale.NumpadWidget");
    const ProductScreen = require("point_of_sale.ProductScreen");
    const OrderWidget = require("point_of_sale.OrderWidget");

    const PosNumpadWidget = (NumpadWidget) =>
        class extends NumpadWidget {
            changeMode(mode) {
                super.changeMode(mode);
                var self = this;
                if (mode && mode == "discount" && self.env.pos.config.sh_allow_order_line_discount) {
                    self.env.pos.is_global_discount = false;
                    let { confirmed, payload } = this.showPopup("GlobalDiscountPopupWidget");
                    if (confirmed) {
                    } else {
                        return;
                    }
                }
            }
        };
    Registries.Component.extend(NumpadWidget, PosNumpadWidget);
});
