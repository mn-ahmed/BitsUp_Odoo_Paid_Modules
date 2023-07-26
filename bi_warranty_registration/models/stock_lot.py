# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductionLot(models.Model):
    _inherit = 'stock.lot'

    company_id = fields.Many2one('res.company', string='Company', required=True, store=True, index=True,
                                 default=lambda self: self.env.company)
    start_date_warranty = fields.Date('Warranty Start Date')
    end_date_warranty = fields.Date('Warranty End Date')
    renewal_times = fields.Integer('No. of Renew')
