/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define("pos_stock.models", function (require) {
  "use strict";
  var core = require("web.core");
  var rpc = require("web.rpc");
  const { Gui } = require("point_of_sale.Gui");
  const Registries = require("point_of_sale.Registries");
  var _t = core._t;
  var { PosGlobalState, Order, Orderline } = require('point_of_sale.models');
  const ProductScreen = require('point_of_sale.ProductScreen');

  const PosStock = (PosGlobalState) => class PosStock extends PosGlobalState {
    async _loadProductProduct(products) {
      var self = this;
      super._loadProductProduct(...arguments);
      await rpc.query({
        model: "pos.config",
        method: "wk_pos_fetch_pos_stock",
        args: [{
          wk_stock_type: self.config.wk_stock_type,
          wk_hide_out_of_stock: self.config.wk_hide_out_of_stock,
          config_id: self.config.id,
        }],
      })
      .then(function (result) {
        self.wk_product_qtys = result;
        self.db.wk_product_qtys = result;
        self.db.wk_hide_out_of_stock = self.config.wk_hide_out_of_stock;
      });
    }

    push_single_order(order, opts) {
      var self = this;
      if (order) {
        if (!order.is_return_order) {
          var wk_order_line = order.get_orderlines();
          for (var j = 0; j < wk_order_line.length; j++) {
            if (!wk_order_line[j].stock_location_id)
              self.wk_product_qtys[wk_order_line[j].product.id] =
                self.wk_product_qtys[wk_order_line[j].product.id] -
                wk_order_line[j].quantity;
          }
        } else {
          var wk_order_line = order.get_orderlines();
          for (var j = 0; j < wk_order_line.length; j++) {
            self.wk_product_qtys[wk_order_line[j].product.id] =
              self.wk_product_qtys[wk_order_line[j].product.id] +
              wk_order_line[j].quantity;
          }
        }
      }
      return super.push_single_order(...arguments);
    }
    push_orders(order, opts) {
      var self = this;
      if (order) {
        if (!order.is_return_order) {
          var wk_order_line = order.get_orderlines();
          for (var j = 0; j < wk_order_line.length; j++) {
            if (!wk_order_line[j].stock_location_id)
              self.wk_product_qtys[wk_order_line[j].product.id] =
                self.wk_product_qtys[wk_order_line[j].product.id] -
                wk_order_line[j].quantity;
          }
        } else {
          var wk_order_line = order.get_orderlines();
          for (var j = 0; j < wk_order_line.length; j++) {
            self.wk_product_qtys[wk_order_line[j].product.id] =
              self.wk_product_qtys[wk_order_line[j].product.id] +
              wk_order_line[j].quantity;
          }
        }
      }
      return super.push_orders(...arguments);
    }
    set_stock_qtys(result) {
      var self = this;
      var all = $(".product");
      $.each(all, function (index, value) {
        var product_id = $(value).data("product-id");
        var stock_qty = result[product_id];
        $(value).find(".qty-tag").html(stock_qty);
      });
    }
    get_information(wk_product_id) {
      this.wk_change_qty_css();
      if (this.env.pos.wk_product_qtys)
        return this.env.pos.wk_product_qtys[wk_product_id];
    }
    wk_change_qty_css() {
      var self = this;
      var wk_order = self.orders;
      var wk_p_qty = new Array();
      var wk_product_obj = self.wk_product_qtys;
      if (wk_order) {
        for (var i in wk_product_obj)
          wk_p_qty[i] = self.wk_product_qtys[i];
        for (var i = 0; i < wk_order.length; i++) {
          if (!wk_order[i].is_return_order) {
            var wk_order_line = wk_order[i].get_orderlines();
            for (var j = 0; j < wk_order_line.length; j++) {
              if (!wk_order_line[j].stock_location_id)
                wk_p_qty[wk_order_line[j].product.id] = wk_p_qty[wk_order_line[j].product.id] - wk_order_line[j].quantity;
              var qty = wk_p_qty[wk_order_line[j].product.id];
              if (qty) {
                console.log($("#qty-tag" + wk_order_line[j].product.id).html(qty))
                $("#qty-tag" + wk_order_line[j].product.id).html(qty);
              }
              else {
                $("#qty-tag" + wk_order_line[j].product.id).html("0");
              }
            }

          }
        }
      }
    }
  }
  Registries.Model.extend(PosGlobalState, PosStock);

  const PosStockOrder = (Order) => class PosStockOrder extends Order {
    add_product(product, options) {
      var self = this;
      options = options || {};
      // warehouse management compatiblity code start---------------
      for (var i = 0; i < this.orderlines; i++) {
        if ((self.orderlines[i].product.id == product.id) && self.orderlines[i].stock_location_id) {
          options.merge = false;
        }
      }
      // warehouse management compatiblity code end---------------
      if (
        !self.pos.config.wk_continous_sale && self.pos.config.wk_display_stock &&
        !self.pos.get_order().is_return_order
      ) {
        var qty_count = 0;
        if (parseInt($("#qty-tag" + product.id).html()))
          qty_count = parseInt($("#qty-tag" + product.id).html());
        else {
          var wk_order = self.pos.orders;
          var wk_p_qty = new Array();
          var qty;
          var wk_product_obj = self.pos.wk_product_qtys;
          if (wk_order) {
            for (var i in wk_product_obj)
              wk_p_qty[i] = self.pos.wk_product_qtys[i];
            _.each(wk_order.models, function (order) {
              var orderline = order.orderlines.models;
              if (orderline.length > 0)
                _.each(orderline, function (line) {
                  if (!line.stock_location_id && product.id == line.product.id)
                    wk_p_qty[line.product.id] =
                      wk_p_qty[line.product.id] - line.quantity;
                });
            });
            qty = wk_p_qty[product.id];
          }
          qty_count = qty;
        }
        if(options.quantity && options.quantity<=0){
          super.add_product(...arguments);
        }
        else{
          if (qty_count <= self.pos.config.wk_deny_val)
            Gui.showPopup("OutOfStockMessagePopup", {
              title: _t("Warning !!!!"),
              body: _t(
                "(" + product.display_name + ")" +
                self.pos.config.wk_error_msg + "."
              ),
              product_id: product.id,
            });
          else super.add_product(...arguments)
        }
      } else super.add_product(...arguments)
      if (self.pos.config.wk_display_stock && !self.is_return_order)
        self.pos.wk_change_qty_css();
    }
  }
  Registries.Model.extend(Order, PosStockOrder);

  const PosStockOrderline = (Orderline) => class PosStockOrderline extends Orderline {
    constructor(obj, options) {
      super(...arguments);
      this.wk_line_stock_qty = 0.0;
      if (options.product)
        this.wk_line_stock_qty = parseInt(
          $("#qty-tag" + options.product.id).html()
        );
    }
    set_quantity(quantity, keep_price) {
      var self = this;
      // -------code for POS Warehouse Management----------------
      if (self.stock_location_id && quantity && quantity != "remove") {
        if (
          self.pos.get_order() &&
          self.pos.get_order().selected_orderline &&
          self.pos.get_order().selected_orderline.cid == self.cid
        ) {
          Gui.showPopup("OutOfStockMessagePopup", {
            title: _t("Warning !!!!"),
            body: _t(
              "Selected orderline product have different stock location, you can't update the qty of this orderline"
            ),
            product_id: self.product.id,
          });
          $(".numpad-backspace").trigger("update_buffer");
          return;
        } else {
          return super.set_quantity(...arguments);
        }
      }
      // -------code for POS Warehouse Management----------------
      if (
        !self.pos.config.wk_continous_sale &&
        self.pos.config.wk_display_stock &&
        isNaN(quantity) != true &&
        quantity != "" &&
        parseFloat(self.wk_line_stock_qty) - parseFloat(quantity) <
        self.pos.config.wk_deny_val &&
        self.wk_line_stock_qty != 0.0
      ) {
        Gui.showPopup("OutOfStockMessagePopup", {
          title: _t("Warning !!!!"),
          body: _t("(" + this.product.display_name + ")" + self.pos.config.wk_error_msg + "."),
          product_id: this.product.id,
        });
        $(".numpad-backspace").trigger("update_buffer");
        if (self.pos.config.wk_display_stock) self.pos.wk_change_qty_css();
      } else {
        var wk_avail_pro = 0;
        if (self.pos.selectedOrder) {
          var wk_pro_order_line = self.pos.selectedOrder.get_selected_orderline();
          if (!self.pos.config.wk_continous_sale && self.pos.config.wk_display_stock && wk_pro_order_line) {
            var wk_current_qty = parseInt($("#qty-tag" + wk_pro_order_line.product.id).html());
            if (quantity == "" || quantity == "remove")
              wk_avail_pro = wk_current_qty + wk_pro_order_line;
            else wk_avail_pro = wk_current_qty + wk_pro_order_line - quantity;
            if (self.pos.config.wk_display_stock) self.pos.wk_change_qty_css();
            if (wk_avail_pro < self.pos.config.wk_deny_val && !(quantity == "" || quantity == "remove")) {
              Gui.showPopup("OutOfStockMessagePopup", {
                title: _t("Warning !!!!"),
                body: _t("(" + wk_pro_order_line.product.display_name + ")" + self.pos.config.wk_error_msg + "."),
                product_id: wk_pro_order_line.product.id,
              });
            } else {
              var result = super.set_quantity(...arguments);
              if (self.pos.config.wk_display_stock) self.pos.wk_change_qty_css();
              return result
            }
          } else {
            var result = super.set_quantity(...arguments);
            if (self.pos.config.wk_display_stock) self.pos.wk_change_qty_css();
            return result
          }
        } else {
          var result = super.set_quantity(...arguments);
          if (self.pos.config.wk_display_stock) self.pos.wk_change_qty_css();
          return result
        }
      }
    }
  }
  Registries.Model.extend(Orderline, PosStockOrderline);
});
