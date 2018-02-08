# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# See LICENSE file for copyright and licensing details.# -*- coding: utf-8 -*-
#from odoo import http

# class ../../inceptus/iesAddons/iesCardDesigner(http.Controller):
#     @http.route('/../../inceptus/ies_addons/ies_card_designer/../../inceptus/ies_addons/ies_card_designer/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/../../inceptus/ies_addons/ies_card_designer/../../inceptus/ies_addons/ies_card_designer/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('../../inceptus/ies_addons/ies_card_designer.listing', {
#             'root': '/../../inceptus/ies_addons/ies_card_designer/../../inceptus/ies_addons/ies_card_designer',
#             'objects': http.request.env['../../inceptus/ies_addons/ies_card_designer.../../inceptus/ies_addons/ies_card_designer'].search([]),
#         })

#     @http.route('/../../inceptus/ies_addons/ies_card_designer/../../inceptus/ies_addons/ies_card_designer/objects/<model("../../inceptus/ies_addons/ies_card_designer.../../inceptus/ies_addons/ies_card_designer"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('../../inceptus/ies_addons/ies_card_designer.object', {
#             'object': obj
#         })
