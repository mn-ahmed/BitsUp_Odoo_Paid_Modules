# -*- coding: utf-8 -*-
from odoo import fields, models, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    transfer_id = fields.Many2one('stock.transfer')

    def action_done(self):
        res = super(StockPicking, self).action_done()
        for picking in self:
            if all([picking.state == 'done' for picking in picking.transfer_id.picking_ids]):
                picking.transfer_id.state = 'done'
        return res
