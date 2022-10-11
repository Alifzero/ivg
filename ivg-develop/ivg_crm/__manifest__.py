# -*- encoding: utf-8 -*-
{
	"name": "IVG CRM Customizations",
	"summary": "IVG CRM Customization",
	"description": """

	""",
	"version": "15.0",
	"category": "CRM",
	"author": "Muhammad Bilal",
	"website": "https://alifzero.com",
	"depends": ['base', 'crm',],
	"license": 'LGPL-3',
    'support': 'Muhammad Bilal mbilal4m@gmail.com',
	"data": [
		'security/ir.model.access.csv',
		'data/ir_cron_data.xml',
		'data/mail_template_data.xml',
		'views/crm_view.xml',
		'views/crm_lead_line_view.xml',
		'views/res_partner_view.xml',
		'views/crm_rating_report.xml',
		'report/crm_product_report_views.xml',
		],
	"auto_install": False,
	"installable": True,
	"application": False,
}
