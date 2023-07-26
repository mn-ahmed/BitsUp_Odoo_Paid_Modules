from odoo import fields, models, api, _


class CRMLeadExtend(models.Model):
    _inherit = 'crm.lead'

    unique_query_id = fields.Char(string='UNIQUE QUERY ID')