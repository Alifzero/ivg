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