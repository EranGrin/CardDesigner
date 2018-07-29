# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# Part of LICENSE file for copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)
import datetime
from odoo import models, fields, _, api


class CardTemplate(models.Model):
    _inherit = 'card.template'

    enable_printer = fields.Boolean(
        string=_("Enable Printer"),
    )
    printer_id = fields.Many2one(
        "printer.lines",
        string=_("Printer"),
    )
    color_type = fields.Selection([
        ("color", "Color"),
        ("grayscale", "Grayscale"),
        ("blackwhite", "Black & White")
    ], string=_("Color Type"), default="color")
    copies = fields.Integer(
        string=_("Copies"),
        default=1,
        required=True
    )
    units = fields.Selection([
        ("in", "Inches (IN)"),
        ("mm", "Millimeters (mm)"),
        ("cm", "Centimeters (cm)")
    ], string=_("Units"), default="in")
    density = fields.Integer(
        string=_("Pixel Density"),
        default=300,
    )
    size = fields.Char(
        string=_("Size"),
        default="400,400",
    )
    margins = fields.Char(
        string=_("Margins"),
        default="0, 0, 0, 0",
    )
    orientation = fields.Selection([
        ("default", "Default"),
        ("portrati", "Portrait"),
        ("landscape", "Landscape"),
        ("reverse-landscape", "Reverse Landscape")
    ], string=_("Orientation"), default="default")
    interpolation = fields.Selection([
        ("default", "Default"),
        ("bicubic", "Bicubic"),
        ("bilinear", "Bilinear"),
        ("nearest-neighbor", "Nearest-Neighbor")
    ], string=_("Interpolation"), default="default")
    printer_lang = fields.Selection([
        ("ZPL", "ZPL"),
        ("EPL", "EPL"),
        ("EVOLIS", "EVOLIS"),
    ], string=_("Printer Language"), default="ZPL")
    header_data = fields.Text(
        string=_("Header Data"),
        default="'^XA\n','^FO50,50^ADN,36,20^FDPRINTED USING QZ TRAY PLUGIN\n',"
    )
    Footer_data = fields.Text(
        string=_("Footer Data"),
        default="'^FS\n','^XZ\n'"
    )

    @api.multi
    def qz_print_front_side(self):
        for rec in self:
            printer = rec.printer_id.printer_id
            printer_config_dict = {
                "host": printer.host,
                "port": {
                    "secure": [int(secure_port) for secure_port in printer.secure_port.split(",")],
                    "insecure": [int(secure_port) for secure_port in printer.secure_port.split(",")],
                },
                'use_secure': printer.using_secure,
                "keep_alive": printer.keep_alive,
                "retries": printer.retries,
                "delay": printer.delay,
            }
            printer_name = printer.default_printer.name
            svg_file_name = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            path, data_file = self.render_pdf(svg_file_name, rec.body_html, '_front_side')
            file_path = 'card_design/static/src/export_files/' + path
            return {
                "type": "ir.actions.print.data",
                "res_model": self._name,
                "res_id": printer.id,
                "printer_name": printer_name,
                "path": file_path,
                "printer_config_dict": printer_config_dict,
                "context": self.env.context,
            }

    @api.multi
    def qz_print_back_side(self):
        for rec in self:
            printer = rec.printer_id.printer_id
            printer_config_dict = {
                "host": printer.host,
                "port": {
                    "secure": [int(secure_port) for secure_port in printer.secure_port.split(",")],
                    "insecure": [int(secure_port) for secure_port in printer.secure_port.split(",")],
                },
                'use_secure': printer.using_secure,
                "keep_alive": printer.keep_alive,
                "retries": printer.retries,
                "delay": printer.delay,
            }
            printer_name = printer.default_printer.name
            svg_file_name = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            path, data_file = self.render_pdf(svg_file_name, rec.back_body_html, '_back_side')
            file_path = 'card_design/static/src/export_files/' + path
            return {
                "type": "ir.actions.print.data",
                "res_model": self._name,
                "res_id": printer.id,
                "printer_name": printer_name,
                "path": file_path,
                "printer_config_dict": printer_config_dict,
                "context": self.env.context,
            }
