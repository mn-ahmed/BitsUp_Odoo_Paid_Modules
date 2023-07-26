# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"

    gst_status = fields.Selection([
                                ('not_uploaded', 'Not Uploaded'),
                                ('ready_to_upload', 'Ready to upload'),
                                ('uploaded', 'Uploaded to govt'),
                                ('filed', 'Filed')
                            ],
                            string='GST Status',
                            default="not_uploaded",
                            copy=False,
                            help="status will be consider during gst import, "
            )
    invoice_type = fields.Selection([
                                ('b2b', 'B2B'),
                                ('b2cl', 'B2CL'),
                                ('b2cs', 'B2CS'),
                                ('b2bur', 'B2BUR'),
                                ('import', 'IMPS/IMPG'),
                                ('export', 'Export'),
                                ('cdnr', 'CDNR'),
                                ('cdnur', 'CDNUR'),
                            ],
                            copy=False,
                            string='Invoice Type'
            )
    export_type = fields.Selection([
                                ('regular', 'Regular'),
                                ('sez_with_payment', 'SEZ supplies with payment'),
                                ('sez_without_payment', 'SEZ supplies without payment'),
                                ('deemed', 'Deemed Exp'),
                                ('intra_state_igst', 'Intra-State supplies attracting IGST'),
                            ],
                            string='Export Type',
                            default='regular',
                            required=True
            )
    export = fields.Selection([
                                ('WPAY', 'WPay'),
                                ('WOPAY', 'WoPay')
                            ],
                            string='Export'
            )
    bonded_wh = fields.Selection([
                                ('Y', 'Yes'),
                                ('N', 'No')
                            ],
                            string='Sale from Bonded WH',
                            default='N',
                            help='When goods will be kept in bonded warehouses and later cleared from there',
            )
    itc_eligibility = fields.Selection([
                                ('Inputs', 'Inputs'),
                                ('Capital goods', 'Capital goods'),
                                ('Input services', 'Input services'),
                                ('Ineligible', 'Ineligible'),
                            ],
                            string='ITC Eligibility',
                            default='Ineligible'
            )
    reverse_charge = fields.Boolean(
                        string='Reverse Charge',
                        help="Allow reverse charges for b2b invoices")
    pre_gst = fields.Boolean(
                        string='Pre GST',
                        help="Allow pre gst for cdnr invoices")
    inr_total = fields.Float(string='INR Total')
