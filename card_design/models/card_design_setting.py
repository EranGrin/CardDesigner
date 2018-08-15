# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# See LICENSE file for copyright and licensing details.
from odoo import fields, models, api


class BaseConfigSettings(models.TransientModel):
    _inherit = 'base.config.settings'

    download_path = fields.Char(string="PDF Download Path")
    file_name = fields.Char(string="File Name (with out extension)")
    allow_to_zip = fields.Integer("Maximum File Download Separately (ZIP Creation)")

    @api.model
    def get_default_download_path(self, fields):
        path = self.env.ref('card_design.svg_to_pdf').value
        file_name = self.env.ref('card_design.svg_file_name').value
        allow_to_zip = self.env.ref('card_design.allow_to_zip').value
        return {
            'download_path': path,
            'file_name': file_name,
            'allow_to_zip': allow_to_zip and int(allow_to_zip) or 0
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
            self.env.ref('card_design.allow_to_zip').write({
                'value': record.allow_to_zip and int(record.allow_to_zip) or 0
            })
