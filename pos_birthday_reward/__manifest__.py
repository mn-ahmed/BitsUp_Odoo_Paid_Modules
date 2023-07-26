# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

{
    "name": "Pos Birthday Discount",
    "version": "16.0.1.0",
    "summary": "This module allows offering extra discount to the customer in their birthday month once. | Birthday Month Discount | Birthday Discount | Birthday Rewards | Rewareds | Discount",
    "description": """
    get promotion on birthday month
    ================================
    """,
    "license": "OPL-1",
    "author": "BitsUp Technologies",
    "website": "https://www.bitsuptech.com",
    "category": "Point Of Sale, Paid Modules",
    "depends": ["point_of_sale"],
    "data": [
        "views/birthday_reward.xml",
    ],
    "assets": {
        "point_of_sale.assets": [
            "pos_birthday_reward/static/src/js/PosBirthdayReward.js",
            "pos_birthday_reward/static/src/js/Screens/ClientListScreen/PartnerListScreen.js",
            "pos_birthday_reward/static/src/xml/Screens/ProductScreen/ActionpadWidget.xml",
            "pos_birthday_reward/static/src/xml/Screens/ProductScreen/Orderline.xml",
            "pos_birthday_reward/static/src/xml/Screens/ReceiptScreen/OrderReceipt.xml",
        ],
    },
    "images": ["static/description/banner.jpg"],
    "sequence": 1,
    "installable": True,
    "price": 40,
    "currency": "EUR",
}
