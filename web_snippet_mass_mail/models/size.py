# -*- coding: utf-8 -*-

from odoo import fields, models, _
# from odoo import http
# from odoo.http import request
# from odoo.addons.mass_mailing.controllers.web_editor import Web_Editor


class template_size(models.Model):
    _name = 'template.size'

    name = fields.Char(string=_("Name"))
    height = fields.Integer(string=_("Height (PX)"))
    width = fields.Integer(string=_("Width (PX)"))


class custome_image_snippets(models.Model):
    _name = 'custome.image.snippets'

    name = fields.Char(string=_("Name"))
    model_id = fields.Many2one(
        'ir.model', index=True, ondelete='cascade',
        help="The model this field belongs to", string=_("Model")
    )
    field_id = fields.Many2one(
        'ir.model.fields',
        string=_("Image Field"),
        ondelete='cascade',
        domain="[('ttype', '=', 'binary'), ('model_id', '=', model_id)]"
    )
    sample_image = fields.Binary(_("Image"), attachment=True)


# class Web_editor(Web_Editor):

#     @http.route(['/mass_mailing/snippets'], type='json', auth="user", website=True)
#     def mass_mailing_snippets(self):
#         sizes = request.env['template.size'].sudo().search([])
#         image_snippets_ids = request.env['custome.image.snippets'].sudo().search([])
#         values = {
#             'company_id': request.env['res.users'].browse(request.uid).company_id,
#             'sizes': sizes,
#             'image_snippets_ids': image_snippets_ids
#         }
#         return request.env.ref('mass_mailing.email_designer_snippets').render(values)
