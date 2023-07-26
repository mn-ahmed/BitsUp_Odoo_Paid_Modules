# -*- coding: utf-8 -*-

{
    "name": "Odoo Indiamart Connector",
    "version": "16.0.0.1",
    "category": "CRM, Paid Modules",
    "summary": "Sync Leads from indiamart to odoo.",
    "description": """
        Sync Lead related data from indiamart to odoo.
    """,
    "author": "BitsUp Technologies",
    "website": "http://www.bitsuptech.com",
    "support": "support@bitsuptech.com",
    "depends": ["crm"],
    "data": [
        "data/cron.xml",
        "security/ir.model.access.csv",
        "views/indiamart.xml",
        "views/crm.xml",
    ],
    "images": ["images/screen_image.png"],
    "price": 30,
    "currency": "USD",
    "application": True,
    "installable": True,
    "auto_install": False,
    "license": "OPL-1",
}
