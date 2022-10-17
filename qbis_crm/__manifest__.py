# -*- encoding: utf-8 -*-

{
    'name': 'Android ODOO CRM APP',
    'category': 'CRM',
    'version': '14.0.1',
    'author': 'QBIS Consultancy',
    'depends': ['crm'],
    'license': 'AGPL-3',
    'images': ['static/description/banner.gif'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',

        'views/crm_views.xml',
        'views/res_partner_views.xml',
        'views/res_users_views.xml',
        'views/version_views.xml',
    ],
    "summary": "QIBT CRM App allows salesperson to easy capture the lead information in real time",
    "description": """ Modules enhance the feature of CRM for Android APP to easy capture of new lead information in real
    time and allow them to track the related task on the each leads by them. 
    """,

#     "price": "25",
#     "currency": "USD",
    'installable': True,
    'auto_install': False,
}
