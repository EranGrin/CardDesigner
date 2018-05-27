# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# See LICENSE file for copyright and licensing details.
from odoo import fields, models, api


class BaseConfigSettings(models.TransientModel):
    _inherit = 'base.config.settings'

    download_path = fields.Char(string="PDF Download Path")
    page_width = fields.Char(string="Page Width")
    page_height = fields.Char(string="Page Height")
    margin_top = fields.Char(string="Marging Top")
    margin_right = fields.Char(string="Marging Right")
    margin_bottom = fields.Char(string="Marging Bottom")
    margin_left = fields.Char(string="Marging Left")
    file_name = fields.Char(string="File Name (with out extension)")

    @api.model
    def get_default_download_path(self, fields):
        path = self.env.ref('card_design.svg_to_pdf').value
        page_width = self.env.ref('card_design.svg_page_width').value
        page_height = self.env.ref('card_design.svg_page_height').value
        margin_top = self.env.ref('card_design.svg_margin_top').value
        margin_right = self.env.ref('card_design.svg_margin_right').value
        margin_bottom = self.env.ref('card_design.svg_margin_bottom').value
        margin_left = self.env.ref('card_design.svg_margin_left').value
        file_name = self.env.ref('card_design.svg_file_name').value
        return {
            'download_path': path,
            'page_width': page_width,
            'page_height': page_height,
            'margin_top': margin_top,
            'margin_right': margin_right,
            'margin_bottom': margin_bottom,
            'margin_left': margin_left,
            'file_name': file_name,
        }

    @api.multi
    def set_default_download_path(self):
        for record in self:
            self.env.ref('card_design.svg_to_pdf').write({
                'value': record.download_path
            })
            self.env.ref('card_design.svg_file_name').write({
                'value': record.file_name
            })
            self.env.ref('card_design.svg_margin_left').write({
                'value': record.margin_left
            })
            self.env.ref('card_design.svg_margin_bottom').write({
                'value': record.margin_bottom
            })
            self.env.ref('card_design.svg_margin_right').write({
                'value': record.margin_right
            })
            self.env.ref('card_design.svg_margin_top').write({
                'value': record.margin_top
            })
            self.env.ref('card_design.svg_page_height').write({
                'value': record.page_height
            })
            self.env.ref('card_design.svg_page_width').write({
                'value': record.page_width
            })
