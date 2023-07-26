/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define("pos_stock.ProductScreen", function (require) {
  "use strict";

  const { onMounted, onRendered } = owl;
  const Registries = require("point_of_sale.Registries");
  const ProductItem = require("point_of_sale.ProductItem");
  const ProductScreen = require("point_of_sale.ProductScreen");
  const ProductsWidget = require("point_of_sale.ProductsWidget");

  const PosStockProductsWidget = (ProductsWidget) => class PosStock extends ProductsWidget {
    get productsToDisplay() {
        var self = this;
        var result = super.productsToDisplay;
        if (self.env.pos.config.wk_display_stock && self.env.pos.config.wk_hide_out_of_stock) {
          var available_product = [];
          if(self.env.pos.db.wk_product_qtys){
            var data_list = Object.keys(self.env.pos.db.wk_product_qtys);
            _.each(result, function (product) {
              if (data_list.indexOf(product.id.toString()) != -1) {
                if (product.type == "service") {
                  delete self.env.pos.db.wk_product_qtys[product.id];
                }
                switch (self.env.pos.config.wk_stock_type) {
                  case "forecasted_qty":
                    if (product.virtual_available > 0 || product.type == "service")
                      available_product.push(product);
                    break;
                  case "virtual_qty":
                    if (
                      product.qty_available - product.outgoing_qty > 0 ||
                      product.type == "service"
                    )
                      available_product.push(product);
                    break;
                  default:
                    if (product.qty_available > 0 || product.type == "service") {
                      available_product.push(product);
                    }
                }
              }
            });
          }
          result = available_product;
        }
        self.env.pos.wk_change_qty_css();
        return result;
    }
  }
  Registries.Component.extend(ProductsWidget, PosStockProductsWidget);

  const PosProductItem = (ProductItem) => class extends ProductItem{
    setup() {
      super.setup();
      onMounted(this.onMounted);
      onRendered(this.onRendered);
    }
    onMounted(){
      this.render();
    }
    onRendered(){
      var product = this.props.product;
      var tag = $("#qty-tag" + product.id);
      var tag_qty = parseInt($("#qty-tag" + product.id).html());
      if(tag_qty > 0) tag.css({'background' : 'green'});
      else if(tag_qty === 0) tag.css({'background' : 'grey'});
      else tag.css({'background' : 'red'});
    }
  }
  Registries.Component.extend(ProductItem, PosProductItem);

  const PosProductScreen = (ProductScreen) => class extends ProductScreen {
      onMounted() {
        super.onMounted();
        this.env.pos.set_stock_qtys(this.env.pos.wk_product_qtys);
        this.env.pos.wk_change_qty_css();
      }
  };
  Registries.Component.extend(ProductScreen, PosProductScreen);
});
