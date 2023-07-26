odoo.define('bi_pos_warranty.models', function(require) {
	"use strict";

	var { Order } = require('point_of_sale.models');
	const Registries = require('point_of_sale.Registries');
	var rpc = require('web.rpc');
	
	const PosOrder = (Order) => class PosOrder extends Order {
		constructor(obj, options) {
			super(...arguments);
			this.set_lots_data();
		}
		set_lots_data(){
			var self = this;
			this.used_lots = this.used_lots || [];
			this.all_lots = this.all_lots || [];
			setInterval(function () {
				rpc.query({
					model: 'pos.order',
					method: 'check_warranty_reg',
					args: [1],
				}).then(function(output) {
					self.set_used_lots(output[0]);
					self.set_all_lots(output[1]);
				});
			}, 5000);
		}
		set_all_lots(all_lots){
			this.all_lots = all_lots;
		}
		get_all_lots(){
			return this.all_lots;
		}
		set_used_lots(used_lots){
			this.used_lots = used_lots;
		}
		get_used_lots(){
			return this.used_lots;
		}

	}
	Registries.Model.extend(Order, PosOrder);
});