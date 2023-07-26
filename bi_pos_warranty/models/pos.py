# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class POSConfig(models.Model):

	_inherit ="pos.config"

	create_warranty = fields.Boolean('Create Warranty from POS')	



class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    create_warranty = fields.Boolean(related='pos_config_id.create_warranty', readonly=False)

class Warranty(models.Model):
	_inherit = 'product.warranty'

	pos_id = fields.Many2one('pos.order',"POS Order")


class PosOrderInherit(models.Model):

	_inherit ="pos.order"

	def check_warranty_reg(self):
		used_lots = [] 
		all_lots = []
		warranty = self.env['product.warranty'].sudo().search([])
		all_lts = self.env['stock.lot'].search([])
		for wrnty in warranty :
			if wrnty and wrnty.product_serial_id :
				used_lots.append(wrnty.product_serial_id.name)
	
		for lts in all_lts :
			all_lots.append(lts.name)

		return [used_lots,all_lots]

	@api.depends('lines')
	def _compute_warranty_pos(self):
		for res in self:
			count = 0
			warranty = self.env['product.warranty'].search_count([('pos_id','=',res.id)])
			res.pos_warranty = warranty

	pos_warranty = fields.Integer(string="warranty",compute="_compute_warranty_pos")

	@api.model
	def _process_order(self, order, draft, existing_order):
		res = super(PosOrderInherit, self)._process_order(order,draft,existing_order)
		orders = self.env['pos.order'].browse(res)
		for odr in orders :
			if odr.config_id.create_warranty :
				for line in odr.lines :
					if  line.product_id.under_warranty == True:
						for pack_lot in line.pack_lot_ids :
							lot = self.env['stock.lot'].search([('name','=',pack_lot.lot_name), ('product_id', '=', line.product_id.id)])
							if lot :
								val = {
									'partner_id' : odr.partner_id.id if odr.partner_id.id else odr.user_id.partner_id.id,
									'product_id' : line.product_id.id,
									'phone' : odr.partner_id.phone,
									'email' : odr.partner_id.email,
									'product_serial_id' : lot.id,
									'pos_id' : odr.id,
								}
								warranty = self.env['product.warranty'].create(val)
		return res

	def button_warranty(self):
		return{
			'name': _('warranty'),
			'view_mode': 'tree,form',
			'res_model': 'product.warranty',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'domain': [('pos_id', '=',self.id )],
		}