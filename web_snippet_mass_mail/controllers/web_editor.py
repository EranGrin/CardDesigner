# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons.card_design.controllers.web_editor import Web_Editor


class Web_Editor(Web_Editor):

    @http.route(['/card_design/snippets'], type='json', auth="user", website=True)
    def card_design_snippets(self):
        sizes = request.env['template.size'].sudo().search([])
        image_snippets_ids = request.env['custome.image.snippets'].sudo().search([])
        values = {
            'company_id': request.env['res.users'].browse(request.uid).company_id,
            'sizes': sizes,
            'image_snippets_ids': image_snippets_ids
        }
        return request.env.ref('card_design.email_designer_snippets').render(values)
