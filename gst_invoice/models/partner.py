# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

from odoo import api, fields, models, _


class Partner(models.Model):
    _inherit = "res.partner"

    @api.depends('vat')
    def _compute_partner_type(self):
        if self.country_id.code == 'IN':
            if self.vat:
                self.partner_type = 'B2B'
            else:
                self.partner_type = 'B2BUR'
        else:
            self.partner_type = 'IMPORT'

    partner_type = fields.Selection([('B2B', 'B2B'), ('B2BUR', 'B2BUR'), ('IMPORT', 'IMPS/IMPG')],
                                    string='Partner Type', copy=False,
                                    compute='_compute_partner_type',
                                    help="""
                                        * B2B : B2B Supplies.
                                        * B2BUR : Inward supplies from unregistered Supplier.
                                        * IMPORT : Import of Services/Goods.
                                    """)
