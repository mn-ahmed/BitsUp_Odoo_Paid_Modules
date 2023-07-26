# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
  "name"                 :  "GST - Returns and Invoices",
  "summary"              :  """Odoo GST - Returns and Invoices helps to file the monthly return that summarizes all outward supplies by registered taxpayers""",
  "category"             :  "Accounting, Paid Modules",
  "version"              :  "3.0.0",
  "sequence"             :  1,
  "author"               :  "BitsUp Technologies",
  "license"              :  "Other proprietary",
  "website"              :  "https://www.bitsuptech.com",
  "description"          :  """GST - Returns and Invoices
GST
One Nation One Tax
Tax
Odoo Tax
Odoo GST
Returns and Invoices
Goods and Services Tax
Tax module
Tax App
GST module
Goods and Services Tax in Odoo""",
  "live_test_url"        :  "https://odoodemo.webkul.com/demo_feedback?module=gst_invoice",
  "depends"              :  [
                             'l10n_in',
                             'account_tax_python',
                            ],
  "data"                 :  [
                             'data/data_unit_quantity_code.xml',
                             'data/data_uom_mapping.xml',
                             'data/data_dashboard.xml',
                             'security/gst_security.xml',
                             'security/ir.model.access.csv',
                             'wizard/message_wizard_view.xml',
                             'wizard/invoice_type_wizard_view.xml',
                             'data/gob_server_actions.xml',
                             'views/account_move_view.xml',
                             'views/gst_view.xml',
                             'views/gstr2_view.xml',
                             'views/res_partner_views.xml',
                             'views/gst_dashboard_view.xml',
                             'views/account_fiscalyear_view.xml',
                             'views/ir_attachment_view.xml',
                             'views/account_period_view.xml',
                             'views/gst_sequence.xml',
                             'views/unit_quantity_code_view.xml',
                             'views/uom_map_view.xml',
                             'views/gst_action_view.xml',
                             'views/gst_menu_view.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  99,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
  "assets"               :  {
    'web.assets_backend' :  [
                             'gst_invoice/static/src/scss/gst_dashboard.scss',
                            #  'gst_invoice/static/src/js/gst_dashboard.js',
                            ],
                            },
}
