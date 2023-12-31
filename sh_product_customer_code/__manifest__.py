# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
{
    "name": "Product Customer Code",
    "author": "BitsUp Technologies",
    "license": "OPL-1",
    "website": "https://www.bitsuptech.com",
    "support": "support@bitsuptech.com",
    "category": "Inventory, Paid Modules",
    "summary": "Sale Product Code,Manage Partner Product Code,SO Client Product Code,Quotation Product Code, Customer Product Code,Sale Order Product Code,Customers Product Code,Products Code,Product Codes,Product Variant Code,Client Code,Sales Code Odoo",
    "description": """Our module is useful to manage specific product codes for customers. You can show the customer product code in the sale order line and quotation order line. After the selection of the product, the product code field fills by default. You can find products/product variants using product codes.""",
    "version": "16.0.4",
    'depends': ['sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'security/customer_product_code_security.xml',

        'views/sale_res_config_settings_views.xml',
        'views/sh_product_customer_code.xml',
        'views/sh_product_customer_code_menu.xml',
        'views/sale_order_views.xml',
        'views/account_views.xml',

        'report/sale_order_report_views.xml',
        'report/account_report_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sh_product_customer_code/static/src/scss/custom.scss',
        ],
    },

    'images': ['static/description/background.png', ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "price": 15,
    "currency": "EUR"
}
