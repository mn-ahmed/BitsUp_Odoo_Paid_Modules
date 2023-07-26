# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

import time
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError
from odoo.osv import expression


class AccountFiscalyear(models.Model):
    _name = "account.fiscalyear"
    _description = "Fiscal Year"
    _order = "date_start, id"

    name = fields.Char('Fiscal Year', required=True)
    code = fields.Char('Code', size=6, required=True)
    company_id = fields.Many2one('res.company', 'Company', required=True,
        default=lambda self: self.env.company)
    date_start = fields.Date('Start Date', required=True,
        default=lambda *a: time.strftime('%Y-%m-01 %H:59:%S'))
    date_stop = fields.Date('End Date', required=True,
        default=lambda *a: time.strftime('%Y-12-31 %H:59:%S'))
    period_ids = fields.One2many('account.period', 'fiscalyear_id', 'Periods')

    @api.constrains('date_start', 'date_stop')
    def _check_duration(self):
        if self.date_stop < self.date_start:
            raise UserError(_('Error!\nThe start date of a fiscal year must precede its end date.'))

    def create_period3(self):
        return self.create_period(3)

    def create_period1(self):
        return self.create_period(1)

    def create_period(self, interval=1):
        period_obj = self.env['account.period']
        for fy in self:
            date_start = fy.date_start
            period_obj.create({
                'name': "%s %s" % (_('Opening Period'), date_start.strftime('%Y')),
                'code': date_start.strftime('00/%Y'),
                'date_start': date_start,
                'date_stop': date_start,
                'special': True,
                'fiscalyear_id': fy.id,
            })
            while date_start < fy.date_stop:
                date_end = date_start + relativedelta(months=interval, days=-1)
                if date_end > fy.date_stop:
                    date_end = fy.date_stop
                period_obj.create({
                    'name': date_start.strftime('%b-%Y'),
                    'code': date_start.strftime('%m/%Y'),
                    'date_start': date_start,
                    'date_stop': date_end,
                    'fiscalyear_id': fy.id,
                })
                date_start = date_start + relativedelta(months=interval)
        return True

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        if operator in expression.NEGATIVE_TERM_OPERATORS:
            domain = [('code', operator, name), ('name', operator, name)]
        else:
            domain = ['|', ('code', operator, name), ('name', operator, name)]
        objs = self.search(expression.AND([domain, args]), limit=limit)
        return objs.name_get()
