# -*- coding: utf-8 -*-
import uuid

from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

class ResCompany(models.Model):
    _inherit = "res.company"

    company_latitude = fields.Char(string='Company Latitude')
    company_longitude = fields.Char(string='Company Longitude')


class ResUsers(models.Model):
    _inherit = "res.users"

    target_amount = fields.Float(string='Monthly Target')
    image = fields.Binary(related='partner_id.image_1920', store=True)

    token = fields.Char()

    def get_user_access_token(self):
        return uuid.uuid4().hex

    def get_dashboard_data(self):
        self.ensure_one()
        Task = self.env['crm.sales.task']
        Lead = self.env['crm.lead']
        today = datetime.today().strftime('%Y-%m-%d')
        today_task = Task.search_count([
            ('user_id', '=', self.env.user.id),
            ('state', '=', 'pending'),
            ('action_date', '=', today)])
        missed_task = Task.search_count([
            ('user_id', '=', self.env.user.id),
            ('state', '=', 'pending'),
            ('action_date', '<', today)])
        future_task = Task.search_count([
            ('user_id', '=', self.env.user.id),
            ('state', '=', 'pending'),
            ('action_date', '>', today)])

        lead_pending = Lead.search_count([
            ('user_id', '=', self.env.user.id),
            ('mobile_state', '=', 'pending')
        ])
        lead_won = Lead.search_count([
            ('user_id', '=', self.env.user.id),
            ('mobile_state', '=', 'won')
        ])
        lead_lost = Lead.search_count([
            ('user_id', '=', self.env.user.id),
            ('mobile_state', '=', 'lost')
        ])

        lead_high = Lead.search_count([
            ('user_id', '=', self.env.user.id),
            ('priority', 'in', [2, 3])
        ])
        lead_medium = Lead.search_count([
            ('user_id', '=', self.env.user.id),
            ('priority', '=', 1)
        ])
        lead_low = Lead.search_count([
            ('user_id', '=', self.env.user.id),
            ('priority', '=', 0)
        ])

        target_amount = self.target_amount
        date = datetime.today()
        last_day = date + relativedelta(day=1, months=+1, days=-1)
        first_day = date + relativedelta(day=1)

        leads = Lead.search([
            ('create_date', '>', first_day.strftime('%Y-%m-%d')),
            ('create_date', '<=', last_day.strftime('%Y-%m-%d')),
            ('user_id', '=', self.env.user.id),
            ('mobile_state', 'in', ['won', 'pending']),
        ])
        achieved_amount = sum(leads.mapped('expected_revenue'))
        company = self.env.user.company_id
        return  {
            'today_task': today_task,
            'missed_task': missed_task,
            'future_task': future_task,

            'lead_pending': lead_pending,
            'lead_won': lead_won,
            'lead_lost': lead_lost,

            'lead_high': lead_high,
            'lead_medium': lead_medium,
            'lead_low': lead_low,
            'target_amount': target_amount,
            'achieved_amount': achieved_amount,

            'latitude': company.company_latitude,
            'longitude': company.company_longitude,
            'company_name': company.name,
            'company_email': company.email,
            'company_phone': company.phone,
            'company_address': '' + (company.street or '') + ', ' + (company.city or '') + ',' + (company.country_id.name or ''),
            'currency': company.currency_id.name,
        }
