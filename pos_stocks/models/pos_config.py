# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
#
#################################################################################
from odoo import fields, models, api

class PosConfig(models.Model):
    _inherit = 'pos.config'

    wk_display_stock = fields.Boolean('Display stock in POS', default=True)
    wk_stock_type = fields.Selection([('available_qty', 'Available Quantity(On hand)'), ('forecasted_qty', 'Forecasted Quantity'), (
        'virtual_qty', 'Quantity on Hand - Outgoing Qty')], string='Stock Type', default='available_qty', required=True)
    wk_continous_sale = fields.Boolean('Allow Order When Out-of-Stock')
    wk_deny_val = fields.Integer(
        'Deny order when product stock is lower than ')
    wk_error_msg = fields.Char(
        string='Custom message', default="Product out of stock")
    wk_hide_out_of_stock = fields.Boolean(
        string="Hide Out of Stock products", default=True)

    @api.model
    def update_qty_real_time(self, result):
        active_sessions = self.env['pos.session'].search([('state', '!=', 'closed')])
        for session in active_sessions:
            order_ids = session.order_ids
            for order in order_ids:
                if not order.picking_ids:
                    for line in order.lines:
                        if(line.product_id.id in result.keys()):
                            result[line.product_id.id] -= line.qty
        return result
        
    @api.model
    def wk_pos_fetch_pos_stock(self, kwargs):
        result = {}
        location_id = False
        wk_stock_type = kwargs['wk_stock_type']
        wk_hide_out_of_stock = kwargs['wk_stock_type']
        config_id = self.browse([kwargs.get('config_id')])
        picking_type = config_id.picking_type_id
        location_id = picking_type.default_location_src_id.id
        product_obj = self.env['product.product']
        pos_products = product_obj.search(
            [('sale_ok', '=', True), ('available_in_pos', '=', True)])
        pos_products_qtys = pos_products.with_context(location=location_id)._compute_quantities_dict(self._context.get(
            'lot_id'), self._context.get('owner_id'), self._context.get('package_id'), self._context.get('from_date'), self._context.get('to_date'))
        for pos_product in pos_products_qtys:
            if wk_stock_type == 'available_qty':
                result[pos_product] = pos_products_qtys[
                    pos_product]['qty_available']
            elif wk_stock_type == 'forecasted_qty':
                result[pos_product] = pos_products_qtys[
                    pos_product]['virtual_available']
            else:
                result[pos_product] = pos_products_qtys[pos_product][
                    'qty_available'] - pos_products_qtys[pos_product]['outgoing_qty']
                
        result = self.update_qty_real_time(result)
            
        return result

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_wk_display_stock = fields.Boolean(related='pos_config_id.wk_display_stock', readonly=False)
    pos_wk_stock_type = fields.Selection(related='pos_config_id.wk_stock_type', readonly=False)
    pos_wk_continous_sale = fields.Boolean(related='pos_config_id.wk_continous_sale', readonly=False)
    pos_wk_deny_val = fields.Integer(related='pos_config_id.wk_deny_val', readonly=False)
    pos_wk_error_msg = fields.Char(related='pos_config_id.wk_error_msg', readonly=False)
    pos_wk_hide_out_of_stock = fields.Boolean(related='pos_config_id.wk_hide_out_of_stock', readonly=False)

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_product_product(self):
        result = super()._loader_params_product_product()
        result['search_params']['fields'].extend(['qty_available', 'virtual_available', 'outgoing_qty', 'type'])
        return result
