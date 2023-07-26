# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings_Inherit(models.TransientModel):
	_inherit = 'res.config.settings'

	commission_configuration = fields.Boolean('Apply POS Commission', related="company_id.commission_configuration",readonly=False)
	commission_discount_account = fields.Many2one('account.account',domain=[('account_type', '=', 'expense')],
												  string="Commission Account"
												  ,related="company_id.commission_discount_account",readonly=False)

class Res_company_inherit(models.Model):
	_inherit = 'res.company'

	commission_configuration = fields.Boolean('Apply POS Commission')
	commission_discount_account = fields.Many2one('account.account',domain=[('account_type', '=', 'expense')],
												  string="Commission Account")