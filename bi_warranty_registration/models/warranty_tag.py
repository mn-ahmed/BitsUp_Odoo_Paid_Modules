# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class WarrantyTag(models.Model):
    _name = 'warranty.tag'
    _rec_name = 'tag_name'
    _description = "Warranty Tag"

    tag_name = fields.Char('Tag Name')
    tag_desc = fields.Char('Description')
