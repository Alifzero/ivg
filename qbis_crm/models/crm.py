# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class CrmIndustry(models.Model):
    _name = 'crm.industry'
    _description = 'Crm Industry'

    name = fields.Char()


class CrmLead(models.Model):
    _inherit = "crm.lead"

    mobile_state = fields.Selection([('pending', 'Pending'), ('won', 'Won'), (
        'lost', 'Lost')], default='pending', string='Mobile Status')
    partner_latitude = fields.Float(string='Geo Latitude', digits=(16, 5))
    partner_longitude = fields.Float(string='Geo Longitude', digits=(16, 5))
    task_ids = fields.One2many(
        'crm.sales.task', 'lead_id', string='Sales Task')
    industry = fields.Many2one('crm.industry', string='Industry')
    # industry = fields.Selection([('IT', 'IT Consulting'), ('ERP', 'ERP'),
    #                              ('mobile_app', 'Mobile Apps'), ('crm', 'CRM'),
    #                              ('hr_services', 'HR Services'), ('others', 'OTHERS'),
    #                              ('financial_services', 'Financial Services')],
    #                             string='Industry')

    def open_google_map(self):
        if not self.partner_latitude or not self.partner_longitude:
            raise UserError(_('Latitude or Longitude Missing'))
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': 'https://maps.google.com/?q={},{}&z=8'.format(self.partner_latitude, self.partner_longitude),
        }

    def action_set_lost(self):
        res = super(CrmLead, self).action_set_lost()
        self.mobile_state = 'lost'
        return res

    def action_set_won_rainbowman(self):
        res = super(CrmLead, self).action_set_won_rainbowman()
        self.mobile_state = 'won'
        return res


class CrmSalesTask(models.Model):
    _name = 'crm.sales.task'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Sales Task'
    _rec_name = 'lead_id'

    lead_id = fields.Many2one('crm.lead', string='Lead')
    action = fields.Selection([('call', 'Call'), ('email', 'Email'), (
        'meeting', 'Meeting'), ('visit', 'Visit'), ('follow', 'Follow')], string='Action')
    note = fields.Text()
    name = fields.Char(string="Dummy Field", default="No Value Needed.")
    action_date = fields.Datetime(string='Action Datetime')
    state = fields.Selection(
        [('pending', 'Pending'), ('done', 'Done'), ('cancel', 'Cancel')], string='Status', track_visibility='onchange', default='pending')
    action_complete_date = fields.Datetime(string='Action Complete Date')
    user_id = fields.Many2one(
        'res.users', string='User', default=lambda self: self.env.user.id)

    def action_done(self):
        self.write({'state': 'done'})
        return True

    def action_cancel(self):
        self.write({'state': 'cancel'})
        return True

    @api.model
    def create(self, vals):
        # TODO: remove once api update
        if isinstance(vals.get('lead_id'), str):
            vals['lead_id'] = int(vals['lead_id'])
        if isinstance(vals.get('user_id'), str):
            vals['user_id'] = int(vals['user_id'])

        task = super().create(vals)
        if task.action and task.action_date and task.user_id:
            self.env['mail.activity'].create({
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'note': task.note,
                'res_id': task.id,
                'res_model_id': self.env.ref('qibt_crm.model_crm_sales_task').id,
                'summary': task.action,
                'user_id': task.user_id.id,
                'date_deadline': task.action_date,
            })
        return task

    def write(self, vals):
        res = super().write(vals)
        if 'state' in vals:
            for task in self:
                #clean activity
                activity_to_update = task.activity_ids.filtered(lambda a: a.user_id == self.env.user)
                if task.state == 'done':
                    activity_to_update.action_done()
                elif task.state == 'cancel':
                    activity_to_update.unlink()
        return res

