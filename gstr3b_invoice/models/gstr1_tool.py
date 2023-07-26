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
from odoo.addons.gstr3b_invoice.models.gst_columns import GSTR3BCOLUMN

def _unescape(text):
    try:
        text = unquote_plus(text.encode('utf8'))
        return text
    except Exception as e:
        return text

KEYS = ('txval', 'iamt', 'camt', 'samt', 'csamt')


class Gstr1Tool(models.Model):
    _inherit = "gstr1.tool"

    def _get_gst_type(self):
        res = super(Gstr1Tool, self)._get_gst_type()
        res.append(('gstr3b', 'GSTR3B'))
        return res

    @api.onchange('period_id', 'date_from', 'date_to')
    def _compute_invoice_lines(self):
        if self.gst_type != 'gstr3b':
            return super(Gstr1Tool, self)._compute_invoice_lines()
        domain = {}
        filter = []
        ctx = dict(self._context or {})
        invoiceObjs = []
        if ctx.get('current_id'):
            filter.append(('id', '!=', ctx.get('current_id')))
        invoiceType = ['in_invoice', 'out_invoice']
        invoiceObjs = self.getInvoiceObjs(filter, invoiceType)
        if invoiceObjs:
            self.updateGSTInvoiceLines(invoiceObjs)
            domain['invoice_lines'] = [('id', 'in', invoiceObjs.ids)]
        else:
            domain['invoice_lines'] = [('id', 'in', [])]
        return {'domain': domain}

    def fetchAllInvoices(self):
        ctx = dict(self._context or {})
        filter = [('id', '!=', self.id)]
        invoiceObjs = self.with_context(ctx).getInvoiceObjs(filter, ['in_invoice', 'out_invoice'])
        self.invoice_lines = [(6, 0, invoiceObjs.ids)]
        if invoiceObjs:
            self.updateInvoiceCurrencyRate(invoiceObjs)
            self.updateGSTInvoiceLines(invoiceObjs)
        return True

    def getInvoiceObjs(self, extrafilter=[], invoiceType=[]):
        if self.gst_type != 'gstr3b':
            extrafilter.append(('gst_type', '!=', 'gstr3b'))
            return super(Gstr1Tool, self).getInvoiceObjs(extrafilter=extrafilter,
                                                         invoiceType=invoiceType)
        invoiceObjs = []
        extrafilter.append(('gst_type', '=', 'gstr3b'))
        gstObjs = self.search(extrafilter)
        invoiceIds = gstObjs and gstObjs.mapped(
            'invoice_lines') and gstObjs.mapped('invoice_lines').ids or []
        if self.period_id:
            filter = [
                ('invoice_date', '>=', self.period_id.date_start),
                ('invoice_date', '<=', self.period_id.date_stop),
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
                    raise UserError("Date should belong to selected period")
                if self.date_from > self.date_to:
                    raise UserError("End date should greater than or equal to starting date")
                filter.append(('invoice_date', '>=', self.date_from))
                filter.append(('invoice_date', '<=', self.date_to))
            if invoiceIds:
                filter.append(('id', 'not in', invoiceIds))
            invoiceObjs = self.env['account.move'].search(filter)
        return invoiceObjs

    def reset(self):
        res = super(Gstr1Tool, self).reset()
        if self.gst_type == 'gstr3b':
            self.fetchAllInvoices()
        return res

    def generateJsonGstr3B(self):
        gstType = self.gst_type
        if gstType != 'gstr3b':
            return
        gstinCompany = self.env.company.vat
        ret_period = self.period_id.code
        if ret_period:
            ret_period = ret_period.replace('/', '')
        ctx = dict(self._context or {})
        name = self.name
        active_ids = self.invoice_lines.ids if self.invoice_lines else []
        respData = self.exportCsv(active_ids, '', name, gstType)
        attachments = respData[0]
        jsonData = respData[1]
        jsonData.update({
            "gstin": gstinCompany,
            "ret_period": ret_period,
        })
        for attachment in attachments:
            if attachment.get('GSTR3B_3_1') and not self.b2b_attachment:
                self.b2b_attachment = attachment.get('GSTR3B_3_1').id
            elif attachment.get('GSTR3B_3_2') and not self.b2cs_attachment:
                self.b2cs_attachment = attachment.get('GSTR3B_3_2').id
            elif attachment.get('GSTR3B_4') and not self.b2bur_attachment:
                self.b2bur_attachment = attachment.get('GSTR3B_4').id
            elif attachment.get('GSTR3B_5') and not self.b2cl_attachment:
                self.b2cl_attachment = attachment.get('GSTR3B_5').id
        if not self.json_attachment:
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
                    'name': jsonFileName
                })
            except ValueError:
                return jsonAttachment
            if jsonAttachment:
                self.status = 'ready_to_upload'
                self.json_attachment = jsonAttachment.id
        message = "Your GSTR3B Data are successfully generated"
        partial = self.env['message.wizard'].create({'text': message})
        return {
            'name': ("Information"),
            'view_mode': 'form',
            'res_model': 'message.wizard',
            'view_id': self.env.ref('gst_invoice.message_wizard_form1').id,
            'res_id': partial.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
        
    def export_gst_attachment(self):
        if self.gst_type != 'gstr3b':
            return super(Gstr1Tool, self).export_gst_attachment()
        if self._context.get('export_type'):
            export_type = self._context.get('export_type')
            if hasattr(self, '%s' % export_type):
                attachment = getattr(self, '%s' % export_type)
                if not attachment:
                    self.generateJsonGstr3B()
                attachment = getattr(self, '%s' % export_type)
                if not attachment:
                    raise UserError("CSV of %s invoice is not present"%((export_type.split('_')[0])).upper())
                return {'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=1'% attachment.id, 'target': 'new'}


    def updateInvoiceStatus(self, status):
        if self.gst_type != 'gstr3b':
            return super(Gstr1Tool, self).updateInvoiceStatus(status=status)
        return True

    @api.model
    def exportCsv(self, active_ids, invoice_type, gstToolName, gstType):
        if gstType != 'gstr3b':
            return super(Gstr1Tool,
                         self).exportCsv(active_ids=active_ids,
                                         invoice_type=invoice_type,
                                         gstToolName=gstToolName,
                                         gstType=gstType)
        respData = self.getInvoiceData(active_ids, invoice_type, gstType)
        jsonData = respData[1]
        types = ['GSTR3B_3_1', 'GSTR3B_3_2', 'GSTR3B_4', 'GSTR3B_5']
        attachments = []
        flag = 0
        for mainData in respData[0]:
            attachment = self.prepareCsv(mainData, types[flag], gstToolName, gstType)
            attachments.append({types[flag]: attachment})
            flag += 1
        return [attachments, jsonData]

    def prepareCsv(self, mainData, invoice_type, gstToolName, gstType):
        if gstType != 'gstr3b':
            return super(Gstr1Tool,
                         self).prepareCsv(mainData=mainData,
                                          invoice_type=invoice_type,
                                          gstToolName=gstToolName,
                                          gstType=gstType)
        attachment = False
        if mainData:
            fp = io.StringIO()
            writer = csv.writer(fp, quoting=csv.QUOTE_NONE, escapechar='\\')
            columns = GSTR3BCOLUMN.get(invoice_type)
            writer.writerow(columns)
            for lineData in mainData:
                writer.writerow([_unescape(name) for name in lineData])
            fp.seek(0)
            data = fp.read()
            fp.close()
            attachment = self.generateAttachment(data, invoice_type, gstToolName)
        return attachment

    def getInvoiceData(self, active_ids, invoiceType, gstType):
        if gstType != 'gstr3b':
            return super(Gstr1Tool,
                         self).getInvoiceData(active_ids=active_ids,
                                              invoiceType=invoiceType,
                                              gstType=gstType)
        jsonData = {}
        mainData = []
        if active_ids:
            invoiceObjs = self.env['account.move'].browse(active_ids)
            jsonData = self.getGstr3BJsonData()
            for invoiceObj in invoiceObjs:
                invoiceType = invoiceObj.invoice_type
                jsonData = self.getGSTInvoiceData(
                    invoiceObj, invoiceType, jsonData, gstType)
            lineData = []
            rows = ['osup_det', 'osup_zero', 'osup_nil_exmp', 'isup_rev', 'osup_nongst']
            cols = ['txval', 'iamt', 'camt', 'samt', 'csamt']
            vals = [
                '(a) Outward Taxable supplies(other than zero/nil/exempted)',
                '(b) Outward Taxable supplies(zero rated)',
                '(c) Other Outward Taxable  supplies(Nil/exempted)',
                '(d) Inward supplies (liable to reverse charge)',
                '(e) Non-GST Outward supplies'
            ]
            for index in range(len(jsonData['sup_details'])):
                line = [vals[index]]
                for col in cols:
                    line.append(jsonData['sup_details'][rows[index]][col])
                lineData.append(line)
            mainData.append(lineData)
            lineData = []
            rows = ['unreg_details', 'comp_details', 'uin_details']
            poss = []
            for row in rows:
                for ele in jsonData['inter_sup'][row]:
                    poss.append(ele['pos'])
            poss = list(set(poss))
            for pos in poss:
                line = [pos]
                for row in rows:
                    for ele in jsonData['inter_sup'][row]:
                        if ele['pos'] == pos:
                            line += [ele['txval'], ele['iamt']]
                            break
                    else:
                        line += [0.0, 0.0]
                lineData.append(line)
            mainData.append(lineData)
            lineData = []
            rows = ['itc_avl', 'itc_rev', 'itc_net', 'itc_inelg']
            cols = ['iamt', 'camt', 'samt', 'csamt']
            vals = [
                '(A)(1) Import of goods',
                '(A)(2) Import of services',
                '(A)(3) Inward supplies liable to reverse charge(other than 1&2 above)',
                '(A)(4) Inward supplies from ISD',
                '(A)(5) All other ITC',
                '(B)(1) As per Rule 42 & 43 of SGST/CGST rules',
                '(B)(2) Others',
                '(C) Net ITC Available (A)-(B)',
                '(D)(1) As per section 17(5) of CGST//SGST Act',
                '(D)(2) Others'
            ]
            flag = 0
            for row in rows:
                for details in jsonData['itc_elg'][row]:
                    line = [vals[flag]]
                    for col in cols:
                        line.append(details[col])
                    flag += 1
                    lineData.append(line)
            mainData.append(lineData)
            lineData = []
            vals = [
                'From a supplier under composition/Exempt/Nil rated supply',
                'Non GST supply'
            ]
            flag = 0
            for details in jsonData['inward_sup']['isup_details']:
                line = [vals[flag], details['inter'], details['intra']]
                flag += 1
                lineData.append(line)
            mainData.append(lineData)
        return [mainData, jsonData]

    def getGstr3BJsonData(self):
        return {
            'gstin': '',
            'ret_period': '',
            'sup_details': {
                'osup_det': {
                    'txval': 0.0,
                    'iamt': 0.0,
                    'camt': 0.0,
                    'samt': 0.0,
                    'csamt': 0.0
                },
                'osup_zero': {
                    'txval': 0.0,
                    'iamt': 0.0,
                    'camt': 0.0,
                    'samt': 0.0,
                    'csamt': 0.0
                },
                'osup_nil_exmp': {
                    'txval': 0.0,
                    'iamt': 0.0,
                    'camt': 0.0,
                    'samt': 0.0,
                    'csamt': 0.0
                },
                'isup_rev': {
                    'txval': 0.0,
                    'iamt': 0.0,
                    'camt': 0.0,
                    'samt': 0.0,
                    'csamt': 0.0
                },
                'osup_nongst': {
                    'txval': 0.0,
                    'iamt': 0.0,
                    'camt': 0.0,
                    'samt': 0.0,
                    'csamt': 0.0
                }
            },
            'inter_sup': {
                'unreg_details': [],
                'comp_details': [],
                'uin_details': []
            },
            'itc_elg': {
                'itc_avl': [{
                    'iamt': 0.0,
                    'camt': 0.0,
                    'samt': 0.0,
                    'csamt': 0.0,
                    'ty': 'IMPG'
                }, {
                    'iamt': 0.0,
                    'camt': 0.0,
                    'samt': 0.0,
                    'csamt': 0.0,
                    'ty': 'IMPS'
                }, {
                    'iamt': 0.0,
                    'camt': 0.0,
                    'samt': 0.0,
                    'csamt': 0.0,
                    'ty': 'ISRC'
                }, {
                    'iamt': 0.0,
                    'camt': 0.0,
                    'samt': 0.0,
                    'csamt': 0.0,
                    'ty': 'ISD'
                }, {
                    'iamt': 0.0,
                    'camt': 0.0,
                    'samt': 0.0,
                    'csamt': 0.0,
                    'ty': 'OTH'
                }],
                'itc_rev': [{
                    'iamt': 0.0,
                    'camt': 0.0,
                    'samt': 0.0,
                    'csamt': 0.0,
                    'ty': 'RUL'
                }, {
                    'iamt': 0.0,
                    'camt': 0.0,
                    'samt': 0.0,
                    'csamt': 0.0,
                    'ty': 'OTH'
                }],
                'itc_net': [{
                    'iamt': 0.0,
                    'camt': 0.0,
                    'samt': 0.0,
                    'csamt': 0.0
                }],
                'itc_inelg': [{
                    'iamt': 0.0,
                    'camt': 0.0,
                    'samt': 0.0,
                    'csamt': 0.0,
                    'ty': 'RUL'
                }, {
                    'iamt': 0.0,
                    'camt': 0.0,
                    'samt': 0.0,
                    'csamt': 0.0,
                    'ty': 'OTH'
                }]
            },
            'inward_sup': {
                'isup_details': [{
                    'inter': 0.0,
                    'intra': 0.0,
                    'ty': 'GST'
                }, {
                    'inter': 0.0,
                    'intra': 0.0,
                    'ty': 'NONGST'
                }]
            },
            'intr_ltfee': {
                'intr_details': {
                    'camt': 0.0,
                    'csamt': 0.0,
                    'iamt': 0.0,
                    'samt': 0.0
                },
                'ltfee_details': {}
            }
        }

    def updateGstValues(self, data, respData, onlyKeys=[]):
        for key in data.keys():
            if key in KEYS and key in data and key in respData:
                if not onlyKeys or key in onlyKeys:
                    data[key] = round(data[key] + respData[key], 2)

    def getGSTInvoiceData(self, invoiceObj, invoiceType, data, gstType=''):
        if gstType != 'gstr3b':
            return super(Gstr1Tool,
                         self).getGSTInvoiceData(invoiceObj=invoiceObj,
                                                 invoiceType=invoiceType,
                                                 data=data,
                                                 gstType=gstType)
        rateJsonDict = {}
        ctx = dict(self._context or {})
        ctx['gstType'] = gstType
        for invoiceLineObj in invoiceObj.invoice_line_ids:
            response = self.with_context(ctx).getInvoiceLineData([], invoiceLineObj, invoiceObj, invoiceType)
            if response:
                respData = response[1]
                respData['txval'] = response[3]
                if invoiceObj.move_type == 'out_invoice':
                    sup_details = data['sup_details']
                    inter_sup = data['inter_sup']
                    if invoiceObj.reverse_charge:
                        self.updateGstValues(sup_details['osup_nil_exmp'], respData)
                    elif invoiceType == 'export':
                        onlyKeys = ['txval', 'iamt', 'csamt']
                        self.updateGstValues(sup_details['osup_zero'], respData, onlyKeys)
                    elif invoiceType in ['b2b', 'b2cs', 'b2cl']:
                        is_nil_exempted = True
                        if invoiceLineObj.tax_ids:
                            tax = invoiceLineObj.tax_ids[0]
                            if tax.amount or (tax.amount_type == 'group' and tax.children_tax_ids and tax.children_tax_ids[0].amount):
                                is_nil_exempted = False
                            if tax.l10n_in_reverse_charge or (tax.amount_type == 'group' and tax.children_tax_ids and any(child_tax_id.l10n_in_reverse_charge for child_tax_id in tax.children_tax_ids)):
                                is_nil_exempted = True
                        if not is_nil_exempted:
                            self.updateGstValues(sup_details['osup_det'], respData)
                        else:
                            onlyKeys = ['txval']
                            self.updateGstValues(sup_details['osup_nil_exmp'], respData, onlyKeys)
                        details = inter_sup['uin_details']
                        if invoiceType in ['b2cs', 'b2cl']:
                            onlyKeys = ['txval']
                            self.updateGstValues(sup_details['osup_nongst'], respData, onlyKeys)
                            details = inter_sup['unreg_details']
                        if self.env.company.state_id != invoiceObj.partner_id.state_id:
                            pos = _unescape(invoiceObj.partner_id.state_id.l10n_in_tin)
                            for element in details:
                                if element['pos'] == pos:
                                    self.updateGstValues(element, respData)
                                    break
                            else:
                                details.append({
                                    'pos': pos,
                                    'txval': respData.get('txval', 0.0),
                                    'iamt': respData.get('iamt', 0.0)
                                })
                            if invoiceLineObj.product_id.is_composition:
                                for element in inter_sup['comp_details']:
                                    if element['pos'] == pos:
                                        self.updateGstValues(element, respData)
                                        break
                                else:
                                    inter_sup['comp_details'].append({
                                        'pos': pos,
                                        'txval': respData.get('txval', 0.0),
                                        'iamt': respData.get('iamt', 0.0)
                                    })
                elif invoiceObj.move_type == 'in_invoice':
                    sup_details = data['sup_details']
                    if invoiceObj.reverse_charge:
                        self.updateGstValues(sup_details['isup_rev'], respData)
                    if invoiceLineObj.tax_ids:
                        tax = invoiceLineObj.tax_ids[0]
                        if tax.l10n_in_reverse_charge or (tax.amount_type == 'group' and tax.children_tax_ids and any(child_tax_id.l10n_in_reverse_charge for child_tax_id in tax.children_tax_ids)):
                            self.updateGstValues(sup_details['isup_rev'], respData)
                    
                    itc_elg = data['itc_elg']
                    inward_sup = data['inward_sup']
                    isup_details = inward_sup['isup_details']
                    if invoiceType == 'import':
                        if invoiceLineObj.product_id and invoiceLineObj.product_id.type == 'consu':
                            productType = 'IMPG'
                        else:
                            productType = 'IMPS'
                    else:
                        productType = 'OTH'
                    if invoiceObj.reverse_charge:
                        productType = 'ISRC'
                    if invoiceLineObj.tax_ids:
                        tax = invoiceLineObj.tax_ids[0]
                        if tax.l10n_in_reverse_charge or (tax.amount_type == 'group' and tax.children_tax_ids and any(child_tax_id.l10n_in_reverse_charge for child_tax_id in tax.children_tax_ids)):
                            productType = 'ISRC'
    
                    for element in itc_elg['itc_avl']:
                        if element['ty'] == productType:
                            self.updateGstValues(element, respData)
                            break
                    if invoiceType != 'import':
                            if not invoiceObj.partner_id.vat:
                                if self.env.company.state_id == invoiceObj.partner_id.state_id:
                                    ele_state = 'intra'
                                else:
                                    ele_state = 'inter'
                                for ele in isup_details:
                                    if ele['ty'] == 'NONGST':
                                        ele[ele_state] = round(ele[ele_state] + respData['txval'], 2)
                                        break
                            else:
                                is_nil_exempted = True
                                if invoiceLineObj.tax_ids:
                                    tax = invoiceLineObj.tax_ids[0]
                                    if tax.amount or (tax.amount_type == 'group' and tax.children_tax_ids and tax.children_tax_ids[0].amount):
                                        is_nil_exempted = False
                                if is_nil_exempted:
                                    if self.env.company.state_id == invoiceObj.partner_id.state_id:
                                        ele_state = 'intra'
                                    else:
                                        ele_state = 'inter'
                                    for ele in isup_details:
                                        if ele['ty'] == 'GST':
                                            ele[ele_state] = round(ele[ele_state] + respData['txval'], 2)
                                            break
                    for key in itc_elg['itc_net'][0].keys():
                        if key in KEYS:
                            itcAvl_sum = sum([ele[key] for ele in itc_elg['itc_avl']])
                            itcRev_sum = sum([ele[key] for ele in itc_elg['itc_rev']])
                            itc_elg['itc_net'][0][key] = itcAvl_sum - itcRev_sum
        return data

    def getGstTaxData(self, invoiceObj, invoiceLineObj, rateObjs, taxedAmount, invoiceType):
        if self._context.get('gstType', '') != 'gstr3b':
            return super(Gstr1Tool,
                         self).getGstTaxData(invoiceObj=invoiceObj,
                                             invoiceLineObj=invoiceLineObj,
                                             rateObjs=rateObjs,
                                             taxedAmount=taxedAmount,
                                             invoiceType=invoiceType)
        gstDict = {
            "txval": 0.0,
            "iamt": 0.0,
            "camt": 0.0,
            "samt": 0.0,
            "csamt": 0.0,
        }
        if rateObjs:
            if invoiceObj.partner_id.country_id.code == 'IN':
                rateObj = rateObjs[0]
                if rateObj.amount_type == "group":
                    gstDict['samt'] = round(taxedAmount / 2, 2)
                    gstDict['camt'] = round(taxedAmount / 2, 2)
                else:
                    gstDict['iamt'] = round(taxedAmount, 2)
            elif invoiceType in ['export', 'import']:
                gstDict['iamt'] = round(taxedAmount, 2)
        return gstDict
