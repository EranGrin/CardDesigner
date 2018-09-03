# -*- coding: utf-8 -*-

from odoo import fields, models, _, api
import math


class template_size(models.Model):
    _name = 'template.size'

    name = fields.Char(string=_("Name"), required=1)
    height = fields.Float(string=_("Height"), inverse="_calculate_pixel", required=1)
    width = fields.Float(string=_("Width"), inverse="_calculate_pixel", required=1)
    size_unit = fields.Selection([
        ('cm', 'cm'),
        ('in', 'inches'),
        ('px', 'pixel'),
    ], string="Size Units", default='cm', inverse="_calculate_pixel", required=1)
    dpi = fields.Integer(string=_("DPI"), inverse="_calculate_pixel", required=1)
    size_width_px = fields.Integer(string=_("Width"), required=1)
    size_height_px = fields.Integer(string=_("Height"), required=1)

    def get_pixels(self, mode, width, height, DPI):
        # or whatever your machine can handle comfortably
        largest_tile_dimension_wide = 1000
        largest_tile_dimension_high = 1000
        CMINCH = 0.393700787  # 1 centimeter = 0.393700787 inch
        cells_wide = 0
        cells_high = 0
        if mode == 'in':
            w_in_px = width
            h_in_px = height
        else:
            if mode == 'cm':
                width_in_inches = width * CMINCH
                height_in_inches = height * CMINCH
            elif mode == 'in':
                width_in_inches = width
                height_in_inches = height
            # [ ] todo verify if rounding up here is cool
            w_in_px = width_in_inches*DPI
            h_in_px = height_in_inches*DPI
            w_in_px = math.floor(w_in_px)
            h_in_px = math.floor(h_in_px)

            # determine number of tiles wide / high
            cells_wide = math.ceil(w_in_px / largest_tile_dimension_wide)
            cells_high = math.ceil(h_in_px / largest_tile_dimension_high)

        return cells_wide, cells_high, w_in_px, h_in_px

    @api.multi
    def _calculate_pixel(self):
        for rec in self:
            if rec.height and rec.width and rec.size_unit and rec.dpi:
                cells_wide, cells_high, w_in_px, h_in_px = self.get_pixels(
                    rec.size_unit, rec.width, rec.height, rec.dpi
                )
                if w_in_px and h_in_px:
                    rec.size_width_px = w_in_px
                    rec.size_height_px = h_in_px


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
