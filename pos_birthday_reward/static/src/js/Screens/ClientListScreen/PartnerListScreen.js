odoo.define('pos_birthday_reward.ClientListScreen', function(require) {
    'use strict';

    const PartnerListScreen = require('point_of_sale.PartnerListScreen')
    const Registries = require("point_of_sale.Registries");

    const KnkClientListScreen = (PartnerListScreen) =>
        class KnkClientListScreen extends PartnerListScreen {
            setup(){
                super.setup();
            }
            confirm() {
                super.confirm()
                var self = this;
                var client = this.state.selectedPartner;
                if (client) {
                    if (this.env.pos.config.is_first_order_apply) {
                        if (client.is_birthdate_month && client.birthday_order_counter == 0) {
                            var order = this.env.pos.selectedOrder;
                            if (order) {
                                _.each(order.orderlines, function(obj) {
                                    obj.set_birthday_discount(self.env.pos.config.birthday_discount);
                                });
                            }
                        } else {
                            var order = this.env.pos.selectedOrder;
                            if (order) {
                                _.each(order.orderlines, function(obj) {
                                    obj.set_birthday_discount(0);
                                });
                            }
                        }
                    } else {
                        if (client.is_birthdate_month) {
                            var order = this.env.pos.selectedOrder;
                            if (order) {
                                _.each(order.orderlines, function(obj) {
                                    obj.set_birthday_discount(self.env.pos.config.birthday_discount);
                                });
                            }
                        } else {
                            var order = this.env.pos.selectedOrder;
                            if (order) {
                                _.each(order.orderlines, function(obj) {
                                    obj.set_birthday_discount(0);
                                });
                            }
                        }
                    }

                }
                else{
                    var order = this.env.pos.selectedOrder;
                    if (order) {
                        _.each(order.orderlines, function(obj) {
                            obj.set_birthday_discount(0);
                        });
                    }
                }
            }

        }
    Registries.Component.extend(PartnerListScreen, KnkClientListScreen)
})