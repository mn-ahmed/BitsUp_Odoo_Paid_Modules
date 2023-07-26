odoo.define("sh_pos_order_discount.OrderWidget", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const NumpadWidget = require("point_of_sale.NumpadWidget");
    const ProductScreen = require("point_of_sale.ProductScreen");
    const OrderSummary = require("point_of_sale.OrderSummary");
    
    const ShOrderSummary = (OrderSummary) =>
    class extends OrderSummary {
        constructor() {
            super(...arguments);
        }
        pos_discount(){
            var order = this.env.pos.get_order();
            return order.get_order_global_discount() ?  parseFloat(order.get_order_global_discount()).toFixed(2) : 0
        }
    }
    Registries.Component.extend(OrderSummary, ShOrderSummary);
});
