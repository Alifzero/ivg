# -*- coding: utf-8 -*-
from odoo import http
import requests
from odoo.http import request
import base64
from geopy.geocoders import Nominatim

class PushImage(http.Controller):




    @http.route('/crm_push_image/', auth='public',csrf=False)
    def crm_push_image(self, **kw):
        # ip = requests.get('https://api64.ipify.org?format=json').json()
        # response = requests.get(f'https://ipapi.co/111.119.183.15/json/').json()
        # location_data = {
        #     "ip": '111.119.183.15',
        #     "city": response.get("city"),
        #     "region": response.get("region"),
        #     "country": response.get("country_name")
        # }
        # print(location_data)
        # print(response)
        latitude = kw['x']
        longitude = kw['y']
        geolocator = Nominatim(user_agent="alifzerocrm"
        )
        location = geolocator.geocode(latitude+","+longitude,language="en")

        attachment = kw['file'].read() 
        file_base64 = base64.encodestring(attachment)
        vals = {
            'res_model': 'crm.lead',
            'name': kw['file'].filename,
            'res_id': kw['id'],
            'type': 'binary',
            'datas': file_base64,
            'latitude': latitude,
            'longitude': longitude,
            'location': location
        }
        ir_attachments = request.env['ir.attachment'].create(vals)
        # return True