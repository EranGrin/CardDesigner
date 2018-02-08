# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.web_editor.controllers.main import Web_Editor


class Web_Editor(Web_Editor):

    @http.route('/card_designer/field/card_template', type='http', auth="user")
    def card_designer_FieldTextHtmlEmailTemplate(self, model=None, res_id=None, field=None, callback=None, **kwargs):
        kwargs['snippets'] = '/card_designer/snippets'
        kwargs['template'] = 'ies_card_designer.FieldTextHtmlInline'
        return self.FieldTextHtmlInline(model, res_id, field, callback, **kwargs)

    @http.route(['/card_designer/snippets'], type='json', auth="user", website=True)
    def card_designer_snippets(self):
        values = {'company_id': request.env['res.users'].browse(request.uid).company_id}
        return request.env.ref('ies_card_designer.card_designer_snippets').render(values)
