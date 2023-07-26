odoo.define("sh_pos_order_discount.RemoveDiscountButton", function (require) {

    const PosComponent = require("point_of_sale.PosComponent");
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require("point_of_sale.Registries");
    const ProductScreen = require("point_of_sale.ProductScreen");

    class RemoveDiscountButton extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }
        async onClick() {
            var orderlines = this.env.pos.get_order().get_orderlines();
            if (orderlines) {
                _.each(orderlines, function (each_orderline) {
                    each_orderline.set_discount(0);
                    each_orderline.set_global_discount(0);
                });
                this.env.pos.get_order().set_order_global_discount(0.00)
            }
        }
    }
    RemoveDiscountButton.template = "RemoveDiscountButton";
    ProductScreen.addControlButton({
        component: RemoveDiscountButton,
        condition: function () {
            return this.env.pos.config.sh_allow_global_discount || this.env.pos.config.sh_allow_order_line_discount;
        },
    });
    Registries.Component.add(RemoveDiscountButton);

    return { RemoveDiscountButton };
});
