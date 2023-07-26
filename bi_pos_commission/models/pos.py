# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo import tools
import datetime
import psycopg2
from odoo.exceptions import UserError, ValidationError


class PosOrder(models.Model):
    _inherit = "pos.order"

    def refund(self):
        res = super(PosOrder, self).refund()
        for order in self:
            if order.commission_ids :
                invoiced = order.commission_ids.filtered(lambda line: line.invoiced)

                if not invoiced:
                    order.commission_ids.sudo().unlink()
                else:
                    raise ValidationError('You can not return this product. For this order Commission Amount is already paid to a salesperson.')
        return res

    commission_ids = fields.One2many('pos.invoice.commission', 'pos_order_id', string='POS Commissions')

    def get_exceptions(self, line, commission_brw):
        '''This method searches exception for any product line.
           @return : List of ids for all exception for particular product line.'''
        exception_obj = self.env['pos.commission.exception']
        categ_obj = self.env['product.category']
        product_exception_id = exception_obj.search([
                                        ('product_id', '=', line.product_id.id),
                                        ('commission_id', '=', commission_brw.id),
                                        ('based_on', '=', 'Products')
                                        ])
        if product_exception_id:
            return product_exception_id
        subcateg_exception_id = exception_obj.search([
                                       ('sub_categ_id', '=', line.product_id.categ_id.id),
                                       ('commission_id', '=', commission_brw.id),
                                       ('based_on', '=', 'Product Sub-Categories')])
        if subcateg_exception_id:
            return subcateg_exception_id
        exclusive_categ_exception_id = exception_obj.search([
                                       ('categ_id', '=', line.product_id.categ_id.id),
                                       ('commission_id', '=', commission_brw.id),
                                       ('based_on', '=', 'Product Categories'),
                                       ])
        if exclusive_categ_exception_id:
            return exclusive_categ_exception_id
        
        return []



    def get_mix_commission(self, commission_brw, order, user_id):
        '''This method calculates commission for Product/Category/Margin Based.
           @return : List of ids for commission records created.'''
        exception_obj = self.env['pos.commission.exception']
        invoice_commission_obj = self.env['pos.invoice.commission']
        invoice_commission_ids = []
        for line in order.lines:
            invoice_commission_data = {}
            exception_ids = []
            if not line.product_id:continue

            if line.price_subtotal > 0 :
                single_prod_price = (line.price_subtotal / line.qty)
                margin =  single_prod_price - line.product_id.standard_price

                actual_margin_percentage = (margin * 100)/single_prod_price

                exception_ids = self.get_exceptions(line, commission_brw)
                for exception in exception_ids:
                    product_id = False
                    categ_id = False
                    sub_categ_id = False
                    commission_amount = 0.0
                    commission_precentage = 0.0
                    name = ''
                    if exception.based_on_2 == 'Fix Price':
                        amount = line.price_subtotal
                    else:
                        amount = margin * line.qty
                    margin_percentage = exception.margin_percentage
                    if exception.based_on_2 == 'Margin' and actual_margin_percentage > margin_percentage:
                        commission_precentage = exception.above_margin_commission
                    elif exception.based_on_2 == 'Margin' and actual_margin_percentage <= margin_percentage:
                        commission_precentage = exception.below_margin_commission
                    elif exception.based_on_2 == 'Commission Exception':
                        commission_precentage = exception.commission_precentage
                    elif exception.based_on_2 == 'Fix Price' and line.price_unit >= exception.price :
                        commission_precentage = exception.price_percentage
                    elif exception.based_on_2 == 'Fix Price' and line.price_unit < exception.price :
                        pass
                        
                    if commission_precentage != 0.0:    
                        commission_amount = amount * (commission_precentage / 100)
                    
                    if exception.based_on == 'Products':
                        product_id = exception.product_id.id
                        name = 'Commission Exception for ' + tools.ustr(exception.based_on) + ' "' + tools.ustr(exception.product_id.name) + '" @' + tools.ustr(commission_precentage) + '%'
                    elif exception.based_on == 'Product Categories':
                        categ_id = exception.categ_id.id
                        name = 'Commission Exception for ' + tools.ustr(exception.based_on) + ' "' + tools.ustr(exception.categ_id.name) + '" @' + tools.ustr(commission_precentage) + '%'
                    elif exception.based_on == 'Product Sub-Categories':
                        sub_categ_id = exception.sub_categ_id.id
                        name = 'Commission Exception for ' + tools.ustr(exception.based_on) + ' "' + tools.ustr(exception.sub_categ_id.name) + '" @' + tools.ustr(commission_precentage) + '%'
                    invoice_commission_data = {'name': name,
                                                'product_id': product_id or False,
                                                'commission_id' : commission_brw.id,
                                                'categ_id': categ_id or False,
                                                'sub_categ_id': sub_categ_id or False,
                                                'user_id' : user_id.id,
                                                'type_name' : commission_brw.name,
                                                'comm_type' : commission_brw.comm_type,
                                                'commission_amount' : commission_amount,
                                                'pos_order_id' : order.id,
                                                'date':datetime.datetime.today()}
                    if invoice_commission_data and commission_amount > 0:
                        inv = invoice_commission_obj.sudo().create(invoice_commission_data)
                        invoice_commission_ids.append(inv)
        return invoice_commission_ids


    def get_partner_commission(self, commission_brw, order , user_id):
        '''This method calculates commission for Partner Based.
           @return : List of ids for commission records created.'''
        invoice_commission_ids = []
        
        invoice_commission_obj = self.env['pos.invoice.commission']
        sales_person_list = [x.sudo().id for x in commission_brw.user_ids]
        
        for line in order.lines:
            amount = line.price_subtotal
            invoice_commission_data = {}
            if (order.sudo().user_id and order.sudo().user_id.id in sales_person_list) and order.partner_id.is_affiliated == True:
                commission_amount = amount * (commission_brw.affiliated_partner_commission / 100)
                name = 'Partner Based commission " '+ tools.ustr(commission_brw.name) +' (' + tools.ustr(commission_brw.affiliated_partner_commission) + '%)" for Affiliated Partner "' + tools.ustr(order.partner_id.name) + '"'
                invoice_commission_data = {'name' : name,
                                        'user_id' : user_id.id,
                                        'partner_id' : order.partner_id.id,
                                        'commission_id' : commission_brw.id,
                                        'type_name' : commission_brw.name,
                                        'comm_type' : commission_brw.comm_type,
                                        'partner_type' : 'Affiliated Partner',
                                        'commission_amount' : commission_amount,
                                        'pos_order_id' : order.id,
                                        'date':datetime.datetime.today()}
            elif (order.sudo().user_id and order.sudo().user_id.id in sales_person_list) and  order.partner_id.is_affiliated == False:
                commission_amount = amount * (commission_brw.nonaffiliated_partner_commission / 100)
                name = 'Partner Based commission " '+ tools.ustr(commission_brw.name) +' (' + tools.ustr(commission_brw.nonaffiliated_partner_commission) + '%)" for Non-Affiliated Partner "' + tools.ustr(order.partner_id.name) + '"'
                invoice_commission_data = {'name' : name,
                                        'user_id' : user_id.id,
                                        'partner_id' : order.partner_id.id,
                                        'commission_id' : commission_brw.id,
                                        'type_name' : commission_brw.name,
                                        'comm_type' : commission_brw.comm_type,
                                        'partner_type' : 'Non-Affiliated Partner',
                                        'commission_amount' : commission_amount,
                                        'pos_order_id' : order.id,
                                        'date':datetime.datetime.today()}
            if invoice_commission_data and commission_amount > 0:
                inv = invoice_commission_obj.sudo().create(invoice_commission_data)
                invoice_commission_ids.append(inv)

        return invoice_commission_ids

    def get_discount_commission(self, commission_brw, order , user_id):
        '''This method calculates commission for Discount Based Rules.
           @return : List of ids for commission records created.'''
        invoice_commission_ids = []
        invoice_commission_obj = self.env['pos.invoice.commission']
        for line in order.lines:
            amount = line.price_subtotal
            invoice_commission_data = {}
            commission_percentage = 0.0
            commission_amount = 0.0
            name = ''
            sol_discount = line.discount
            if sol_discount == 0.0:
                commission_percentage = commission_brw.no_discount_commission_percentage
            elif sol_discount > commission_brw.max_discount_commission_percentage:
                for rule in commission_brw.rule_ids:
                    if rule.discount_percentage == sol_discount:
                        commission_percentage = rule.commission_percentage
            else:
                for rule in commission_brw.rule_ids:
                    if rule.discount_percentage == sol_discount:
                        commission_percentage = rule.commission_percentage

                if sol_discount > commission_brw.dis_commission_percentage:
                    commission_percentage = commission_brw.gt_discount_commission_percentage

            commission_amount = amount * (commission_percentage / 100)
            name = 'Discount Based commission for ' +' (' +  tools.ustr(sol_discount) +' %) discount is '+' (' +  tools.ustr(commission_percentage)+  '%) commission"'
            invoice_commission_data = {'name': name,
                            'user_id' : user_id.id,
                            'commission_id' : commission_brw.id,
                            'product_id' : line.product_id.id,
                            'type_name' : commission_brw.name,
                            'comm_type' : commission_brw.comm_type,
                            'commission_amount' : commission_amount,
                            'pos_order_id' : order.id,
                            'date':datetime.datetime.today()}
            if invoice_commission_data and commission_amount > 0:
                invoice_commission_ids.append(invoice_commission_obj.create(invoice_commission_data))
        return invoice_commission_ids 


    def get_standard_commission(self, commission_brw, order , user_id):
        '''This method calculates standard commission if any exception is not found for any product line.
           @return : Id of created commission record.'''
        invoice_commission_ids = []
        invoice_commission_obj = self.env['pos.invoice.commission']
        for line in order.lines:
            amount = line.price_subtotal
            standard_commission_amount = amount * (commission_brw.standard_commission / 100)
            name = 'Standard commission " '+ tools.ustr(commission_brw.name) +' ( ' + tools.ustr(commission_brw.standard_commission) + '%)" for product "' + tools.ustr(line.product_id.name) + '"'
            standard_invoice_commission_data = {
                               'name': name,
                               'user_id' : user_id.id,
                               'commission_id' : commission_brw.id,
                               'product_id' : line.product_id.id,
                               'type_name' : commission_brw.name,
                               'comm_type' : commission_brw.comm_type,
                               'commission_amount' : standard_commission_amount,
                               'pos_order_id' : order.id,
                               'date':datetime.datetime.today()}
            inv = invoice_commission_obj.sudo().create(standard_invoice_commission_data)
            invoice_commission_ids.append(inv)
        return invoice_commission_ids


    def get_sales_commission(self):
        '''This is control method for calculating commissions(called from workflow).
           @return : List of ids for commission records created.'''
        invoice_commission_ids = []
        for order in self:
            if order.user_id:
                
                commission_obj = self.env['pos.commission']
                user_id = False
                if order.config_id.module_pos_hr and  order.employee_id.id:
                    if order.employee_id.user_id.id:
                        user_id = order.employee_id.user_id
                    else:
                        raise UserError(_('for commission line , user must be created, %s employee not related any user ') % (order.employee_id.name))
                else:
                    user_id = order.user_id
                commission_id = commission_obj.sudo().search([('user_ids', 'in', user_id.id)])
                if not commission_id:
                    return False
                else:
                    commission_id = commission_id[0]
                commission_brw = commission_id
                if commission_brw.comm_type == 'mix':
                    invoice_commission_ids = self.get_mix_commission(commission_brw, order , user_id)
                elif commission_brw.comm_type == 'partner':
                    invoice_commission_ids = self.get_partner_commission(commission_brw, order , user_id)
                elif commission_brw.comm_type == 'discount':
                    invoice_commission_ids = self.get_discount_commission(commission_brw, order , user_id)
                else:
                    invoice_commission_ids = self.get_standard_commission(commission_brw, order , user_id)

        return invoice_commission_ids


    @api.model
    def create_from_ui(self, orders, draft=False):
        order_ids = super(PosOrder, self).create_from_ui(orders, draft=False)
        # This code is for pos_commission
        commission_configuration = self.env.user.company_id.commission_configuration
        if commission_configuration == True:
            for order_id in order_ids:
                pos_order_id = self.browse(order_id.get('id'))
                pos_order_id.get_sales_commission()
        return order_ids
