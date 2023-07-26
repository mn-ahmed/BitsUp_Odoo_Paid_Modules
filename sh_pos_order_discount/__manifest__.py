# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Point Of Sale Order Discount",
    "author": "BitsUp Technologies",
    "website": "https://www.bitsuptech.com",
    "support": "support@bitsuptech.com",
    "category": "Point Of Sale, Paid Modules",
    "license": "OPL-1",
    "summary": "POS Product Discount Point Of Sale Discount Point Of Sale Order Line Discount POS Custom Discount Point Of Sale Global Discount Point Of Sale Line Discount POS Line Discount POS Global Discount POS Order Discount POS Order Line Discount Odoo",
    "description": """Currently, in odoo point of sale, you can apply discount individually on every order line only. The "Point Of Sale Order Discount" module allows you to give discounts globally. This module applies the discounts on the point of sale order line as well as on the whole order. You can apply multiple discounts per order & order line. The discount can be applied in a fixed amount or percentage amount. Applied discount print on the receipt.""",
    "version": "16.0.3",
    "depends": ["point_of_sale"],
    "application": True,
    "data": [
        'views/pos_config_views.xml', 
        'views/res_config_settings_views.xml'
    ],
    'assets': {
        'point_of_sale.assets': [
            'sh_pos_order_discount/static/src/scss/pos.scss',
            'sh_pos_order_discount/static/src/js/**/*.js',
            'sh_pos_order_discount/static/src/xml/**/*.xml',
        ],
    },
    "auto_install": False,
    "installable": True,
    'images': ['static/description/background.png', ],
    "price": 20,
    "currency": "EUR",
}
