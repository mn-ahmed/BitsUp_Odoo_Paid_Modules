{
    'name': "Inter Warehouse Transfer",
    'version': '16.0.0',
    'author': 'BitsUp Technologies',
    'summary': """Internal transfer of goods from one warehouse to another warehouse""",
    'description':""" 
                    Internal transfer of goods from one warehouse to another warehouse
                    internal warehouse
                    Internal location
                    Inter transfer
                    Inter location
                    Inter warehouse
                """,
    "category": "Inventory, Paid Modules",
    'depends': ['stock'],
    'data': [
        'data/stock_data.xml',
        'security/ir.model.access.csv',
        'views/stock_transfer_view.xml',
    ],
   'application': False,
    'installable': True,
    'price': 35,
    'currency': 'EUR',
    "images":['static/description/banner.jpg'],
    'license': 'OPL-1',
}
