# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class WarrantyHistory(models.Model):
    _name = "warranty.history"
    _description = "Warranty History"

    date_renewal = fields.Date('Date')
    warranty_renewal_date = fields.Date('Warranty Start Date')
    warranty_renew_end_date = fields.Date('Warranty End Date')
    renewal_cost = fields.Float('Renewal Amount')
    paid = fields.Boolean('Paid')
    free = fields.Boolean('Free')
    warranty_id = fields.Many2one('product.warranty', 'Warranty')
