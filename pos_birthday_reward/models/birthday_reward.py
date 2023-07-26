# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    birth_date = fields.Date(string="Birthdate")
    is_birthdate_month = fields.Boolean(
        compute="_compute_month", string="Birthday Discount", store=True
    )
    birthday_order_counter = fields.Integer(string="Total Birthday Order")

    @api.depends("birth_date")
    def _compute_month(self):
        for record in self:
            current_month = fields.Date.today().strftime("%m")
            if record.birth_date:
                birth_month = str(record.birth_date).split("-")[1]
                if birth_month == current_month:
                    record.is_birthdate_month = True
                else:
                    record.is_birthdate_month = False

class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            records = self.env['res.partner'].search([('id','=',vals['partner_id'])])
            current_month = fields.Date.today().strftime("%Y-%m")
            for rec in records:
                orders = self.env["pos.order"].search(
                    [("partner_id", "=", rec.id), ("state", "!=", "cancel")]
                )
                orders = orders.filtered(
                    lambda x: x.date_order.strftime("%Y-%m") == current_month
                )
                lines = orders.mapped("lines")
                b_lines = lines.filtered(
                    lambda x: x.membership_birthmonth_discount > 0
                )
                b_order = b_lines.mapped("order_id")
                rec.birthday_order_counter = len(b_order)
        return super().create(vals)

class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    membership_birthmonth_discount = fields.Float(
        string="Birthday Discount(%)"
    )

    @api.depends("price_unit", "tax_ids", "qty", "discount", "product_id")
    def _compute_amount_line_all(self):
        for line in self:
            currency = line.order_id.pricelist_id.currency_id
            taxes = line.tax_ids.filtered(
                lambda tax: tax.company_id.id == line.order_id.company_id.id
            )
            fiscal_position_id = line.order_id.fiscal_position_id
            if fiscal_position_id:
                taxes = fiscal_position_id.map_tax(
                    taxes, line.product_id, line.order_id.partner_id
                )
            price = (
                line.price_unit
                * (1 - (line.discount or 0.0) / 100.0)
                * (1 - (line.membership_birthmonth_discount or 0.0) / 100.0)
            )
            line.price_subtotal = line.price_subtotal_incl = price * line.qty
            if taxes:
                taxes = taxes.compute_all(
                    price,
                    currency,
                    line.qty,
                    product=line.product_id,
                    partner=line.order_id.partner_id or False,
                )
                line.price_subtotal = taxes["total_excluded"]
                line.price_subtotal_incl = taxes["total_included"]
            line.price_subtotal = currency.round(line.price_subtotal)
            line.price_subtotal_incl = currency.round(line.price_subtotal_incl)


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.model
    def _process_order(self, order, draft, existing_order):
        rec = super(PosOrder, self)._process_order(
            order, draft, existing_order
        )
        if rec:
            order_id = self.browse(rec)
            if order_id and order_id.partner_id:
                current_month = fields.Date.today().strftime("%Y-%m")
                orders = self.search(
                    [
                        ("partner_id", "=", order_id.partner_id.id),
                        ("state", "!=", "cancel"),
                    ]
                )
                orders = orders.filtered(
                    lambda x: x.date_order.strftime("%Y-%m") == current_month
                )
                lines = orders.mapped("lines")
                b_lines = lines.filtered(
                    lambda x: x.membership_birthmonth_discount > 0
                )
                b_order = b_lines.mapped("order_id")
                order_id.partner_id.birthday_order_counter = len(b_order)
        return rec


class PosConfig(models.Model):
    _inherit = "pos.config"

    birthday_discount = fields.Float(
        string="Birthday Month Discount(%)", store=True
    )
    is_first_order_apply = fields.Boolean(
        string="Only apply discount on first order in birthday month.",
        store=True,
    )


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    birthday_discount = fields.Float(
        string="Birthday Month Discount(%)",
        related="pos_config_id.birthday_discount",
        readonly=False,
    )
    is_first_order_apply = fields.Boolean(
        string="Only apply discount on first order in birthday month.",
        related="pos_config_id.is_first_order_apply",
        readonly=False,
    )


class PosSession(models.Model):
    _inherit = "pos.session"

    def _loader_params_res_partner(self):
        result = super(PosSession, self)._loader_params_res_partner()
        result["search_params"]["fields"].extend(
            ["birth_date", "is_birthdate_month", "birthday_order_counter"]
        )
        return result
