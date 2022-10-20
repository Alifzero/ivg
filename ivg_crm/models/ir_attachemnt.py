from odoo import models, fields, api, _ 


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    latitude = fields.Char()
    longitude = fields.Char()
    location = fields.Char()