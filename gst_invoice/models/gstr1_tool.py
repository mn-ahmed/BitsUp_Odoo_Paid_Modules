# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# See LICENSE file for full copyright and licensing details.
# License URL : <https://store.webkul.com/license.html/>
##############################################################################

import base64
import csv
import io
import json
from urllib.parse import unquote_plus

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons.gst_invoice.models.gstr_columns import GSTTYPECOLUMN

GSTTypeList = ['b2b','b2bur','b2cs','b2cl','export','cdnr','cdnur','imps','impg']

def _unescape(text):
    try:
        text = unquote_plus(text.encode('utf8'))
        return text
    except Exception as e:
        return text

class Gstr1Tool(models.Model):

    _name = 'gstr1.tool'
    _description = 'GSTR1 Tool'
    _inherit = ['mail.thread']

    def _get_gst_attachments(self):
        attachments = []
        for gst_type in GSTTypeList:
            attachment = getattr(self, '%s_attachment' % gst_type)
            if attachment:
                attachments.append(attachment.id)
        return attachments

    @api.depends('b2b_attachment', 'b2cs_attachment', 'b2bur_attachment',
                 'b2cl_attachment', 'imps_attachment', 'impg_attachment',
                 'export_attachment', 'cdnr_attachment', 'cdnur_attachment',
                 'hsn_attachment', 'json_attachment')
    def _get_attachment_count(self):
        attachments = self._get_gst_attachments()
        self.update({'attachment_count': len(attachments)})

    @api.depends('invoice_lines')
    def _get_invoice_count(self):
        for gst in self:
            gst.update({'invoices_count': len(gst.invoice_lines)})

    def _get_gst_type(self):
        return [('gstr1', 'GSTR1'), ('gstr2', 'GSTR2')]

    _gst_type_selection = lambda self, * \
        args, **kwargs: self._get_gst_type(*args, **kwargs)

    name = fields.Char(string='GST Invoice')
    gst_type = fields.Selection(string='GST Type', selection=_gst_type_selection,
                                help="GST Typr. ex : ('gstr1', 'gstr2' ...)", default='gstr1')
    reverse_charge = fields.Boolean(string='Reverse Charge', help="Allow reverse charges for b2b invoices")
    counter_filing_status = fields.Boolean(string='Counter Party Filing Status', default=True,
                                           help="Select when counter party has filed for b2b and cdnr invoices")
    period_id = fields.Many2one('account.period', tracking=True, string='Period')
    status = fields.Selection(
        [('not_uploaded', 'Not uploaded'),
         ('ready_to_upload', 'Ready to upload'),
         ('uploaded', 'Uploaded to govt'), ('filed', 'Filed')],
        string='Status', default="not_uploaded", tracking=True, help="status will be consider during gst import, ")
    cgt = fields.Float(string='Current Gross Turnover', tracking=True, help="Current Gross Turnover")
    gt_amount = fields.Float(string='Gross Turnover', tracking=True, help="Gross Turnover till current date")
    date_from = fields.Date(string='Date From', help="Date starting range for filter")
    date_to = fields.Date(string='Date To', help="Date end range for filter")
    invoice_lines = fields.Many2many('account.move', 'gst_account_invoice', 'gst_id', 'account_inv_id',string='Customer Invoices', help="Invoices belong to selected period.")
    b2b_attachment = fields.Many2one('ir.attachment', help="B2B Invoice Attachment")
    b2bur_attachment = fields.Many2one('ir.attachment', help="B2BUR Invoice Attachment")
    b2cs_attachment = fields.Many2one('ir.attachment', help="B2CS Invoice Attachment")
    b2cl_attachment = fields.Many2one('ir.attachment', help="B2CL Invoice Attachment")
    export_attachment = fields.Many2one('ir.attachment', help="Export Invoice Attachment")
    imps_attachment = fields.Many2one('ir.attachment', help="IMPS Invoice Attachment")
    impg_attachment = fields.Many2one('ir.attachment', help="IMPG Invoice Attachment")
    hsn_attachment = fields.Many2one('ir.attachment', help="HSN Data Attachment")
    cdnr_attachment = fields.Many2one('ir.attachment', help="CDNR Data Attachment")
    cdnur_attachment = fields.Many2one('ir.attachment', help="CDNUR Data Attachment")
    json_attachment = fields.Many2one('ir.attachment', help="json date attachment")
    attachment_count = fields.Integer(string='# of Attachments', compute='_get_attachment_count',
                                      readonly=True, help="Number of attachments")
    invoices_count = fields.Integer(string='# of Invoices', compute='_get_invoice_count',
                                    readonly=True, help="Number of invoices")
    itc_eligibility = fields.Selection([
        ('Inputs', 'Inputs'),
        ('Capital goods', 'Capital goods'),
        ('Input services', 'Input services'),
        ('Ineligible', 'Ineligible'),
    ], string='ITC Eligibility', default='Ineligible')
    company_id = fields.Many2one('res.company', string='Company', change_default=True,
                                 required=True, readonly=True,default=lambda self: self.env.user.company_id)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code('gstr1.tool')
        return super(Gstr1Tool, self).create(vals_list)

    def unlink(self):
        for obj in self:
            if obj.status != 'not_uploaded':
                raise UserError("GST invoice can't be delete as invoices are already generated.")
        return super(Gstr1Tool, self).unlink()

    def write(self, vals):
        res = super(Gstr1Tool, self).write(vals)
        for obj in self:
            if obj.date_from and obj.date_to:
                if obj.period_id.date_start > obj.date_from or obj.period_id.date_start > obj.date_to or obj.period_id.date_stop < obj.date_to or obj.period_id.date_stop < obj.date_from:
                    raise UserError("Date should belong to selected period")
                if obj.date_from > obj.date_to:
                    raise UserError("End date should greater than or equal to starting date")
        return res

    def onchange(self, values, field_name, field_onchange):
        ctx = dict(self._context or {})
        ctx['current_id'] = values.get('id')
        return super(Gstr1Tool, self.with_context(ctx)).onchange(values, field_name, field_onchange)

    def reset(self):
        totalInvoices = len(self.invoice_lines)
        for gst_type in GSTTypeList:
            attachment = getattr(self, '%s_attachment' % gst_type)
            if attachment:
                attachment.unlink()
        if self.hsn_attachment:
            self.hsn_attachment.unlink()
        if self.json_attachment:
            self.json_attachment.unlink()
        self.status = 'not_uploaded'
        self.updateInvoiceStatus('not_uploaded')
        if self.gst_type == 'gstr1':
            self.fetchInvoices()
        elif self.gst_type == 'gstr2':
            self.fetchSupplierInvoices()
        body = '<b>RESET </b>: {} GST Invoices'.format(totalInvoices)
        self.message_post(body=_(body), subtype_xmlid='mail.mt_comment')
        return True

    def action_view_invoice(self):
        invoices = self.mapped('invoice_lines')
        action = self.env.ref('gst_invoice.customer_invoice_list_action').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def action_view_attachment(self):
        attachments = self._get_gst_attachments()
        action = self.env.ref('gst_invoice.gst_attachments_action').read()[0]
        if len(attachments) > 1:
            action['domain'] = [('id', 'in', attachments)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    @api.onchange('period_id', 'date_from', 'date_to')
    def _compute_invoice_lines(self):
        domain = {}
        filter = []
        ctx = dict(self._context or {})
        if ctx.get('current_id'):
            filter = [('id', '!=', ctx.get('current_id'))]
        invoiceType = ['out_invoice', 'out_refund']
        if self.gst_type == 'gstr2':
            invoiceType = ['in_invoice', 'in_refund']
        invoiceObjs = self.getInvoiceObjs(filter, invoiceType)
        self.updateGSTInvoiceLines(invoiceObjs)
        domain.update({
            'invoice_lines': [('id', 'in', invoiceObjs.ids)],
        })
        return {'domain': domain}

    def fetchInvoices(self):
        filter = [('id', '!=', self.id)]
        invoiceObjs = self.getInvoiceObjs(filter, ['out_invoice', 'out_refund'])
        self.invoice_lines = [(6, 0, invoiceObjs.ids)]
        if invoiceObjs:
            self.updateInvoiceCurrencyRate(invoiceObjs)
            self.updateGSTInvoiceLines(invoiceObjs)
        return True

    def fetchSupplierInvoices(self):
        filter = [('id', '!=', self.id)]
        invoiceObjs = self.getInvoiceObjs(filter, ['in_invoice', 'in_refund'])
        self.invoice_lines = [(6, 0, invoiceObjs.ids)]
        if invoiceObjs:
            self.updateInvoiceCurrencyRate(invoiceObjs)
            self.updateGSTInvoiceLines(invoiceObjs)
        return True

    def updateInvoiceCurrencyRate(self, invoiceObjs):
        for invoiceObj in invoiceObjs:
            currency = invoiceObj.currency_id
            amount_total = invoiceObj.amount_total_signed
            if currency.name != 'INR':
                amount_total *= currency.rate
            invoiceObj.inr_total = amount_total
        return True

    def updateGSTInvoiceLines(self, invoiceObjs):
        code = self.env.company.state_id.code
        for invoiceObj in invoiceObjs:
            if invoiceObj.move_type in ['in_refund', 'out_refund']:
                if invoiceObj.partner_id.country_id.code == 'IN' and invoiceObj.partner_id.vat:
                    invoiceObj.invoice_type = 'cdnr'
                else:
                    invoiceObj.invoice_type = 'cdnur'
            elif invoiceObj.move_type == 'in_invoice':
                if invoiceObj.partner_id.country_id.code == 'IN':
                    if invoiceObj.partner_id.vat:
                        invoiceObj.invoice_type = 'b2b'
                    else:
                        invoiceObj.invoice_type = 'b2bur'
                else:
                    invoiceObj.invoice_type = 'import'
            else:
                if invoiceObj.partner_id.country_id.code == 'IN':
                    if invoiceObj.partner_id.vat:
                        invoiceObj.invoice_type = 'b2b'
                    elif invoiceObj.inr_total >= 250000 and invoiceObj.partner_id.state_id.code != code:
                        invoiceObj.invoice_type = 'b2cl'
                        if not invoiceObj.bonded_wh:
                            invoiceObj.bonded_wh = 'no'
                    else:
                        invoiceObj.invoice_type = 'b2cs'
                else:
                    invoiceObj.invoice_type = 'export'
                    invoiceObj.export = 'WOPAY'
        return True

    def getInvoiceObjs(self, extrafilter=[], invoiceType=[]):
        invoiceObjs = self.env['account.move']
        gstObjs = self.search(extrafilter)
        invoiceIds = gstObjs and gstObjs.mapped(
            'invoice_lines') and gstObjs.mapped('invoice_lines').ids or []
        if self.period_id:
            filter = ['|',
                      '&', '&', ('move_type', 'in', ['out_invoice', 'out_refund']),
                      ('invoice_date', '>=', self.period_id.date_start),
                      ('invoice_date', '<=', self.period_id.date_stop),
                      '&', '&', ('move_type', 'in', ['in_invoice', 'in_refund']),
                      ('date', '>=', self.period_id.date_start),
                      ('date', '<=', self.period_id.date_stop),
                      ('gst_status', '=', 'not_uploaded'),
                      ('move_type', 'in', invoiceType),
                      ('company_id', '=', self.company_id.id),
                      ('state', 'in', ['posted']),
                      ]
            if not self.date_from:
                self.date_from = self.period_id.date_start
                self.date_to = self.period_id.date_stop
            if self.date_from and self.date_to:
                if self.period_id.date_start > self.date_from \
                        or self.period_id.date_start > self.date_to \
                        or self.period_id.date_stop < self.date_to \
                        or self.period_id.date_stop < self.date_from:
                    raise UserError(_("Date should belong to selected period"))
                if self.date_from > self.date_to:
                    raise UserError(
                        _("End date should greater than or equal to starting date"))
                filter += ['|',
                           '&', '&', ('move_type', 'in', ['out_invoice', 'out_refund']),
                           ('invoice_date', '>=', self.date_from),
                           ('invoice_date', '<=', self.date_to),
                           '&', '&', ('move_type', 'in', ['in_invoice', 'in_refund']),
                           ('date', '>=', self.date_from),
                           ('date', '<=', self.date_to),
                           ]
            if invoiceIds:
                filter.append(('id', 'not in', invoiceIds))
            invoiceObjs = invoiceObjs.search(filter)
        return invoiceObjs

    def generateCsv(self):
        invoiceObjs = self.invoice_lines
        name = self.name
        gstinCompany = self.env.company.vat
        fp = (self.period_id.code or '').replace('/', '')
        jsonData = {
            "gstin": gstinCompany,
            "fp": fp,
            "version": "GST3.0.4",
            "hash": "hash",
            # "gt": self.gt,
            # "cur_gt": self.cgt,
        }
        gstType = self.gst_type
        if invoiceObjs:
            typeDict = {}
            invoiceIds = invoiceObjs.ids
            for invoiceObj in invoiceObjs:
                if typeDict.get(invoiceObj.invoice_type):
                    typeDict.get(invoiceObj.invoice_type).append(invoiceObj.id)
                else:
                    typeDict[invoiceObj.invoice_type] = [invoiceObj.id]
            typeList = self.getTypeList()
            for invoice_type, active_ids in typeDict.items():
                if invoice_type in typeList:
                    continue
                respData = self.exportCsv(active_ids, invoice_type, name, gstType)
                attachment = respData[0]
                jsonInvoiceData = respData[1]
                if invoice_type == 'b2b':
                    jsonData.update({invoice_type: jsonInvoiceData})
                    self.b2b_attachment = attachment.id
                if invoice_type == 'b2bur':
                    jsonData.update({invoice_type: jsonInvoiceData})
                    self.b2bur_attachment = attachment.id
                if invoice_type == 'b2cs':
                    self.b2cs_attachment = attachment.id
                    jsonData.update({invoice_type: jsonInvoiceData})
                if invoice_type == 'b2cl':
                    jsonData.update({invoice_type: jsonInvoiceData})
                    self.b2cl_attachment = attachment.id
                if invoice_type == 'import':
                    impsAttach = attachment[0]
                    impsJsonInvoiceData = attachment[1]
                    impgAttach = jsonInvoiceData[0]
                    impgJsonInvoiceData = jsonInvoiceData[1]
                    jsonData.update({'imp_s': impsJsonInvoiceData,
                                    'imp_g': impgJsonInvoiceData})
                    if impsAttach:
                        self.imps_attachment = impsAttach.id
                    if impgAttach:
                        self.impg_attachment = impgAttach.id
                if invoice_type == 'export':
                    jsonData.update({'exp': {'exp_typ': 'WOPAY',
                                    'inv': jsonInvoiceData}})
                    self.export_attachment = attachment.id
                if invoice_type == 'cdnr':
                    jsonData.update({invoice_type: jsonInvoiceData})
                    self.cdnr_attachment = attachment.id
                if invoice_type == 'cdnur':
                    jsonData.update({invoice_type: jsonInvoiceData})
                    self.cdnur_attachment = attachment.id

            if not self.hsn_attachment:
                respHsnData = self.exportCsv(invoiceIds, 'hsn', name,
                        gstType)
                if respHsnData:
                    hsnAttachment = respHsnData[0]
                    jsonInvoiceData = respHsnData[1]
                    jsonData.update({'hsn': {'data': jsonInvoiceData}})
                    if hsnAttachment:
                        self.hsn_attachment = hsnAttachment.id
                        self.status = 'ready_to_upload'
            if not self.json_attachment:
                if jsonData:
                    jsonData = json.dumps(jsonData, indent=4, sort_keys=False)
                    base64Data = base64.b64encode(jsonData.encode('utf-8'))
                    jsonAttachment = False
                    try:
                        jsonFileName = "{}.json".format(name)
                        jsonAttachment = self.env['ir.attachment'].create({
                            'datas': base64Data,
                            'type': 'binary',
                            'res_model': 'gstr1.tool',
                            'res_id': self.id,
                            'db_datas': jsonFileName,
                            'store_fname': jsonFileName,
                            'name': jsonFileName,
                            })
                    except ValueError:
                        return jsonAttachment
                    if jsonAttachment:
                        self.json_attachment = jsonAttachment.id
        message = "Your gst & hsn csv are successfully generated"
        partial = self.env['message.wizard'].create({'text': message})
        return {
            'name': ("Information"),
            'view_mode': 'form',
            'res_model': 'message.wizard',
            'view_id': self.env.ref('gst_invoice.message_wizard_form1').id,
            'res_id': partial.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }

    def getTypeList(self):
        typeList = []
        for gst_type in GSTTypeList:
            attachment = getattr(self, '%s_attachment' % gst_type)
            if attachment:
                typeList.append(gst_type)
        return typeList

    def export_gst_attachment(self):
        if self._context.get('export_type'):
            export_type = self._context.get('export_type')
            if hasattr(self, '%s' % export_type):
                attachment = getattr(self, '%s' % export_type)
                if not attachment:
                    self.generateCsv()
                attachment = getattr(self, '%s' % export_type)
                if not attachment:
                    raise UserError("CSV of %s invoice is not present"%((export_type.split('_')[0])).upper())
                return {'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=1'% attachment.id, 'target': 'new'}

    def uploadGST(self):
        partial = self.env['message.wizard'].create(
            {'text': 'GST Invoice is successfully uploaded'})
        self.status = 'uploaded'
        self.updateInvoiceStatus('uploaded')
        return {
            'name': ("Information"),
            'view_mode': 'form',
            'res_model': 'message.wizard',
            'view_id': self.env.ref('gst_invoice.message_wizard_form1').id,
            'res_id': partial.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }

    def filedGST(self):
        partial = self.env['message.wizard'].create(
            {'text': 'GST Invoice is successfully Filed'})
        self.status = 'filed'
        self.updateInvoiceStatus('filed')
        return {
            'name': ("Information"),
            'view_mode': 'form',
            'res_model': 'message.wizard',
            'view_id': self.env.ref('gst_invoice.message_wizard_form1').id,
            'res_id': partial.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
        }

    def updateInvoiceStatus(self, status):
        self.invoice_lines.write({'gst_status': status})
        return True

    @api.model
    def exportCsv(self, active_ids, invoice_type, gstToolName, gstType):
        if invoice_type == 'import':
            impsData = self.getInvoiceData(active_ids, 'imps', gstType)
            mainData = impsData[0]
            impsAttachment = self.prepareCsv(mainData, 'imps', gstToolName, gstType)
            impsJsonData = impsData[1]
            impgData = self.getInvoiceData(active_ids, 'impg', gstType)
            mainData = impgData[0]
            impgAttachment = self.prepareCsv(mainData, 'impg', gstToolName, gstType)
            impgJsonData = impgData[1]
            return [[impsAttachment, impsJsonData], [impgAttachment, impgJsonData]]
        respData = self.getInvoiceData(active_ids, invoice_type, gstType)
        mainData = respData[0]
        jsonData = respData[1]
        attachment = self.prepareCsv(mainData, invoice_type, gstToolName, gstType)
        return [attachment, jsonData]

    def prepareCsv(self, mainData, invoice_type, gstToolName, gstType):
        attachment = False
        if mainData:
            fp = io.StringIO()
            writer = csv.writer(fp, quoting=csv.QUOTE_NONE, escapechar='\\')
            if invoice_type in ['b2b','cdnr', 'cdnur']:
                columns = GSTTYPECOLUMN.get('%s_%s'%(invoice_type,gstType))
                writer.writerow(columns)
            else:
                columns = GSTTYPECOLUMN.get(invoice_type)
            for lineData in mainData:
                writer.writerow([_unescape(name) for name in lineData])
            fp.seek(0)
            data = fp.read()
            fp.close()
            attachment = self.generateAttachment(
                data, invoice_type, gstToolName)
        return attachment

    def generateAttachment(self, data, invoice_type, gstToolName):
        attachment = False
        base64Data = base64.b64encode(data.encode('utf-8'))
        store_fname = '{}_{}.csv'.format(invoice_type, gstToolName)
        try:
            attachment = self.env['ir.attachment'].create({
                'datas': base64Data,
                'type': 'binary',
                'res_model': 'gstr1.tool',
                'res_id': self.id,
                'db_datas': store_fname,
                'store_fname': store_fname,
                'name': store_fname
            })
        except ValueError:
            return attachment
        return attachment

    def getInvoiceData(self, active_ids, invoiceType, gstType):
        mainData ,jsonData = [] , []
        count = 0
        b2csDataDict, b2csJsonDataDict, b2clJsonDataDict, b2burDataDict, b2bDataDict, cdnrDataDict, hsnDict, hsnDataDict = {} ,{}, {}, {}, {}, {}, {}, {}
        cdnurDataDict = {'cdnur': []}
        reverseChargeMain = self.reverse_charge and 'Y' or 'N'
        counterFilingStatus = self.counter_filing_status and 'Y' or 'N'
        gstcompany_id = self.company_id or self.env.company
        invoiceObjs = self.env['account.move'].browse(active_ids)
        for invoiceObj in invoiceObjs:
            invData = {}
            reverseCharge = 'Y' if invoiceObj.reverse_charge else 'N' if reverseChargeMain == 'N' else reverseChargeMain
            invType = invoiceObj.export_type or 'regular'
            invType_val = dict(invoiceObj._fields['export_type'].selection).get(
                invoiceObj.export_type)
            jsonInvType = 'R'
            if invType == 'sez_with_payment':
                jsonInvType = 'SEWP'
            elif invType == 'sez_without_payment':
                jsonInvType = 'SEWOP'
            elif invType == 'deemed':
                jsonInvType = 'DE'
            elif invType == 'intra_state_igst':
                jsonInvType = 'CBW'
            currency = invoiceObj.currency_id
            invoiceNumber = invoiceObj.name or ''
            if gstType == 'gstr2':
                invoiceNumber = invoiceObj.ref or ''
                if invoiceType == 'cdnr':
                    invoiceNumber = invoiceObj.name or ''
            if len(invoiceNumber) > 16:
                invoiceNumber = invoiceNumber[-16:]
            invoiceDate = invoiceObj.move_type in [
                'out_invoice', 'out_refund'] and invoiceObj.date or invoiceObj.invoice_date
            invoiceJsonDate = invoiceDate.strftime('%d-%m-%Y')
            invoiceDate = invoiceDate.strftime('%d-%b-%Y')
            originalInvNumber, originalInvDate, originalInvJsonDate = '', '', ''
            originalInvObj = invoiceObj.reversed_entry_id
            if originalInvObj:
                originalInvNumber = originalInvObj.name or ''
                if gstType == 'gstr2':
                    originalInvNumber = originalInvObj.ref or ''
                if len(originalInvNumber) > 16:
                    originalInvNumber = originalInvNumber[-16:]
                originalInvDate = originalInvObj.move_type in [
                    'out_invoice', 'out_refund'] and originalInvObj.date or originalInvObj.invoice_date
                originalInvJsonDate = originalInvDate.strftime('%d-%b-%Y')
                originalInvDate = originalInvDate.strftime('%d-%m-%Y')
            invoiceTotal = invoiceObj.amount_total
            if currency.name != 'INR':
                invoiceTotal = invoiceTotal * currency.rate
            invoiceObj.inr_total = invoiceTotal
            invoiceTotal = round(invoiceTotal, 2)
            state = invoiceObj.partner_id.state_id
            code = _unescape(state.l10n_in_tin) or 0
            sname = _unescape(state.name)
            stateName = "{}-{}".format(code, sname)
            data = []
            if invoiceType == 'b2b':
                customerName = invoiceObj.partner_id.name
                invData = {
                    "inum": invoiceNumber,
                    "idt": invoiceDate,
                    "val": invoiceTotal,
                    "pos": code,
                    "rchrg": reverseCharge,
                    "inv_typ": jsonInvType
                }
                # if gstType == 'gstr1':
                #     invData['etin'] = ""
                #     invData['diff_percent'] = 0.0
                gstrData = [invoiceObj.l10n_in_gstin, invoiceNumber, invoiceDate,
                            invoiceTotal, stateName, reverseCharge, invType_val]
                if gstType == 'gstr1':
                    gstrData = [invoiceObj.l10n_in_gstin, customerName, invoiceNumber,
                                invoiceDate, invoiceTotal, stateName, reverseCharge, 0.0, invType_val, '']
                data.extend(gstrData)
                respData = self.getGSTInvoiceData(
                    invoiceObj, invoiceType, data, gstType)
                data = respData[0]
                invData['itms'] = respData[1]
                invData['idt'] = invoiceJsonDate
                if b2bDataDict.get(invoiceObj.l10n_in_gstin):
                    b2bDataDict[invoiceObj.l10n_in_gstin].append(invData)
                else:
                    b2bDataDict[invoiceObj.l10n_in_gstin] = [invData]
            elif invoiceType == 'b2bur':
                sply_ty = 'INTER'
                sply_type = 'Inter State'
                if invoiceObj.partner_id.state_id.code != gstcompany_id.state_id.code:
                    sply_ty = 'INTRA'
                    sply_type = 'Intra State'
                invData = {
                    "inum": invoiceNumber,
                    "idt": invoiceDate,
                    "val": invoiceTotal,
                    "pos": code,
                    "sply_ty": sply_ty
                }
                supplierName = invoiceObj.partner_id.name
                data.extend([supplierName, invoiceNumber,
                             invoiceDate, invoiceTotal, stateName, sply_type])
                respData = self.getGSTInvoiceData(
                    invoiceObj, invoiceType, data, gstType)
                data = respData[0]
                invData['itms'] = respData[1]
                invData['idt'] = invoiceJsonDate
                if b2burDataDict.get(supplierName):
                    b2burDataDict[supplierName].append(invData)
                else:
                    b2burDataDict[supplierName] = [invData]
            elif invoiceType == 'b2cl':
                invData = {
                    "inum": invoiceNumber,
                    "idt": invoiceDate,
                    "val": invoiceTotal,
                    # "etin": "",
                }
                # invData['diff_percent'] = 0.0
                data.extend([invoiceNumber, invoiceDate,
                             invoiceTotal, stateName, 0.0])
                respData = self.getGSTInvoiceData(
                    invoiceObj, invoiceType, data, gstType)
                data = respData[0]
                invData['itms'] = respData[1]
                invData['idt'] = invoiceJsonDate
                if b2clJsonDataDict.get(code):
                    b2clJsonDataDict[code].append(invData)
                else:
                    b2clJsonDataDict[code] = [invData]
            elif invoiceType == 'b2cs':
                invData = {'pos': code}
                b2bData = ['OE', stateName]
                respData = self.getGSTInvoiceData(invoiceObj,
                        invoiceType, b2bData, gstType)
                b2bData = respData[0]
                rateDataDict = respData[2]
                rateJsonDict = respData[3]
                if b2csDataDict.get(stateName):
                    for key in rateDataDict.keys():
                        if b2csDataDict.get(stateName).get(key):
                            for key1 in rateDataDict.get(key).keys():
                                if key1 in ['rt']:
                                    continue
                                if b2csDataDict.get(stateName).get(key).get(key1):
                                    b2csDataDict.get(stateName).get(key)[key1] = b2csDataDict.get(
                                        stateName).get(key)[key1] + rateDataDict.get(key)[key1]
                                else:
                                    b2csDataDict.get(stateName).get(
                                        key)[key1] = rateDataDict.get(key)[key1]
                        else:
                            b2csDataDict.get(stateName)[
                                key] = rateDataDict[key]
                else:
                    b2csDataDict[stateName] = rateDataDict
                if b2csJsonDataDict.get(code):
                    for key in rateJsonDict.keys():
                        if b2csJsonDataDict.get(code).get(key):
                            for key1 in rateJsonDict.get(key).keys():
                                if b2csJsonDataDict.get(code).get(key).get(key1):
                                    if key1 in ['rt', 'sply_ty', 'typ']:
                                        continue
                                    b2csJsonDataDict.get(code).get(key)[key1] = b2csJsonDataDict.get(
                                        code).get(key)[key1] + rateJsonDict.get(key)[key1]
                                    b2csJsonDataDict.get(code).get(key)[key1] = round(
                                        b2csJsonDataDict.get(code).get(key)[key1], 2)
                                else:
                                    b2csJsonDataDict.get(code).get(
                                        key)[key1] = rateJsonDict.get(key)[key1]
                        else:
                            b2csJsonDataDict.get(code)[key] = rateJsonDict[key]
                else:
                    b2csJsonDataDict[code] = rateJsonDict
                if respData[1]:
                    invData.update(respData[1][0])
            elif invoiceType == 'imps':
                state = self.env.company.state_id
                code = _unescape(state.l10n_in_tin) or 0
                sname = _unescape(state.name)
                stateName = "{}-{}".format(code, sname)
                invData = {
                    "inum": invoiceNumber,
                    "idt": invoiceDate,
                    "ival": invoiceTotal,
                    "pos": code
                }
                supplierName = invoiceObj.partner_id.name
                data.extend([invoiceNumber, invoiceDate,
                             invoiceTotal, stateName])
                respData = self.getGSTInvoiceData(
                    invoiceObj, invoiceType, data, gstType)
                data = respData[0]
                invData['itms'] = respData[1]
                invData['idt'] = invoiceJsonDate
                jsonData.append(invData)
            elif invoiceType == 'impg':
                companyGST = self.env.company.vat
                portcode = ''
                if invoiceObj.l10n_in_shipping_port_code_id:
                    portcode = invoiceObj.l10n_in_shipping_port_code_id.name
                invData = {
                    "boe_num": invoiceNumber,
                    "boe_dt": invoiceJsonDate,
                    "boe_val": invoiceTotal,
                    "port_code": portcode,
                    "stin": companyGST,
                    'is_sez': 'Y'
                }
                supplierName = invoiceObj.partner_id.name
                data.extend([portcode, invoiceNumber, invoiceDate,
                             invoiceTotal, 'Imports', companyGST])
                respData = self.getGSTInvoiceData(
                    invoiceObj, invoiceType, data, gstType)
                data = respData[0]
                invData['itms'] = respData[1]
                jsonData.append(invData)
            elif invoiceType == 'export':
                portcode = ''
                if invoiceObj.l10n_in_shipping_port_code_id:
                    portcode = invoiceObj.l10n_in_shipping_port_code_id.name
                shipping_bill_number = invoiceObj.l10n_in_shipping_bill_number or ''
                shipping_bill_date = invoiceObj.l10n_in_shipping_bill_date and invoiceObj.l10n_in_shipping_bill_date.strftime(
                    '%d-%m-%Y') or ''
                invData = {
                    "inum": invoiceNumber,
                    "idt": invoiceDate,
                    "val": invoiceTotal,
                    "sbpcode": portcode,
                    "sbnum": shipping_bill_number,
                    "sbdt": shipping_bill_date,
                }
                # invData['diff_percent'] = 0.0
                data.extend([
                    invoiceObj.export, invoiceNumber, invoiceDate,
                    invoiceTotal, portcode, shipping_bill_number,
                    shipping_bill_date, 0.0
                ])
                respData = self.getGSTInvoiceData(
                    invoiceObj, invoiceType, data, gstType)
                data = respData[0]
                invData['itms'] = respData[1]
                invData['idt'] = invoiceJsonDate
                jsonData.append(invData)
            elif invoiceType in ['cdnr', 'cdnur']:
                customerName = invoiceObj.partner_id.name
                pre_gst = 'N'
                if invoiceObj.pre_gst:
                    pre_gst = 'Y'
                invoiceObjRef = invoiceObj.ref or ''
                reasonList = invoiceObjRef.split(',')
                reasonNote = reasonList[1].strip() if len(
                    reasonList) > 1 else invoiceObjRef
                sply_ty = 'INTER'
                sply_type = 'Inter State'
                if invoiceObj.partner_id.state_id.code != gstcompany_id.state_id.code:
                    sply_ty = 'INTRA'
                    sply_type = 'Intra State'
                invData = {
                    "nt_num": invoiceNumber,
                    "nt_dt": invoiceJsonDate,
                    "ntty": "C",
                    "val": invoiceTotal,
                    "pos": code,
                }
                if invoiceType == 'cdnr':
                    invData.update({
                        "rchrg": reverseCharge,
                        "inv_typ": jsonInvType,
                    })
                    if gstType == 'gstr2':
                        invData['ntty'] = "D"
                    gstrData = [invoiceObj.l10n_in_gstin, invoiceNumber, invoiceDate, originalInvNumber,
                                originalInvJsonDate, reverseCharge, 'D', reasonNote, sply_type, invoiceTotal]
                    if gstType == 'gstr1':
                        gstrData = [invoiceObj.l10n_in_gstin, customerName, invoiceNumber,
                                    invoiceDate, 'C', stateName, reverseCharge, invType_val, invoiceTotal, 0.0]
                else:
                    ur_type = 'B2CL'
                    gstrData = [ur_type, invoiceNumber, invoiceDate,
                                'C', stateName, invoiceTotal, 0.0]
                data.extend(gstrData)
                respData = self.getGSTInvoiceData(
                    invoiceObj, invoiceType, data, gstType)
                data = respData[0]
                invData['itms'] = respData[1]
                if invoiceType == 'cdnr':
                    if cdnrDataDict.get(invoiceObj.l10n_in_gstin):
                        cdnrDataDict[invoiceObj.l10n_in_gstin].append(invData)
                    else:
                        cdnrDataDict[invoiceObj.l10n_in_gstin] = [invData]
                else:
                    cdnurDataDict['cdnur'].append(invData)
            elif invoiceType == 'hsn':
                respData = self.getHSNData(
                    invoiceObj, count, hsnDict, hsnDataDict)
                data = respData[0]
                jsonData.extend(respData[1])
                hsnDict = respData[2]
                hsnDataDict = respData[3]
                invoiceObj.gst_status = 'ready_to_upload'
            if data:
                mainData.extend(data)

        if b2csJsonDataDict:
            for pos, val in b2csJsonDataDict.items():
                for line in val.values():
                    line['pos'] = pos
                    # line['diff_percent'] = 0.0
                    jsonData.append(line)
        if b2csDataDict:
            b2csData = []
            for state, data in b2csDataDict.items():
                for rate, val in data.items():
                    b2csData.append(['OE', state, 0.0, rate, round(
                        val['taxval'], 2), round(val['cess'], 2), ''])
            mainData = b2csData
        if b2bDataDict:
            for (ctin, inv) in b2bDataDict.items():
                jsonData.append({'ctin': ctin, 'inv': inv})  # 'cfs': counterFilingStatus,
        if b2burDataDict:
            for (ctin, inv) in b2burDataDict.items():
                jsonData.append({'inv': inv})
        if b2clJsonDataDict:
            for (pos, inv) in b2clJsonDataDict.items():
                jsonData.append({'pos': pos, 'inv': inv})
        if cdnrDataDict:
            for (ctin, nt) in cdnrDataDict.items():
                jsonData.append({'ctin': ctin, 'nt': nt})  # 'cfs': counterFilingStatus,
        if cdnurDataDict:
            if cdnurDataDict.get('cdnur'):
                jsonData = cdnurDataDict['cdnur']
        if hsnDict:
            vals = hsnDict.values()
            hsnMainData = []
            for val in vals:
                hsnMainData.extend(val.values())
            mainData = hsnMainData
        if hsnDataDict:
            vals = hsnDataDict.values()
            hsnMainData = []
            for val in vals:
                hsnMainData.extend(val.values())
            jsonData = hsnMainData
        return [mainData, jsonData]

    def getGSTInvoiceData(self, invoiceObj, invoiceType, data, gstType=''):
        jsonItemData = []
        count = 0
        rateDataDict = {}
        rateDict = {}
        rateJsonDict = {}
        itcEligibility = 'Ineligible'
        ctx = dict(self._context or {})
        if gstType == 'gstr2':
            itcEligibility = self.itc_eligibility
            if itcEligibility == 'Ineligible':
                itcEligibility = invoiceObj.itc_eligibility
        for invoiceLineObj in invoiceObj.invoice_line_ids.filtered(lambda l: l.product_id):
            if invoiceLineObj.product_id:
                if invoiceLineObj.product_id.type == 'service':
                    if invoiceType == 'impg':
                        continue
                else:
                    if invoiceType == 'imps':
                        continue
            else:
                if invoiceType == 'impg':
                    continue
            invoiceLineData = self.getInvoiceLineData(data, invoiceLineObj, invoiceObj, invoiceType)
            if invoiceLineData:
                rate = invoiceLineData[2]
                rateAmount = invoiceLineData[3]
                if invoiceLineData[1]:
                    invoiceLineData[1]['txval'] = rateAmount
                if gstType == 'gstr2':
                    igst = invoiceLineData[1].get('iamt') or 0.0
                    cgst = invoiceLineData[1].get('camt') or 0.0
                    sgst = invoiceLineData[1].get('samt') or 0.0
                    if rate not in rateDict.keys():
                        rateDataDict[rate] = {
                            'rt': rate,
                            'taxval': rateAmount,
                            'igst': igst,
                            'cgst': cgst,
                            'sgst': sgst,
                            'cess': 0.0
                        }
                    else:
                        rateDataDict[rate]['taxval'] = rateDataDict[rate]['taxval'] + rateAmount
                        rateDataDict[rate]['igst'] = rateDataDict[rate]['igst'] + igst
                        rateDataDict[rate]['cgst'] = rateDataDict[rate]['cgst'] + cgst
                        rateDataDict[rate]['sgst'] = rateDataDict[rate]['sgst'] + sgst
                        rateDataDict[rate]['cess'] = rateDataDict[rate]['cess'] + 0.0
                if gstType == 'gstr1':
                    if rate not in rateDict.keys():
                        rateDataDict[rate] = {
                            'rt': rate,
                            'taxval': rateAmount,
                            'cess': 0.0
                        }
                    else:
                        rateDataDict[rate]['taxval'] = rateDataDict[rate]['taxval'] + rateAmount
                        rateDataDict[rate]['cess'] = rateDataDict[rate]['cess'] + 0.0
                if rate not in rateJsonDict.keys():
                    rateJsonDict[rate] = invoiceLineData[1]
                else:
                    for key in invoiceLineData[1].keys():
                        if key in ['rt', 'sply_ty', 'typ', 'elg']:
                            continue
                        if rateJsonDict[rate].get(key):
                            rateJsonDict[rate][key] = rateJsonDict[rate][key] + invoiceLineData[1][key]
                            rateJsonDict[rate][key] = round(rateJsonDict[rate][key], 2)
                        else:
                            rateJsonDict[rate][key] = invoiceLineData[1][key]
                invData = []
                if gstType == 'gstr1':
                    invData = invoiceLineData[0] + [rateDataDict[rate]['taxval']]
                if gstType == 'gstr2':
                    if invoiceType in ['imps', 'impg']:
                        invData = invoiceLineData[0] + [
                            rateDataDict[rate]['taxval'],
                            rateDataDict[rate]['igst']
                        ]
                    else:
                        invData = invoiceLineData[0] + [
                            rateDataDict[rate]['taxval'],
                            rateDataDict[rate]['igst'],
                            rateDataDict[rate]['cgst'],
                            rateDataDict[rate]['sgst']
                        ]
                if invoiceType in ['b2b', 'cdnr']:
                    if gstType == 'gstr1':
                        invData = invData + [0.0]
                    if gstType == 'gstr2':
                        if itcEligibility != 'Ineligible':
                            invData = invData + [0.0] + [itcEligibility] + [
                                rateDataDict[rate]['igst']
                            ] + [rateDataDict[rate]['cgst']] + [
                                rateDataDict[rate]['sgst']
                            ] + [rateDataDict[rate]['cess']]
                        else:
                            invData = invData + [0.0] + [itcEligibility] + [0.0] * 4

                elif invoiceType == 'b2bur':
                    if itcEligibility != 'Ineligible':
                        invData = invData + [0.0] + [itcEligibility] + [
                            rateDataDict[rate]['igst']
                        ] + [rateDataDict[rate]['cgst']] + [
                            rateDataDict[rate]['sgst']
                        ] + [rateDataDict[rate]['cess']]
                    else:
                        invData = invData + [0.0] + [itcEligibility] + [0.0] * 4
                elif invoiceType in ['imps', 'impg']:
                    if itcEligibility != 'Ineligible':
                        invData = invData + [0.0] + [itcEligibility] + [
                            rateDataDict[rate]['igst']
                        ] + [rateDataDict[rate]['cess']]
                    else:
                        invData = invData + [0.0] + [itcEligibility] + [0.0] + [0.0]
                elif invoiceType in ['b2cs', 'b2cl']:
                    invData = invData + [0.0, '']
                    # if invoiceType == 'b2cl':
                    #     bonded_wh = 'Y' if invoiceObj.export_type == 'sale_from_bonded_wh' else 'N'
                    #     invData = invData + [bonded_wh]
                rateDict[rate] = invData
        mainData = rateDict.values()
        if rateJsonDict:
            for jsonData in rateJsonDict.values():
                count = count + 1
                if invoiceType in ['b2b', 'b2bur', 'cdnr'] and gstType == 'gstr2':
                    jsonItemData.append({
                        "num": count,
                        'itm_det': jsonData,
                        "itc": {
                            "elg": "no",
                            "tx_i": 0.0,
                            "tx_s": 0.0,
                            "tx_c": 0.0,
                            "tx_cs": 0.0
                        }
                    })
                elif invoiceType in ['imps', 'impg']:
                    jsonItemData.append({
                        "num": count,
                        'itm_det': jsonData,
                        "itc": {
                            "elg": "no",
                            "tx_i": 0.0,
                            "tx_cs": 0.0
                        }
                    })
                else:
                    jsonItemData.append({"num": count, 'itm_det': jsonData})
        return [mainData, jsonItemData, rateDataDict, rateJsonDict]

    def getInvoiceLineData(self, invoiceLineData, invoiceLineObj, invoiceObj, invoiceType):
        lineData = []
        jsonLineData = {}
        taxedAmount = 0.0
        rate = 0.0
        rateAmount = 0.0
        currency = invoiceObj.currency_id or None
        price = invoiceLineObj.price_subtotal / invoiceLineObj.quantity if invoiceLineObj.quantity > 0 else 0.0
        rateObjs = invoiceLineObj.tax_ids
        if rateObjs:
            for rateObj in rateObjs:
                if rateObj.amount_type == "group":
                    for childObj in rateObj.children_tax_ids:
                        rate = childObj.amount * 2
                        lineData.append(rate)
                        break
                else:
                    rate = rateObj.amount
                    lineData.append(rate)
                break
            taxData = self.getTaxedAmount(
                rateObjs, price, currency, invoiceLineObj, invoiceObj)
            rateAmount = taxData[1]
            rateAmount = round(rateAmount, 2)
            taxedAmount = taxData[0]
            jsonLineData = self.getGstTaxData(invoiceObj,
                    invoiceLineObj, rateObjs, taxedAmount, invoiceType)
        else:
            rateAmount = invoiceLineObj.price_subtotal
            rateAmount = rateAmount
            if currency.name != 'INR':
                rateAmount = rateAmount * currency.rate
            rateAmount = round(rateAmount, 2)
            lineData.append(0)
            jsonLineData = self.getGstTaxData(invoiceObj,
                    invoiceLineObj, False, taxedAmount, invoiceType)
        data = invoiceLineData + lineData
        return [data, jsonLineData, rate, rateAmount]

    def getHSNData(self, invoiceObj, count, hsnDict={}, hsnDataDict={}):
        mainData = []
        jsonData = []
        currency = invoiceObj.currency_id or None
        ctx = dict(self._context or {})
        sign = -1 if invoiceObj.move_type in ('out_refund', 'in_refund') else 1
        for invoiceLineObj in invoiceObj.invoice_line_ids.filtered(lambda l: l.product_id):
            quantity = invoiceLineObj.quantity or 1.0
            price = invoiceLineObj.price_subtotal / quantity
            taxedAmount, cgst, sgst, igst, rt = 0.0, 0.0, 0.0, 0.0, 0
            rateObjs = invoiceLineObj.tax_ids
            if rateObjs:
                taxData = self.getTaxedAmount(
                    rateObjs, price, currency, invoiceLineObj, invoiceObj)
                rateAmount = taxData[1]
                taxedAmount = taxData[0]
                if currency.name != 'INR':
                    taxedAmount = taxedAmount * currency.rate
                taxedAmount = round(taxedAmount, 2)
                # if invoiceObj.partner_id.country_id.code == 'IN':
                rateObj = rateObjs[0]
                if rateObj.amount_type == "group":
                    rt = rateObj.children_tax_ids and rateObj.children_tax_ids[0].amount * 2 or 0
                    cgst, sgst = round(taxedAmount / 2, 2), round(taxedAmount / 2, 2)
                else:
                    rt = rateObj.amount
                    igst = round(taxedAmount, 2)
            invUntaxedAmount = round(invoiceLineObj.price_subtotal, 2)
            if currency.name != 'INR':
                invUntaxedAmount = round(invoiceLineObj.price_subtotal * currency.rate, 2)
            productObj = invoiceLineObj.product_id
            hsnvalue = productObj.l10n_in_hsn_code or ''
            hsnVal = hsnvalue.replace('.', '') or 'False'
            hsnName = '' # productObj.name or 'name'
            uqc = 'OTH'
            if productObj.uom_id:
                uom = productObj.uom_id.id
                uqcObj = self.env['uom.mapping'].search([('uom', '=', uom)])
                if uqcObj:
                    uqc = uqcObj[0].name.code
            hsnTuple = (uqc, rt)
            invQty = sign * invoiceLineObj.quantity
            invAmountTotal = sign * (invUntaxedAmount + taxedAmount)
            invUntaxedAmount *= sign
            igst *= sign
            cgst *= sign
            sgst *= sign
            if hsnDataDict.get(hsnVal):
                hsnTupleDict = hsnDataDict.get(hsnVal).get(hsnTuple) or {}
                if hsnTupleDict:
                    if hsnTupleDict.get('qty'):
                        invQty += hsnTupleDict.get('qty')
                        hsnTupleDict['qty'] = invQty
                    else:
                        hsnTupleDict['qty'] = invQty
                    # if hsnTupleDict.get('val'):
                    #     invAmountTotal = round(hsnTupleDict.get('val') + invAmountTotal, 2)
                    #     hsnTupleDict['val'] = invAmountTotal
                    # else:
                    #     invAmountTotal = round(invAmountTotal, 2)
                    #     hsnTupleDict['val'] = invAmountTotal
                    if hsnTupleDict.get('txval'):
                        invUntaxedAmount = round(hsnTupleDict.get('txval') + invUntaxedAmount, 2)
                        hsnTupleDict['txval'] = invUntaxedAmount
                    else:
                        invUntaxedAmount = round(invUntaxedAmount, 2)
                        hsnTupleDict['txval'] = invUntaxedAmount
                    if hsnTupleDict.get('iamt'):
                        igst = round(hsnTupleDict.get('iamt') + igst, 2)
                        hsnTupleDict['iamt'] = igst
                    else:
                        igst = round(igst, 2)
                        hsnTupleDict['iamt'] = igst
                    if hsnTupleDict.get('camt'):
                        cgst = round(hsnTupleDict.get('camt') + cgst, 2)
                        hsnTupleDict['camt'] = cgst
                    else:
                        cgst = round(cgst, 2)
                        hsnTupleDict['camt'] = cgst
                    if hsnTupleDict.get('samt'):
                        sgst = round(hsnTupleDict.get('samt') + sgst, 2)
                        hsnTupleDict['samt'] = sgst
                    else:
                        sgst = round(sgst, 2)
                        hsnTupleDict['samt'] = sgst
                else:
                    count += 1
                    hsnDataDict.get(hsnVal)[hsnTuple] = {
                        'num': count,
                        'hsn_sc': hsnVal,
                        'desc': hsnName,
                        'uqc': uqc,
                        'qty': invQty,
                        # 'val': invAmountTotal,
                        'rt': rt,
                        'txval': invUntaxedAmount,
                        'iamt': igst,
                        'camt': cgst,
                        'samt': sgst,
                        'csamt': 0.0
                    }
            else:
                count += 1
                hsnDataDict[hsnVal] = {
                    hsnTuple: {
                        'num': count,
                        'hsn_sc': hsnVal,
                        'desc': hsnName,
                        'uqc': uqc,
                        'qty': invQty,
                        # 'val': invAmountTotal,
                        'rt': rt,
                        'txval': invUntaxedAmount,
                        'iamt': igst,
                        'camt': cgst,
                        'samt': sgst,
                        'csamt': 0.0
                    }
                }
            hsnvalue = productObj.l10n_in_hsn_code or ''
            hsnData = [
                hsnvalue.replace('.', ''), hsnName, uqc, invQty,
                invAmountTotal, rt, invUntaxedAmount, igst, cgst, sgst, 0.0
            ]
            if hsnDict.get(hsnVal):
                hsnDict.get(hsnVal)[hsnTuple] = hsnData
            else:
                hsnDict[hsnVal] = {hsnTuple: hsnData}
            mainData.append(hsnData)
        return [mainData, jsonData, hsnDict, hsnDataDict]

    def getTaxedAmount(self, rateObjs, price, currency, invoiceLineObj, invoiceObj):
        taxedAmount = 0.0
        total_excluded = 0.0
        taxes = rateObjs.compute_all(price, currency, invoiceLineObj.quantity,
                                     product=invoiceLineObj.product_id, partner=invoiceObj.partner_id)
        if taxes:
            total_included = taxes.get('total_included') or 0.0
            total_excluded = taxes.get('total_excluded') or 0.0
            taxedAmount = total_included - total_excluded
        if currency.name != 'INR':
            taxedAmount = taxedAmount * currency.rate
            total_excluded = total_excluded * currency.rate
        return [taxedAmount, total_excluded]

    def getGstTaxData(self, invoiceObj, invoiceLineObj, rateObjs, taxedAmount, invoiceType):
        taxedAmount = round(taxedAmount, 2)
        gstDict = {
            "rt": 0.0,
            "iamt": 0.0,
            "camt": 0.0,
            "samt": 0.0,
            "csamt": 0.0
        }
        if invoiceType == "export":
            gstDict = {"txval": 0.0, "rt": 0, "iamt": 0.0}
        if invoiceType in ['imps', 'impg']:
            gstDict = {
                "elg": "no",
                "txval": 0.0,
                "rt": 0,
                "iamt": 0.0,
                'tx_i': 0.0,
                'tx_cs': 0.0
            }
        if invoiceType == "b2cs":
            gstDict['sply_ty'] = 'INTRA'
            gstDict['typ'] = 'OE'
        if rateObjs:
            rateObj = rateObjs[0]
            if invoiceObj.partner_id.country_id.code == 'IN':
                if rateObj.amount_type == "group":
                    gstDict['rt'] = rateObj.children_tax_ids and rateObj.children_tax_ids[0].amount * 2 or 0
                    gstDict['samt'] = round(taxedAmount / 2, 2)
                    gstDict['camt'] = round(taxedAmount / 2, 2)
                else:
                    gstDict['rt'] = rateObj.amount
                    gstDict['iamt'] = round(taxedAmount, 2)
            elif invoiceType in ['imps', 'impg']:
                gstDict['rt'] = rateObj.amount
                gstDict['iamt'] = round(taxedAmount, 2)
        return gstDict
