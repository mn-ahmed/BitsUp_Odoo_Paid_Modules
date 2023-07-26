# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    user_id = fields.Many2one('hr.employee', string='Salesperson')
