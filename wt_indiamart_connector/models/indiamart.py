import json
import requests
from odoo import fields, models, api, _
from odoo.exceptions import Warning
from datetime import datetime
import pytz
from odoo.exceptions import UserError, ValidationError


class Indiamart(models.Model):
    _name = 'indiamart.indiamart'
    _description = 'Indiamart'

    name = fields.Char(string='App Name', required=True)
    client_key = fields.Char(string='Client Key', required=True)
    active = fields.Boolean(string='Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)
    is_date_interval = fields.Boolean(string='Fetch Lead Between 2 Date')
    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(string='End Date')


    _sql_constraints = [
        ('instance_uniq', 'unique (client_key, company_id)', 'The instance with same hostname and secret key exists already !')
    ]

    def write(self, vals):
        res = super(Indiamart, self).write(vals)
        if 'start_date' in vals or 'end_date' in vals:
            if (self.end_date - self.start_date).days > 7:
                raise ValidationError(_('You can Fetch Maximum 7 days lead at a time'))
            else:
                pass
        return res

    @api.model_create_multi
    def create(self, vals):
        res = super(Indiamart, self).create(vals)
        if res.start_date and res.end_date:
            if (res.end_date - res.start_date).days > 7:
                raise ValidationError(_('You can Fetch Maximum 7 days lead at a time'))
            else:
                pass
        return res


    def get_import_data_xeroapi(self, url, status=''):
        response = requests.request("GET", url,)
        if response.status_code == 200:
            res = json.loads(response.text)
            return res
        else:
            raise Warning(_('Authentication Failed !\nPlease authenticate again.'))

    def indiamart_get_lead(self):
        if self.env.context.get('manual_fetch') and self.start_date != False and self.end_date != False:
            user = self.env['res.users'].browse(self.env.uid)
            tz = pytz.timezone(user.tz if user.tz else 'UTC')
            startdate = pytz.utc.localize(self.start_date).astimezone(tz).strftime('%d-%m-%Y %H:%M:%S')
            enddate = pytz.utc.localize(self.end_date).astimezone(tz).strftime('%d-%m-%Y %H:%M:%S')
            url = "https://mapi.indiamart.com/wservce/crm/crmListing/v2/?glusr_crm_key={}&start_time={}&end_time={}".format(self.client_key, startdate, enddate)
        else:
            url = "https://mapi.indiamart.com/wservce/crm/crmListing/v2/?glusr_crm_key={}".format(self.client_key)
        res = self.get_import_data_xeroapi(url)
        if res['RESPONSE']:
            for lead in res['RESPONSE']:
                country_id = self.env['res.country'].search([('code', '=', lead.get('SENDER_COUNTRY_ISO'))], limit=1)
                state_id = self.env['res.country.state'].search([('name', '=', lead.get('SENDER_STATE'))], limit=1)
                name = lead.get('QUERY_PRODUCT_NAME') if lead.get('QUERY_PRODUCT_NAME') else lead.get('SENDER_NAME')
                existing_lead = self.env['crm.lead'].search([('unique_query_id', '=', lead.get('UNIQUE_QUERY_ID'))])
                if not existing_lead:
                    self.env['crm.lead'].create({
                        'name': name,
                        'contact_name': lead.get('SENDER_NAME'),
                        'unique_query_id': lead.get('UNIQUE_QUERY_ID'),
                        'phone': lead.get('SENDER_MOBILE'),
                        'email_from': lead.get('SENDER_EMAIL'),
                        'mobile': lead.get('SENDER_MOBILE_ALT'),
                        'partner_name': lead.get('SENDER_COMPANY'),
                        'street': lead.get('SENDER_ADDRESS'),
                        'city': lead.get('SENDER_CITY'),
                        'state_id': state_id.id if state_id else None,
                        'country_id': country_id.id if country_id else None,
                        'description': lead.get('QUERY_MESSAGE'),
                        })
        self._cr.commit()
