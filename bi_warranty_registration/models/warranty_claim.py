# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class crmClaim(models.Model):
    _name = "warranty.claim"
    _description = "Claim"
    _order = "priority,date desc"

    id = fields.Integer('ID', readonly=True)
    name = fields.Char('Claim Subject', required=True)
    active = fields.Boolean('Active', default=lambda *a: 1)
    action_next = fields.Char('Next Action')
    date_action_next = fields.Datetime('Next Action Date')
    description = fields.Text('Description')
    resolution = fields.Text('Resolution')
    create_date = fields.Datetime('Creation Date', readonly=True)
    write_date = fields.Datetime('Update Date', readonly=True)
    date_deadline = fields.Date('Deadline')
    date_closed = fields.Datetime('Closed', readonly=True)
    date = fields.Datetime('Claim Date', index=True, default=fields.datetime.now())
    categ_id = fields.Many2one('warranty.claim.category', 'Category')
    priority = fields.Selection([('0', 'Low'), ('1', 'Normal'), ('2', 'High')], 'Priority', default='1')
    type_action = fields.Selection([('correction', 'Corrective Action'), ('prevention', 'Preventive Action')],
                                   'Action Type')
    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self.env.user)
    user_fault = fields.Char('Trouble Responsible')
    team_id = fields.Many2one('crm.team', 'Sales Team', \
                              index=True, help="Responsible sales team." \
                                               " Define Responsible user and Email account for" \
                                               " mail gateway.")
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company'])
    partner_id = fields.Many2one('res.partner', 'Customer')
    email_cc = fields.Text('Watchers Emails',
                           help="These email addresses will be added to the CC field of all inbound and outbound emails for this record before being sent. Separate multiple email addresses with a comma")
    email_from = fields.Char('Email', help="Destination email for email gateway.")
    partner_phone = fields.Char('Phone')
    stage_id = fields.Many2one('warranty.claim.stage', 'Stage', index=True)
    cause = fields.Text('Root Cause')
    product_ids = fields.Many2many('product.product', string="Products");
    product_id = fields.Many2one('product.product', 'Product', domain="[('id','in',product_ids)]", required=True)
    serial_nos = fields.Many2many('stock.lot', )
    serial_no = fields.Many2one('stock.lot', "Serial No", domain="[('product_id', '=', product_id)]", required=True)
    warranty = fields.Many2one('product.warranty', 'Related Warranty')
    stage_match = fields.Selection([('first', 'first'), ('second', 'second'), ('third', 'third'), ('fourth', 'fourth')],
                                   'Stage Match', default='first')

    @api.onchange('partner_id')
    def customer_details(self):
        self.partner_phone = self.partner_id.phone
        self.email_from = self.partner_id.email
        warranty_claim_obj = self.env['product.warranty'].search(
            [('partner_id', '=', self.partner_id.id), ('state', 'not in', ['expired', 'new'])])
        prod = []
        if warranty_claim_obj:
            for i in warranty_claim_obj:
                prod.append(i.product_id.id)
        self.write({"product_ids": [(6, 0, prod)], })

    @api.onchange('serial_no')
    def warranty_updt_serial(self):
        warranty_claim_obj = self.env['product.warranty'].search([])
        for res in warranty_claim_obj:
            if res.product_serial_id == self.serial_no:
                self.update({'warranty': res.id})

    def submit_claim(self):
        warranty_obj = self.env['product.warranty'].search([('product_serial_id', '=', self.serial_no.id)])
        if not warranty_obj:
            raise ValidationError(_('Warranty is not created for this product'))
        else:
            stage_nxt = self.env['ir.model.data']._xmlid_to_res_id('bi_warranty_registration.stage_claim5')
            self.update({'stage_id': stage_nxt, 'stage_match': 'second'})

        if warranty_obj:
            if warranty_obj.state == 'new':
                raise ValidationError(_('Warranty is not confirmed for this product'))

        if warranty_obj:
            if warranty_obj.warranty_end_date:
                if fields.datetime.today().date() > warranty_obj.warranty_end_date:
                    raise ValidationError(_('Warranty is expired for this product'))

    def completed_claim(self):
        stage_nxt1 = self.env['ir.model.data']._xmlid_to_res_id('bi_warranty_registration.stage_claim2')
        self.update({'stage_id': stage_nxt1, 'stage_match': 'third'})

    def claim_done(self):
        stage_nxt2 = self.env['ir.model.data']._xmlid_to_res_id('bi_warranty_registration.stage_claim3')
        self.update({'stage_id': stage_nxt2, 'stage_match': 'fourth'})

    @api.model
    def create(self, vals):
        context = dict(self._context or {})
        if vals.get('team_id') and not self._context.get('default_team_id'):
            context['default_team_id'] = vals.get('team_id')
        # context: no_log, because subtype already handle this
        return super(crmClaim, self).create(vals)

    @api.model
    def default_get(self, flds):
        result = super(crmClaim, self).default_get(flds)
        stage_nxt1 = self.env['ir.model.data']._xmlid_to_res_id('bi_warranty_registration.stage_claim1')
        result['stage_id'] = stage_nxt1
        return result


class crm_claim_category(models.Model):
    _name = "warranty.claim.category"
    _description = "Category of claim"

    name = fields.Char('Name', required=True, translate=True)
    team_id = fields.Many2one('crm.team', 'Sales Team')
