odoo.define('bi_pos_warranty.OrderWidget', function(require) {
	"use strict";

	const PosComponent = require('point_of_sale.PosComponent');
	const Registries = require('point_of_sale.Registries');
	const OrderWidget = require('point_of_sale.OrderWidget');

	const BiOrderWidget = (OrderWidget) =>
		class extends OrderWidget {
			setup() {
				super.setup();
			}

			async _editPackLotLines(event) {
				let self = this;
				const orderline = event.detail.orderline;
				const isAllowOnlyOneLot = orderline.product.isAllowOnlyOneLot();
				const packLotLinesToEdit = orderline.getPackLotLinesToEdit(isAllowOnlyOneLot);
				const { confirmed, payload } = await this.showPopup('EditListPopup', {
					title: this.env._t('Lot/Serial Number(s) Required'),
					isSingleItem: isAllowOnlyOneLot,
					array: packLotLinesToEdit,
				});
				if (confirmed) {
					// Segregate the old and new packlot lines
					const modifiedPackLotLines = Object.fromEntries(
						payload.newArray.filter(item => item.id).map(item => [item.id, item.text])
					);
					const newPackLotLines = payload.newArray
						.filter(item => !item.id)
						.map(item => ({ lot_name: item.text }));

					let go_on = 0;
					let order = this.env.pos.get_order();
					order.set_lots_data();
					let used_lots_rec = order.get_used_lots();
					let all_lots_rec = order.get_all_lots();
					let count = 0;
					$.each(modifiedPackLotLines, function( i, line ){
						count += 1
						let lot_name = line.toString();
						let x = used_lots_rec.indexOf(lot_name);
						let y = all_lots_rec.indexOf(lot_name);

						if (x == -1 && y >= 0){
							go_on += 1;
						}
						if(x == -1 && y == -1 ){
							return self.showPopup('ErrorPopup', {
								title: self.env._t("Error: LOT Doesn't exists"),
								body: self.env._t("This lot is not exist, please enter valid lot.."),
							});
						}
						if(x >= 0){
							return self.showPopup('ErrorPopup', {
								title: self.env._t("Error: LOT already used"),
								body: self.env._t("This lot number is already used , please use another"),
							});
						}
					});

					$.each(newPackLotLines, function( i, line ){
						count += 1
						let lot_name = line['lot_name'].toString();
						let x = used_lots_rec.indexOf(lot_name);
						let y = all_lots_rec.indexOf(lot_name);
						if (x == -1 && y >= 0){
							go_on += 1;
						}
						if(x == -1 && y == -1 ){
							return self.showPopup('ErrorPopup', {
								title: self.env._t("Error: LOT Doesn't exists"),
								body: self.env._t("This lot is not exist, please enter valid lot.."),
							});
						}
						if(x >= 0){
							return self.showPopup('ErrorPopup', {
								title: self.env._t("Error: LOT already used"),
								body: self.env._t("This lot number is already used , please use another"),
							});
						}
					});

					if(go_on == count){
						orderline.setPackLotLines({ modifiedPackLotLines, newPackLotLines });
					}

				}
				this.order.select_orderline(event.detail.orderline);
			}
		};

	Registries.Component.extend(OrderWidget, BiOrderWidget);

	return OrderWidget;

});
