# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# See LICENSE file for copyright and licensing details.
from odoo import http
from odoo.http import request
from odoo.addons.web_editor.controllers.main import Web_Editor


class Web_Editor(Web_Editor):

    @http.route(["/website_card_design/field/popup_content"], type='http', auth="user")
    def card_design_FieldTextHtmlPopupTemplate(
        self, model=None, res_id=None, field=None, callback=None, **kwargs
    ):
        kwargs['snippets'] = '/website/snippets'
        kwargs['template'] = 'card_design.FieldTextHtmlPopupContent'
        return self.FieldTextHtml(model, res_id, field, callback, **kwargs)

    @http.route('/card_design/field/card_template', type='http', auth="user")
    def card_design_FieldTextHtmlEmailTemplate(
        self, model=None, res_id=None, field=None, callback=None, **kwargs
    ):
        kwargs['snippets'] = '/card_design/snippets'
        kwargs['template'] = 'card_design.FieldTextHtmlInline'
        return self.FieldTextHtmlInline(model, res_id, field, callback, **kwargs)

    @http.route('/card_design/field/card_template_back', type='http', auth="user")
    def card_design_back_FieldTextHtmlEmailTemplate(
        self, model=None, res_id=None, field=None, callback=None, **kwargs
    ):
        kwargs['snippets'] = '/card_design/snippets'
        kwargs['template'] = 'card_design.FieldTextHtmlInline'
        return self.FieldTextHtmlInline(model, res_id, field, callback, **kwargs)

    @http.route(['/card_design/snippets'], type='json', auth="user", website=True)
    def card_design_snippets(self):
        values = {
            'company_id': request.env['res.users'].browse(request.uid).company_id
        }
        return request.env.ref('card_design.email_designer_snippets').render(values)
