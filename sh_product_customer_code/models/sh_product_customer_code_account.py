# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.


from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        res = super(AccountMove, self)._onchange_partner_id()
        if self._origin:
            if self._origin.invoice_line_ids:
                # Partner Parent Child Record Can Show now
                partners = []
                partners.append(self.partner_id.id)
                if self.partner_id and self.partner_id.child_ids:
                    for child in self.partner_id.child_ids:
                        partners.append(child.id)

                if self.partner_id and self.partner_id.parent_id:
                    partners.append(self.partner_id.parent_id.id)
                    if self.partner_id.parent_id.child_ids:
                        for child in self.partner_id.parent_id.child_ids:
                            partners.append(child.id)

                for line in self._origin.invoice_line_ids:

                    customer_code = self.env['sh.product.customer.info'].sudo(
                    ).search([('name', 'in', partners),
                              ('product_id', '=', line.product_id.id)],
                             limit=1)
                    if customer_code:
                        if customer_code.product_code:
                            line.sh_line_customer_code = customer_code.product_code
                        else:
                            line.sh_line_customer_code = False
                    else:
                        line.sh_line_customer_code = False
                    if customer_code:
                        if customer_code.product_name:
                            line.sh_line_customer_product_name = customer_code.product_name
                        else:
                            line.sh_line_customer_product_name = False
                    else:
                        line.sh_line_customer_product_name = False
        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    sh_line_customer_code = fields.Char(string='Customer Product Code')
    sh_line_customer_product_name = fields.Char(string='Customer Product Name')

    @api.model_create_multi
    def create(self, vals_list):
        res_super = super(AccountMoveLine, self).create(vals_list)
        for rec in res_super:
            if rec.product_id:
                # Partner Parent Child Record Can Show now
                partners = []
                partners.append(rec.move_id.partner_id.id)
                if rec.move_id.partner_id and rec.move_id.partner_id.child_ids:
                    for child in rec.move_id.partner_id.child_ids:
                        partners.append(child.id)

                if rec.move_id.partner_id and rec.move_id.partner_id.parent_id:
                    partners.append(rec.move_id.partner_id.parent_id.id)
                    if rec.move_id.partner_id.parent_id.child_ids:
                        for child in rec.move_id.partner_id.parent_id.child_ids:
                            partners.append(child.id)

                customer_code = self.env['sh.product.customer.info'].sudo(
                ).search([('name', 'in', partners),
                          ('product_id', '=', rec.product_id.id)],
                         limit=1)
                if customer_code:
                    if customer_code.product_code:
                        rec.sh_line_customer_code = customer_code.product_code
                    else:
                        rec.sh_line_customer_code = False
                else:
                    rec.sh_line_customer_code = False
                if customer_code:
                    if customer_code.product_name:
                        rec.sh_line_customer_product_name = customer_code.product_name
                    else:
                        rec.sh_line_customer_product_name = False
                else:
                    rec.sh_line_customer_product_name = False
        return res_super

    @api.onchange('product_id')
    def _inverse_product_id(self):
        res = super(AccountMoveLine, self)._inverse_product_id()

        for line in self:
            if line.product_id:

                # Partner Parent Child Record Can Show now
                partners = []
                partners.append(line.move_id.partner_id.id)
                if line.move_id.partner_id and line.move_id.partner_id.child_ids:
                    for child in line.move_id.partner_id.child_ids:
                        partners.append(child.id)

                if line.move_id.partner_id and line.move_id.partner_id.parent_id:
                    partners.append(line.move_id.partner_id.parent_id.id)
                    if line.move_id.partner_id.parent_id.child_ids:
                        for child in line.move_id.partner_id.parent_id.child_ids:
                            partners.append(child.id)

                customer_code = self.env['sh.product.customer.info'].sudo(
                ).search([('name', 'in', partners),
                          ('product_id', '=', line.product_id.id)],
                         limit=1)
                if customer_code:
                    if customer_code.product_code:
                        line.sh_line_customer_code = customer_code.product_code
                    else:
                        line.sh_line_customer_code = False
                else:
                    line.sh_line_customer_code = False

                if customer_code:
                    if customer_code.product_name:
                        line.sh_line_customer_product_name = customer_code.product_name
                    else:
                        line.sh_line_customer_product_name = False
                else:
                    line.sh_line_customer_product_name = False

        return res
