# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "Point of Sale Commission by Order/Invoice/Payment in Odoo",
    "version" : "16.0.0.4",
    "category" : "Point of Sale, Paid Modules",
    "summary" : "App Point of Sales Commission based on Partner Product pos Margin calculated pos commission pos agent commission POS Sales Commission pos commission pos user commission pos order commission pos Cashier Commission for pos payment commission pos commission",
    "description": """
    this module calculates sales commission on based on Product category, Product, Margin
	point of sales commission on sales
	pos commission invoice
	pos commission on order
	pos commission
    pos commission 
    commission on pos
    commission for pos user 
    pos agent commission
    pos user commission
    pos sales person commission
    
    odoo Sale Commission for Users Sale Commission for Partner Sale Commission for Internal Users
odoo Sale Commission for External Partner Sale Commission for Customer Sale Commission for External Partner
odoo Sale Commission on Invoice Sale Commission on Sale order Sale Commission on Register Payment
odoo Sale Commission on Invoice Payment Sale Commission on Payment Sale Commission based on Product
odoo Sale Commission based on Product Category Sale Commission based on Margin Sale Commission based on Partner
odoo Sale Commission Based Invoice Sale Commission Based Sale Commission Based Register Payment
odoo Sale Commission Based Invoice Payment Sale Commission based Payment sale Agent Commission on Invoice
odoo Agent Commission on Sale order Agent Commission on Register Payment sale Agent Commission on Invoice Payment
odoo Agent Commission on Payment Agent sale Commission based Invoice Agent Commission based Sale Agent Commission based Register Payment
odoo Agent Commission based Invoice Payment Agent Commission based Payment sale commision on invoice Sale commision on Sale order
odoo Sale commision on Register Payment Sale commision on Invoice Payment Sale commision on Payment
odoo Sale commision based on Product Sale commision based on Product Category Sale commision based on Margin
odoo Sale commision based on Partner Sale commision Based Invoice Sale commision Based Sale commision Based Register Payment
odoo Sale commision Based Invoice Payment Sale commision based Payment Agent commision on Invoice
odoo Agent commision on Sale Agent commision on Register Payment Agent commision on Invoice Payment sale Agent commision on Payment
odoo sale Agent commision based Invoice sale Agent commision based Sales Agent commision based Register Payment Agent commision based Invoice Payment

odoo Sale Order Commission for Users Sale Order Commission for Partner Sale Order Commission for Internal Users
odoo Sale Order Commission for External Partner Sale Order Commission for Customer Sale Order Commission for External Partner
odoo Sale Order Commission on Invoice Commission on Sale order Commission on Register Payment commission
odoo Sale Order Commission on Payment Sale Order Commission on invoice Sale Order Commission based on Product
odoo Sale Order Commission based on Product Category Sale Order Commission based on Margin Sale Order Commission based on Partner
odoo Sale Order Commission Based Invoice Sale Order Commission Based invoice Commission Based Register Payment
odoo Sale Order Commission Based Invoice Payment sale order Commission based Payment sale Order Agent Commission on Invoice
odoo Agent Commission on Sale order Agent Commission on Register Payment sale invoice Commission on Payment
odoo Agent Commission on Payment Agent sale Order Commission based Invoice Agent Commission based Sale Order Agent Commission based Register Payment
odoo Agent Commission based Invoice Agent Commission based Payment sale Order commision on invoice Sale Order commision on Sale order
odoo Sale Order commision on Register Payment Sale commision on Invoice Payment Sale commision on Payment
odoo Sale Order commision based on Product Sale Order commision based on Product Category Sale commision based on Margin
odoo Sale Order commision based on Partner Sale Order comission Based Invoice Sale comision Based Sale Order commision Based Register Payment
odoo Sale Order commision Based Invoice Payment Sale Order commision based Payment Agent commision on Invoice
odoo Agent commision on Sale Order Agent commision on Register Payment Agent Order commision on Invoice Payment sale Order Agent commision on Payment
odoo sale Order Agent commision based Invoice sale Order Agent commision based Sales Order Agent commision based Register Payment Agent commision based Invoice Payment
odoo SO commission SO partner commission SO agent commission SO commission based on product SO Commission based on margin
    Point of Sale Commission on Invoice
    Point of Sale Commission on orders
    Point of Sale Commission on Register Payment
    Point of Sale Commission on Invoice Payment
    Point of Sale Commission on Payment
    Point of Sale Commission based on Product
    Point of Sale Commission based on Product Category
    Point of Sale Commission based on Margin
    Point of Sale Commission based on Partner
    Point of Sale Commission Based Invoice
    Point of Sale Commission Based Sales
    Point of Sale Commission Based Register Payment
    Point of Sale Commission Based Invoice Payment
    Point of Sale Commission based Payment
    Point of Sale Agent Commission on Invoice
    Point of Sale Agent Commission on Sales
    Point of Sale Cashier Commission on Register Payment
    Point of Sale Agent Commission on Invoice Payment
    Point of Sale Agent Commission on Payment
    POS Agent Commission based Invoice
    POS Agent Commission based Sales
    POS Agent Commission based Register Payment
    POS Agent Commission based Invoice Payment
    POS Agent Commission based Payment
    POS Commission on invoice
    POS Commission on Sales
    POS Commission on Register Payment
    POS Commission on Invoice Payment
    POS Commission on Payment
    POS commision based on Product
    POS Commission based on Product Category
    POS Commission based on Margin
    POS Commission based on Partner
    POS commision based Payment, sales commision,sale commision, commision sales,Commission on sales order, Commission on pos, Commission on point of sale, Commission pos, Commission sales
   odoo calculates sales commission on invoice Sales Commission based on Product category Product Margin
    odoo Sales Commission for Users Sales Commission for Partner Sales Commission for Internal Users
    odoo Sales Commission for External Partner Sales Commission for Customer Sales Commission for External Partner
    odoo Sales Commission on Invoice Sales Commission on Sales order Sales Commission on Register Payment
    odoo Sales Commission on Invoice Payment Sales Commission on Payment Sales Commission based on Product
    odoo Sales Commission based on Product Category Sales Commission based on Margin Sales Commission based on Partner
    odoo Sales Commission Based Invoice Sales Commission Based Sales Sales Commission Based Register Payment
    odoo Sales Commission Based Invoice Payment Sales Commission based Payment Agent Commission on Invoice
    odoo Agent Commission on Sales order Agent Commission on Register Payment Agent Commission on Invoice Payment
    odoo Agent Commission on Payment Agent Commission based Invoice Agent Commission based Sales Agent Commission based Register Payment
    odoo Agent Commission based Invoice Payment Agent Commission based Payment sales commision on invoice Sales commision on Sales order
    odoo Sales commision on Register Payment Sales commision on Invoice Payment Sales commision on Payment
    odoo Sales commision based on Product Sales commision based on Product Category Sales commision based on Margin
    odoo Sales commision based on Partner Sales commision Based Invoice Sales commision Based Sales Sales commision Based Register Payment
    odoo Sales commision Based Invoice Payment Sales commision based Payment Agent commision on Invoice
    odoo Agent commision on Sales Agent commision on Register Payment Agent commision on Invoice Payment Agent commision on Payment
    odoo Agent commision based Invoice Agent commision based Sales Agent commision based Register Payment Agent commision based Invoice Payment
    odoo sales Agent commision based Payment
    """,
    "author" : "BitsUp Technologies",
    "website" : "https://www.bitsuptech.com",
    "price": 39,
    "currency": 'EUR',
    "depends" : ['base','account','point_of_sale'],
    "data" :[
            'security/pos_commission_security.xml',
            'security/ir.model.access.csv',
            'report/pos_inv_comm_template.xml',
            'report/commission_report.xml',
            'views/pos_view.xml'
            ],
    "auto_install": False,
    "installable": True,
    "images":['static/description/Banner.gif'],
    'license': 'OPL-1'
}

