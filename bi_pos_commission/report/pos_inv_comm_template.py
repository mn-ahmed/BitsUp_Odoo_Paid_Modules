# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _


class pos_inv_comm_template(models.AbstractModel):
	_name = 'report.bi_pos_commission.pos_inv_comm_template'
	_description = 'Report POS Invoice Commission'

	def _get_report_values(self, docids, data=None):
		
		record_ids = self.env[data['model']].browse(data['form'])
		return {
				   'doc_ids': self.ids,
				   'doc_model': data['model'],
				   'docs': self,
				   'data' : data,
				   'ids':record_ids
				   }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
