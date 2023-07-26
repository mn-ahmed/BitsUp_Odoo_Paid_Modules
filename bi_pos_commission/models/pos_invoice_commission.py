# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools
from docutils.nodes import field
import datetime

'''New class to handle sales commission in invoice.'''
class InvoiceSaleCommission(models.Model):
	_name = 'pos.invoice.commission'
	_description = 'POS Invoice Commission'

	name = fields.Char(string="Description", size=512)
	type_name = fields.Char(string="Commission Name")
	comm_type = fields.Selection([
		('standard', 'Standard'),
		('partner', 'Partner Based'),
		('mix', 'Product/Category/Margin Based'),
		('discount', 'Discount Based'),
		], 'Commission Type', copy=False, help="Select the type of commission you want to apply.")
	user_id = fields.Many2one('res.users', string='Sales Person',
								 help="sales person associated with this type of commission",
								 required=True)
	pos_order_id = fields.Many2one('pos.order', string='POS Order Reference', help="Affected POS Order")
	commission_amount = fields.Float(string="Commission Amount")
	invoice_id = fields.Many2one('account.move', string='Invoice Reference',
								 help="Affected Invoice")
	commission_id = fields.Many2one('pos.commission', string='Sale Commission',
								 help="Related Commission",)
	product_id = fields.Many2one('product.product', string='Product',
								 help="product",)
	partner_id = fields.Many2one('res.partner', string='Partner')
	partner_type = fields.Selection([('Affiliated Partner', 'Affiliated Partner'),
									  ('Non-Affiliated Partner', 'Non-Affiliated Partner')], string='Partner Type')
	categ_id = fields.Many2one('product.category', string='Product Category')
	sub_categ_id = fields.Many2one('product.category', string='Product Sub-Category')
	date = fields.Date('Date')
	invoiced = fields.Boolean(string='Invoiced', readonly=True, default=False)


class WizardInvoiceSaleCommission(models.Model):
	_name = 'wizard.pos.invoice.commission'
	_description = 'Wizard POS Invoice Commission'

	start_date = fields.Date('Start Date', required=True)
	end_date = fields.Date('End Date', required=True)
	salesperson = fields.Many2one('res.users','Sales Person', required=True)
	
	def print_commission_report(self):
		temp = []
		sale_invoice_commission_ids = self.env['pos.invoice.commission'].search([('date','>=',self.start_date),('date','<=',self.end_date),('user_id','=',self.salesperson.id)])
		if not sale_invoice_commission_ids:
			raise Warning('There Is No Any Commissions.')
		else:
			for a in sale_invoice_commission_ids:
				temp.append(a.id)
		data = temp
		datas = {
			'ids': self._ids,
			'model': 'pos.invoice.commission',
			'form': data,
			'start_date':self.start_date,
			'end_date':self.end_date,
			'user':self.salesperson.name
		}
		return self.env.ref('bi_pos_commission.report_pdf').report_action(self,data=datas)
