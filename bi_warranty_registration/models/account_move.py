# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class WarrantyInvoice(models.Model):
    _inherit = 'account.move'

    warranty_invoice = fields.Boolean('Warranty Renew Invoice')
    warranty_reg_id = fields.Many2one('product.warranty', 'Warranty')

    def action_post(self):
        if self.warranty_reg_id:
            self.warranty_reg_id.update({'state': 'in_progress'})
        if self.payment_id:
            self.payment_id.action_post()
        else:
            self._post(soft=False)
        return False
