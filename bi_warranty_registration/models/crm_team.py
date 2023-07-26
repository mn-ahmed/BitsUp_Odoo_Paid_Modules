# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class WarrantyTeam(models.Model):
    _inherit = 'crm.team'

    use_warranty = fields.Boolean("Warranty")
