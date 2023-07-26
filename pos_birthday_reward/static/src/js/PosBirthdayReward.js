odoo.define('pos_birthday_reward.pos_birthday_reward', function(require) {
    "use strict";

    const {Orderline,Order} = require('point_of_sale.models');
    var core = require('web.core');
    var utils = require('web.utils');
    const Registries = require("point_of_sale.Registries");


    var _t = core._t;
    var round_pr = utils.round_precision;

    const NewOrder = (Order) =>
        class NewOrder extends Order {
        add_product(product, options) {
            super.add_product(product, options);
            var self = this;
            var order = this.pos.selectedOrder;
            if (order.get_partner()) {
                if (self.pos.config.is_first_order_apply) {
                    if (order.get_partner().is_birthdate_month == true && order.get_partner().birthday_order_counter == 0) {
                        _.each(order.orderlines, function(obj) {
                            obj.set_birthday_discount(self.pos.config.birthday_discount);
                        });
                    }
                } else {
                    if (order.get_partner().is_birthdate_month == true) {
                        _.each(order.orderlines, function(obj) {
                            obj.set_birthday_discount(self.pos.config.birthday_discount);
                        });
                    }
                }

            }
        }
    };
    Registries.Model.extend(Order, NewOrder);

    const NewOrderLine = (Orderline) =>
        class NewOrderLine extends Orderline {
        constructor(obj, options) {
            super(...arguments);
            this.membership_birthmonth_discount = 0;
            this.member_birthmonth_discountStr = '';
        }
        set_birthday_discount(birthday_discount) {
            var member_disc_birth = Math.min(Math.max(parseFloat(birthday_discount) || 0, 0), 100);
            this.membership_birthmonth_discount = member_disc_birth;
            this.member_birthmonth_discountStr = '' + member_disc_birth;
        }
        get_birthday_discount() {
            return this.membership_birthmonth_discount;
        }
        get_birthday_discount_str() {
            return this.member_birthmonth_discountStr;
        }
        
        // Method Overriding from models.js --> Orderline
        get_base_price() {
            var rounding = this.pos.currency.rounding;
            var price_computed = round_pr(this.get_unit_price() * this.get_quantity() * (1 - this.get_birthday_discount() / 100), rounding);
            price_computed = round_pr(price_computed * (1 - this.get_discount() / 100), rounding);
            return price_computed;
        }
        get_all_prices(qty = this.get_quantity()) {
            var self = this;
            var base = round_pr(this.get_unit_price() * (1.0 - (this.get_birthday_discount() / 100.0)), this.pos.currency.rounding);
            var price_unit_all = round_pr(base * (1.0 - (this.get_discount() / 100.0)), this.pos.currency.rounding);
            var price_unit = price_unit_all
            var taxtotal = 0;

            var product =  this.get_product();
            var taxes_ids = this.tax_ids || product.taxes_id;
            taxes_ids = _.filter(taxes_ids, t => t in this.pos.taxes_by_id);
            var taxdetail = {};
            var product_taxes = this.pos.get_taxes_after_fp(taxes_ids, this.order.fiscal_position);

            var all_taxes = this.compute_all(product_taxes, price_unit, qty, this.pos.currency.rounding);
            var all_taxes_before_discount = this.compute_all(product_taxes, this.get_unit_price(), qty, this.pos.currency.rounding);
            _(all_taxes.taxes).each(function(tax) {
                taxtotal += tax.amount;
                taxdetail[tax.id] = tax.amount;
            });

            return {
                "priceWithTax": all_taxes.total_included,
                "priceWithoutTax": all_taxes.total_excluded,
                "priceSumTaxVoid": all_taxes.total_void,
                "priceWithTaxBeforeDiscount": all_taxes_before_discount.total_included,
                "tax": taxtotal,
                "taxDetails": taxdetail,
            };
        }

        init_from_JSON(json) {
            this.set_birthday_discount(json.membership_birthmonth_discount);
            super.init_from_JSON(json);
        }
        export_as_JSON() {
            var json = super.export_as_JSON();
            json.membership_birthmonth_discount = this.get_birthday_discount();
            return json;
        }
        export_for_printing() {
            var print = super.export_for_printing();
            print.membership_birthmonth_discount = this.get_birthday_discount();
            return print;
        }
    };
    Registries.Model.extend(Orderline, NewOrderLine);

});