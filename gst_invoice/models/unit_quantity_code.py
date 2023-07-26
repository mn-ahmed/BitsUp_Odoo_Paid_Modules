# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

from odoo import api, fields, models

class UnitQuantityCode(models.Model):
    _name = "unit.quantity.code"
    _description = "Unit Quantity Code"

    name = fields.Char(string="Unit", help="UQC (Unit of Measure) of goods sold")
    code = fields.Char(string="Code", help="Code for UQC (Unit of Measure)")
