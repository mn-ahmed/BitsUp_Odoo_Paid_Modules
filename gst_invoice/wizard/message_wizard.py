# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

from odoo import api, fields, models


class MessageWizard(models.TransientModel):
    _name = "message.wizard"
    _description = "Message wizard"

    text = fields.Text(string='Message', readonly=True, translate=True)
