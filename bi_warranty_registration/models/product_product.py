# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class productProduct(models.Model):
    _inherit = 'product.product'

    under_warranty = fields.Boolean('Under Warranty')
    warranty_period = fields.Integer("Warranty Period")
    allow_renewal = fields.Boolean('Allow Renewal')
    warranty_renewal_time = fields.Integer("Allow Warranty Renewal Times ")
    warranty_renewal_period = fields.Integer("Warranty Renewal Period")
    warranty_renewal_cost = fields.Float("Warranty renewal Cost")
    create_warranty_with_saleorder = fields.Boolean('Create Warranty from Sale Order')
    warranty_sale_config = fields.Boolean(compute='_compute_sale_warranty')

    def _compute_sale_warranty(self):
        tmp = self.env['warranty.settings'].search([], order="id desc", limit=1).create_warranty_from_saleorder
        for line in self:
            line.warranty_sale_config = tmp

    @api.model
    def create(self, vals):
        res = super(productProduct, self).create(vals)
        template = res.product_tmpl_id
        if template:
            if template.under_warranty:
                res.under_warranty = template.under_warranty
                res.warranty_period = template.warranty_period
            else:
                template.under_warranty = res.under_warranty
                template.warranty_period = res.warranty_period
            if template.allow_renewal:
                res.allow_renewal = template.allow_renewal
                res.warranty_renewal_time = template.warranty_renewal_time
                res.warranty_renewal_period = template.warranty_renewal_period
                res.warranty_renewal_cost = template.warranty_renewal_cost
            else:
                template.allow_renewal = res.allow_renewal
                template.warranty_renewal_time = res.warranty_renewal_time
                template.warranty_renewal_period = res.warranty_renewal_period
                template.warranty_renewal_cost = res.warranty_renewal_cost
            if template.create_warranty_with_saleorder:
                res.create_warranty_with_saleorder = template.create_warranty_with_saleorder
            else:
                template.create_warranty_with_saleorder = res.create_warranty_with_saleorder
        return res
