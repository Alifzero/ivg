from odoo import models, fields, api, _ 


class ResPartner(models.Model):
    _inherit  = 'res.partner'

    count_sample_product = fields.Integer(compute='_compute_sample_product')
    sample_product_ids = fields.One2many('crm.lead.line', 'partner_id')
    
    def _compute_sample_product(self):
        for rec in self:
            rec.count_sample_product = len(rec.sample_product_ids)

    def action_view_sample_product(self):
        action = self.env['ir.actions.actions']._for_xml_id('ivg_crm.action_crm_lead_line')
        action['view_mode'] = 'tree'
        action['views'] =[(self.env.ref('ivg_crm.view_crm_lead_line_tree').id, 'tree')] 
        action['domain'] = [('partner_id', '=', self.id)]
        action['context'] = {'create': 0}
        return action