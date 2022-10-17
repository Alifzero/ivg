# -*- coding: utf-8 -*-
import json
import datetime
import base64

import odoo
from odoo import http, _, SUPERUSER_ID
from odoo import fields as odoo_fields
from odoo.http import request
from odoo.addons.web.controllers import main


class QprRestAPI(http.Controller):

    @http.route([
        '/qibt/api/get/version',
    ], auth="public", methods=['POST'], csrf=False, type='json')
    def qibt_get_version(self, **post):
        versio_info = request.env['version.control'].sudo().search_read([], ['name', 'version_number', 'release_date', 'force_update', 'note'], limit=1)
        return versio_info and versio_info[0] or {'error': 'No Version found'}

    @http.route([
        '/qibt/api/user/get_token',
    ], auth="public", methods=['POST'], csrf=False, type='json')
    def qibt_get_token(self, **post):
        res = {}
        if not request.params.get('login') or not request.params.get('password'):
            return {'error': "No login or password found in parameters"}
        try:
            uid = request.session.authenticate(request.session.db, request.params[
                                            'login'], request.params['password'])
            if uid:
                user = request.env['res.users'].sudo().browse(uid)
                token = user.get_user_access_token()
                user.token = token
                res.update(
                    token=token,
                    id=user.id,
                    name=user.partner_id.name,
                    email=user.partner_id.email,
                    login_id=user.login,
                    phone=user.partner_id.phone,
                    image=user.partner_id.image_1920 #base64.encodebytes(user.partner_id.image_1920).decode('ascii'),
                )
                request.session.logout()
            else:
                res['error'] = "Wrong login/password"
        except Exception as e:
            res['error'] = "Something Went Wrong!  %s" % e
        return res

    @http.route([
        '/qibt/api/user/delete_token',
    ], auth="public", methods=['POST'], csrf=False, type='json')
    def qibt_delete_token(self, **post):
        current_user = self._get_current_user(post.get('token'))
        if not current_user:
            return {'error': _('Invalid User Token')}
        else:
            try:
                current_user.token = False
            except Exception as e:
                return {'error': _(' %s' % e)}

        return {'success': _('Token \'%s\' Deleted Successfully' % post.get('token'))}

    @http.route([
        '/qibt/api/user/refresh_token',
    ], auth="public", methods=['POST'], csrf=False, type='json')
    def qibt_refresh_token(self, **post):
        """
            Refresh token : it is medetory to pass token after this call token will return new token.
            eg.localhost:8069/api/user/refresh_token?token=24e635ff9cc74429bed3d420243f5aa6

            It return {"token": "6656a5ba22ca440ca53fd40caeea38eb"}
        """
        current_user = self._get_current_user(post.get('token'))
        if not current_user:
            return {'error': _('Invalid User Token')}
        else:
            try:
                current_user.token = False
                token = current_user.get_user_access_token()
                current_user.token = token
                res = {}
                res.update(
                    token=token,
                    name=current_user.partner_id.name,
                    email=current_user.partner_id.email,
                    login_id=current_user.login,
                    phone=current_user.partner_id.phone,
                    photo=base64.encodebytes(current_user.partner_id.image_1920).decode('ascii'),
                )
                return res
            except Exception as e:
                return {'error': _(' %s' % e)}

    @http.route(['/qibt/api/<string:model>/search', '/qibt/api/<string:model>/search/<int:id>'], auth="public", methods=['POST'], csrf=False, type='json',)
    def qibt_search_data(self, model=None, id=None, **post):
        result = dict()
        current_user = self._get_current_user(post.get('token'))
        if not current_user:
            return {'error': _('Invalid User Token')}
        try:
            Model = request.env[model].with_user(current_user.id)
        except Exception as e:
            return {'error': _('Model Not Found %s' % e)}
        else:
            if id:
                domain = [('id', '=', id)]
                fields = []
            else:
                domain = post.get('domain') and eval(post['domain']) or []
                fields = ['name']

                # Model Specific Code
                if model == 'crm.lead':
                    fields += ['mobile_state']
                    fields += ['partner_latitude']
                    fields += ['partner_longitude']
                    fields += ['task_ids']
                    fields += ['partner_name']
                    fields += ['contact_name']
                    fields += ['email_from']
                    fields += ['phone']
                    fields += ['street']
                    fields += ['description']
                    fields += ['priority']
                    fields += ['industry']
                    fields += ['create_date']
                    fields += ['tag_ids']

                if model == 'crm.sales.task':
                    fields += ['lead_id']
                    fields += ['action']
                    fields += ['action_date']
                    fields += ['note']
                    fields += ['action_complete_date']
                    fields += ['state']
                # ===================

                if post.get('fields'):
                    fields = eval(post.get('fields'))
            result = Model.search_read(domain, fields=fields, offset=int(
                post.get('offset', 0)), limit=post.get('limit') and int(post['limit'] or None))
        result = self.parse_image(result)
        return result

    @http.route(['/qibt/api/<string:model>/create'
                 ], type='json', auth="public", methods=['POST'], csrf=False)
    def qibt_create_record(self, model=None, **post):
        current_user = self._get_current_user(post.get('token'))
        if not current_user:
            return {'error': _('Invalid User Token')}
        try:
            Model = request.env[model].with_user(current_user.id)
        except Exception as e:
            return {'error': _('Model Not Found %s' % e)}
        else:
            if post.get('create_vals'):
                create_vals = eval(post.get('create_vals'))
                if isinstance(create_vals, list):
                    res = []
                    for vals in create_vals:
                        try:
                            record = Model.create(vals)
                        except Exception as e:
                            return {'error': _(' %s' % e)}
                        if record:
                            res.append({'id': record.id})
                    return res #json.dumps(res)
                else:
                    try:
                        record = Model.create(create_vals)
                    except Exception as e:
                        return {'error': _(' %s' % e)}
                    if record:
                        res = {'id': record.id}
                        return res #json.dumps(res)
            else:
                return {'error': _('create_vals not found in query string')}

    @http.route(['/qibt/api/<string:model>/update', '/qibt/api/<string:model>/update/<int:id>'
                 ], type='json', auth="public", methods=['POST'], csrf=False)
    def qibt_update_record(self, model=None, id=None, **post):
        current_user = self._get_current_user(post.get('token'))
        if not current_user:
            return {'error': _('Invalid User Token')}
        try:
            Model = request.env[model].with_user(current_user.id)
        except Exception as e:
            return {'error': _('Model Not Found %s' % e)}
        else:
            if id:
                if post.get('update_vals'):
                    try:
                        record = Model.browse(id)
                        update_vals = eval(post.get('update_vals'))
                        result = record.write(update_vals)
                        if result:
                            return {'success': _('Record Updated Successfully')}
                    except Exception as e:
                        return {'error': _('Model Not Found %s' % e)}
                else:
                    return {'error': _('update_vals not found in query string')}
            else:
                return {'error': _('id not found in query string')}

    @http.route(['/qibt/api/<string:model>/unlink/', '/qibt/api/<string:model>/unlink/<int:id>'
                 ], type='json', auth="public", csrf=False)
    def qibt_unlink_record(self, model=None, id=None, methods=['POST'], **post):
        current_user = self._get_current_user(post.get('token'))
        if not current_user:
            return {'error': _('Invalid User Token')}
        if not current_user:
            return {'error': _('Invalid User Token')}
        try:
            Model = request.env[model].with_user(current_user.id)
        except Exception as e:
            return {'error': _('Model Not Found %s' % e)}
        else:
            if id:
                try:
                    if Model.browse(id).unlink():
                        return {'success': _('Records Successfully Deleted ID - %d' % id)}
                except Exception as e:
                    return {'error': _('Model Not Found %s' % e)}
            else:
                try:
                    ids_list = post.get('unlink_ids') and eval(
                        post['unlink_ids']) or []
                    if Model.browse(ids_list).unlink():
                        return {'success': _('Records Successfully Deleted %s' % post['unlink_ids'])}
                except Exception as e:
                    return json.dumps({'error': _(' %s' % e)})

    @http.route(['/qibt/api/<string:model>/<int:id>/method/<string:method_name>'
                 ], type='json', auth="public", methods=['POST'], csrf=False)
    def qibt_method_call(self, model=None, id=None, method_name=None, **post):
        current_user = self._get_current_user(post.get('token'))
        if not current_user:
            return {'error': _('Invalid User Token')}
        try:
            Model = request.env[model].with_user(current_user.id)
        except Exception as e:
            return {'error': _('Model Not Found %s' % e)}
        else:
            try:
                record = Model.browse(id)
                args = []
                kwargs = {}
                if 'args' in post.keys():
                    args = eval(post['args'])
                if 'kwargs' in post.keys():
                    kwargs = eval(post['kwargs'])
                result = getattr(record, method_name)(*args, **kwargs)
                return {'success': _('%s' % result)}
            except Exception as e:
                return {'error': _('%s' % e)}

    def parse_datetime(self, result):
        for data in result:
            for key, value in data.items():
                if isinstance(value, datetime.date):
                    data[key] = odoo_fields.Date.to_string(value)
                elif isinstance(value, datetime.datetime):
                    data[key] = odoo_fields.Datetime.to_string(value)
        return result

    def parse_image(self, result):
        for data in result:
            for key, value in data.items():
                if isinstance(value, bytes):
                    data[key] = value.decode('utf-8')
        return result
    
    def _get_current_user(self, token):
        if token:
            return request.env['res.users'].sudo().search([('token', '=', token)])
        return False
