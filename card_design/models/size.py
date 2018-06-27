# -*- coding: utf-8 -*-

from odoo import fields, models, _


class template_size(models.Model):
    _name = 'template.size'

    name = fields.Char(string=_("Name"))
    height = fields.Integer(string=_("Height"))
    width = fields.Integer(string=_("Width"))
    size_unit = fields.Selection([
        ('px', 'px'),
        ('pt', 'pt'),
        ('em', 'em'),
        ('cm', 'cm'),
        ('mm', 'mm'),
        ('%', '%'),
        ('in', 'inches'),
    ], string="Size Units", default='px')


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
