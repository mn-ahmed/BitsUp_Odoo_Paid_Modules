from odoo import api, fields, models, tools, _


class Partner(models.Model):
	_inherit = 'res.partner'
	
	is_affiliated = fields.Boolean(string="Affiliated", default=False,
							   help="Check this box if this customer is Affiliated.")