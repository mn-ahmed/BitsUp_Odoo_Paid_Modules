odoo.define("sh_pos_order_discount.models", function (require) {
    
    const {PosGlobalState, Order, Orderline} = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    var field_utils = require("web.field_utils");
    var utils = require('web.utils');
    var round_pr = utils.round_precision;

    const ShPosOrderDiscountOrder = (Order) => class ShPosOrderDiscountOrder extends Order {
        constructor() {
            super(...arguments);
            this.order_global_discount;
        }
        set_order_global_discount(discount) {
            this.order_global_discount = discount;
        }
        get_order_global_discount() {
            return this.order_global_discount || false;
        }
    };
    Registries.Model.extend(Order, ShPosOrderDiscountOrder);

    const ShPosOrderDiscountOrderline = (Orderline) => class ShPosOrderDiscountOrderline extends Orderline {
        constructor() {
            super(...arguments);
            this.global_discount;
            this.fix_discount;
            this.total_discount;

            if (this.order.get_orderlines().length == 0){
                this.order.set_order_global_discount(0.00)
            }

        }
        set_global_discount(global_discount) {
            this.global_discount = global_discount;
        }
        get_global_discount() {
            return this.global_discount;
        }
        set_fix_discount(discount) {
            this.fix_discount = discount;
        }
        get_fix_discount() {
            return this.fix_discount;
        }
        get_sh_discount_str() {
            return this.discount.toFixed(2);
        }
        set_total_discount(discount) {
            this.total_discount = discount;
        }
        get_total_discount() {
            return this.total_discount || false;
        }
        set_custom_discount(discount) {
            var disc = Math.min(Math.max(discount || 0, 0), 100);
            this.discount = disc;
            this.discountStr = '' +  field_utils.format.float(disc, { digits: [69, 2]});
        }
    };
    Registries.Model.extend(Orderline, ShPosOrderDiscountOrderline);

    const ShPosOrderDiscountGlobalState = (PosGlobalState) => class ShPosOrderDiscountGlobalState extends PosGlobalState {
        constructor() {
            super(...arguments);
            this.is_global_discount = false;
        }
        compute_all(taxes, price_unit, quantity, currency_rounding, handle_price_include=true) {
            var self = this;
    
            // 1) Flatten the taxes.
    
            var _collect_taxes = function(taxes, all_taxes){
                taxes = [...taxes].sort(function (tax1, tax2) {
                    return tax1.sequence - tax2.sequence;
                });
                _(taxes).each(function(tax){
                    if(tax.amount_type === 'group')
                        all_taxes = _collect_taxes(tax.children_tax_ids, all_taxes);
                    else
                        all_taxes.push(tax);
                });
                return all_taxes;
            }
            var collect_taxes = function(taxes){
                return _collect_taxes(taxes, []);
            }
    
            taxes = collect_taxes(taxes);
    
            // 2) Deal with the rounding methods
    
            var round_tax = this.company.tax_calculation_rounding_method != 'round_globally';
    
            var initial_currency_rounding = currency_rounding;
            if(!round_tax)
                currency_rounding = currency_rounding * 0.00001;
    
            // 3) Iterate the taxes in the reversed sequence order to retrieve the initial base of the computation.
            var recompute_base = function(base_amount, fixed_amount, percent_amount, division_amount){
                 return (base_amount - fixed_amount) / (1.0 + percent_amount / 100.0) * (100 - division_amount) / 100;
            }
    
            // var base = round_pr(price_unit * quantity, initial_currency_rounding);
            var  base = price_unit * quantity
    
            var sign = 1;
            if(base < 0){
                base = -base;
                sign = -1;
            }
    
            var total_included_checkpoints = {};
            var i = taxes.length - 1;
            var store_included_tax_total = true;
    
            var incl_fixed_amount = 0.0;
            var incl_percent_amount = 0.0;
            var incl_division_amount = 0.0;
    
            var cached_tax_amounts = {};
            if (handle_price_include){
                _(taxes.reverse()).each(function(tax){
                    if(tax.include_base_amount){
                        base = recompute_base(base, incl_fixed_amount, incl_percent_amount, incl_division_amount);
                        incl_fixed_amount = 0.0;
                        incl_percent_amount = 0.0;
                        incl_division_amount = 0.0;
                        store_included_tax_total = true;
                    }
                    if(tax.price_include){
                        if(tax.amount_type === 'percent')
                            incl_percent_amount += tax.amount;
                        else if(tax.amount_type === 'division')
                            incl_division_amount += tax.amount;
                        else if(tax.amount_type === 'fixed')
                            incl_fixed_amount += Math.abs(quantity) * tax.amount
                        else{
                            var tax_amount = self._compute_all(tax, base, quantity);
                            incl_fixed_amount += tax_amount;
                            cached_tax_amounts[i] = tax_amount;
                        }
                        if(store_included_tax_total){
                            total_included_checkpoints[i] = base;
                            store_included_tax_total = false;
                        }
                    }
                    i -= 1;
                });
            }
    
            var total_excluded = round_pr(recompute_base(base, incl_fixed_amount, incl_percent_amount, incl_division_amount), initial_currency_rounding);
            var total_included = total_excluded;
    
            // 4) Iterate the taxes in the sequence order to fill missing base/amount values.
    
            base = total_excluded;
    
            var skip_checkpoint = false;
    
            var taxes_vals = [];
            i = 0;
            var cumulated_tax_included_amount = 0;
            _(taxes.reverse()).each(function(tax){
                if(tax.price_include || tax.is_base_affected)
                    var tax_base_amount = base;
                else
                    var tax_base_amount = total_excluded;
    
                if(!skip_checkpoint && tax.price_include && total_included_checkpoints[i] !== undefined){
                    var tax_amount = total_included_checkpoints[i] - (base + cumulated_tax_included_amount);
                    cumulated_tax_included_amount = 0;
                }else
                    var tax_amount = self._compute_all(tax, tax_base_amount, quantity, true);
    
                tax_amount = round_pr(tax_amount, currency_rounding);
    
                if(tax.price_include && total_included_checkpoints[i] === undefined)
                    cumulated_tax_included_amount += tax_amount;
    
                taxes_vals.push({
                    'id': tax.id,
                    'name': tax.name,
                    'amount': sign * tax_amount,
                    'base': sign * round_pr(tax_base_amount, currency_rounding),
                });
    
                if(tax.include_base_amount){
                    base += tax_amount;
                    if(!tax.price_include)
                        skip_checkpoint = true;
                }
    
                total_included += tax_amount;
                i += 1;
            });
    
            return {
                'taxes': taxes_vals,
                'total_excluded': sign * round_pr(total_excluded, this.currency.rounding),
                'total_included': sign * round_pr(total_included, this.currency.rounding),
            };
        }
    };
    Registries.Model.extend(PosGlobalState, ShPosOrderDiscountGlobalState);

});
