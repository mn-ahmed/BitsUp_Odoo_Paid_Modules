odoo.define("sh_pos_order_discount.GlobalDiscountButton", function (require) {

    const PosComponent = require("point_of_sale.PosComponent");
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require("point_of_sale.Registries");
    const ProductScreen = require("point_of_sale.ProductScreen");

    class GlobalDiscountButton extends PosComponent {
        setup() {
            super.setup();
            useListener('click', this.onClick);
        }
        async onClick() {
            if (this.env.pos.get_order().get_orderlines() && this.env.pos.get_order().get_orderlines().length > 0) {
                this.env.pos.is_global_discount = true;
                let { confirmed, payload } = this.showPopup("GlobalDiscountPopupWidget");
                if (confirmed) {
                    return true
                } else {
                    return;
                }
            } else {
                alert("Add Product In Cart.");
            }
        }
    }
    GlobalDiscountButton.template = "GlobalDiscountButton";
    ProductScreen.addControlButton({
        component: GlobalDiscountButton,
        condition: function () {
            return this.env.pos.config.sh_allow_global_discount;
        },
    });
    Registries.Component.add(GlobalDiscountButton);

    return { GlobalDiscountButton };
});
