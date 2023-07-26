odoo.define('bi_pos_warranty.productScreen', function(require) {
	"use strict";

	const PosComponent = require('point_of_sale.PosComponent');
	const Registries = require('point_of_sale.Registries');
	const NumberBuffer = require('point_of_sale.NumberBuffer');
	const ProductScreen = require('point_of_sale.ProductScreen'); 

	const BiProductScreen = (ProductScreen) =>
		class extends ProductScreen {
			setup() {
				super.setup();
			}

			async _clickProduct(event) {
				let self = this;
				if (!this.currentOrder) {
					this.env.pos.add_new_order();
				}
				const product = event.detail;
				let price_extra = 0.0;
				let draftPackLotLines, weight, description, packLotLinesToEdit;

				if (this.env.pos.config.product_configurator && _.some(product.attribute_line_ids, (id) => id in this.env.pos.attributes_by_ptal_id)) {
					let attributes = _.map(product.attribute_line_ids, (id) => this.env.pos.attributes_by_ptal_id[id])
									  .filter((attr) => attr !== undefined);
					let { confirmed, payload } = await this.showPopup('ProductConfiguratorPopup', {
						product: product,
						attributes: attributes,
					});

					if (confirmed) {
						description = payload.selected_attributes.join(', ');
						price_extra += payload.price_extra;
					} else {
						return;
					}
				}

				// Gather lot information if required.
				if (['serial', 'lot'].includes(product.tracking)) {
					const isAllowOnlyOneLot = product.isAllowOnlyOneLot();
					if (isAllowOnlyOneLot) {
						packLotLinesToEdit = [];
					} else {
						const orderline = this.currentOrder
							.get_orderlines()
							.filter(line => !line.get_discount())
							.find(line => line.product.id === product.id);
						if (orderline) {
							packLotLinesToEdit = orderline.getPackLotLinesToEdit();
						} else {
							packLotLinesToEdit = [];
						}
					}
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
							draftPackLotLines = { modifiedPackLotLines, newPackLotLines };
						}
					} else {
						// We don't proceed on adding product.
						return;
					}
				}

				// Take the weight if necessary.
				if (product.to_weight && this.env.pos.config.iface_electronic_scale) {
					// Show the ScaleScreen to weigh the product.
					if (this.isScaleAvailable) {
						const { confirmed, payload } = await this.showTempScreen('ScaleScreen', {
							product,
						});
						if (confirmed) {
							weight = payload.weight;
						} else {
							// do not add the product;
							return;
						}
					} else {
						await this._onScaleNotAvailable();
					}
				}

				// Add the product after having the extra information.
				this.currentOrder.add_product(product, {
					draftPackLotLines,
					description: description,
					price_extra: price_extra,
					quantity: weight,
				});
				NumberBuffer.reset();
			}
		};

	Registries.Component.extend(ProductScreen, BiProductScreen);

	return ProductScreen;

});
