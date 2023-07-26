# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class WarrantySettings(models.Model):
	_name = 'warranty.settings'
	_inherit = 'res.config.settings'
	_rec_name = 'setting_desc'
	_description = "Warranty Settings"

	@api.model 
	def default_get(self, flds): 
		result = super(WarrantySettings, self).default_get(flds)
		warranty_notif = self.env['ir.model.data']._xmlid_to_res_id('bi_warranty_registration.email_template_warranty_registration') 
		renew_notif = self.env['ir.model.data']._xmlid_to_res_id('bi_warranty_registration.email_template_warranty_renew')
		create_warranty_from_saleorder = self.env['ir.config_parameter'].sudo().get_param('bi_warranty_registration.create_warranty_from_saleorder')
		renew_notif_interval = self.env['ir.config_parameter'].sudo().get_param('bi_warranty_registration.renew_notif')

		result['warranty_tmpl'] = warranty_notif
		result['renew_tmpl'] = renew_notif
		result['create_warranty_from_saleorder'] = create_warranty_from_saleorder
		result['renew_notif'] = renew_notif_interval
		return result
	
	renew_notif = fields.Char("Renew Notification Submit Interval")
	setting_desc = fields.Char('Description')
	warranty_tmpl = fields.Many2one('mail.template', 'Warranty Registration mail template')
	renew_tmpl = fields.Many2one('mail.template', 'Warranty Renew mail template')
	company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
	create_warranty_from_saleorder = fields.Boolean('Create Warranty from Sale Order')


	def set_values(self):
		super(WarrantySettings,self).set_values()
		self.env['ir.config_parameter'].sudo().set_param('bi_warranty_registration.renew_notif', self.renew_notif)
		self.env['ir.config_parameter'].sudo().set_param('bi_warranty_registration.create_warranty_from_saleorder', self.create_warranty_from_saleorder)
		module = False
		if self.create_warranty_from_saleorder == True :
			module = self.env['ir.module.module'].search([('state', '!=', 'installed'),('name', '=', 'v9_sale_invoice_serial')])
		if module :
			module.button_immediate_install()
