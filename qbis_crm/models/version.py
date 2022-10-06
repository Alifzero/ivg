# -*- coding: utf-8 -*-

from odoo import api, fields, models


class VersionControl(models.Model):
    _name = 'version.control'
    _description = 'Version Control'
    _order = 'release_date desc'

    name = fields.Char(string='Name')
    version_number = fields.Char(string='Version Number')
    release_date = fields.Datetime(string='Release Date')
    force_update = fields.Selection([('yes', 'Yes'), ('no', 'No')])
    active = fields.Boolean(default=True)
    note = fields.Text(string='Release Note')
