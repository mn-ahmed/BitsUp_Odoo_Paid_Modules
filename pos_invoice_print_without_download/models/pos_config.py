# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   License URL : <https://store.webkul.com/license.html/>
# 
#################################################################################
from odoo import fields, models, api
import logging
import base64
_logger = logging.getLogger(__name__)

class PosConfig(models.Model):
    _inherit = 'pos.config'

    invoice_print = fields.Boolean(string="Print Invoice Without its Download", help="Enable this options to Print Invoice Without Download .", default=True)
    
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    pos_invoice_print = fields.Boolean(related='pos_config_id.invoice_print',readonly=False)

class PosOrder(models.Model):
    _inherit = "pos.order" 

    def action_invoice_pdf(self,invoice_id):
        pdf =  self.env['ir.actions.report']._render_qweb_pdf("account.account_invoices",[invoice_id])[0]
        base = base64.b64encode(pdf)
        return base
        