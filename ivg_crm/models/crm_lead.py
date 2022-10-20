from odoo import models, fields, api, _  


class CRMLead(models.Model):
    _name = 'crm.lead'
    _inherit = ['crm.lead', 'rating.mixin']

    is_send_ob_mail = fields.Boolean(copy=False)
    lead_line_ids = fields.One2many(
        comodel_name="crm.lead.line", 
        inverse_name="lead_id", 
        string="Lead Lines"
    )

    count_sample_product = fields.Integer(string="Sample Count",compute='_compute_records')
    attachment_number = fields.Integer('Number of Attachments', compute='_compute_records')
    rating_count = fields.Integer('Rating Count', compute='_compute_records')
    def _compute_records(self):
        domain = [('res_model', '=', 'crm.lead'), ('res_id', 'in', self.ids)]
        attachment_data = self.env['ir.attachment'].read_group(domain, ['res_id'], ['res_id'])
        attachment = dict((data['res_id'], data['res_id_count']) for data in attachment_data)
    
        for rec in self:
            rec.count_sample_product = len(rec.lead_line_ids)
            rec.attachment_number = attachment.get(rec.id, 0)
            rec.rating_count = self.env['rating.rating'].search_count([('res_id', '=', rec.id), ('res_model', '=', 'crm.lead')])

    lead_documents_ids = fields.Many2many('ir.attachment')
    @api.model
    def _send_crm_onboard_all(self):
        leads = self.search([
            ('is_send_ob_mail', '=', False),
            ('email_from', '!=', False),
            ('type', '=', 'opportunity'),
        ])
        for lead in leads:
            lead._send_crm_onboard_mail()
            lead.is_send_ob_mail = True


    def _send_crm_onboard_mail(self, force_send=False):
        for lead in self:
            # template = self.env['mail.template'].browse(21)
            template = self.env.ref('ivg_crm.email_template_crm_customer_onboard', False)
            # lang=lead.lang_id
            # if lang:
            #     template = template.with_context(lang=lang)
            lead.message_post_with_template(
                template.id,
                composition_mode='comment',
                email_layout_xmlid='mail.mail_notification_light',
            )



    def send_crm_rating_mail(self, force_send=False):
        self._send_crm_onboard_mail()
        # for crm in self:
        #     rating_template = self.env.ref('ivg_crm.rating_crm_request_email_template', False)
        #     if rating_template:
        #         crm.rating_send_request(rating_template, force_send=force_send)


    def action_view_sample_product(self):

        action = {
            'name': _('Sample Products'),
            'view_mode': 'kanban,tree,form',
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead.line',
            'domain': [('lead_id', '=', self.id)],
            'context': {'default_lead_id': self.id}
        }
        return action
    
    def action_get_attachment_view(self):
        action = {
            'name': _('Attachments'),
            'view_mode': 'kanban,tree,form',
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'domain': [('res_model', '=', 'crm.lead'), ('res_id', 'in', self.ids)],
            'context': {'default_res_model': 'crm.lead', 'default_res_id': self.id}
        }
        return action
        
    def action_view_rating(self):
        action = {
            'name': _('Customer Ratings'),
            'view_mode': 'kanban,tree,form',
            'type': 'ir.actions.act_window',
            'res_model': 'rating.rating',
            'domain': [('res_model', '=', 'crm.lead'), ('res_id', 'in', self.ids)],
            'context': {'default_res_model': 'crm.lead', 'default_res_id': self.id}
        }
        return action
