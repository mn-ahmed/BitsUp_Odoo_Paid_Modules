# -*- coding: utf-8 -*-
{
    'name': 'POS Salesperson(Employee)',
    'version': '1.0',
    'author': 'BitsUp Technologies',
    'category': 'Point of Sale, Paid Modules',
    'depends': ['point_of_sale', 'hr'],
    'summary': 'This apps helps you set salesperson on pos orderline from pos interface | POS Orderline User | Assign Sales Person on POS | POS Sales Person',
    'description': """
- Odoo POS Orderline user
- Odoo POS Orderline salesperson
- Odoo POS Salesperson
- Odoo POS Item Salesperson
- Odoo POS Item User
- Odoo POS product salesperson
    """,
    'data': [
        'views/pos_config_view.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pw_pos_salesperson_emp/static/src/js/**/*',
            'pw_pos_salesperson_emp/static/src/xml/**/*',
        ],
    },
    'price': 40.0,
    'currency': "EUR",
    'application': True,
    'installable': True,
    "license": "LGPL-3",
    "images":["static/description/Banner.png"],
}
