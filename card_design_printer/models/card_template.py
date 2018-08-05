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
        default="^XA"
    )
    footer_data = fields.Text(
        string=_("Footer Data"),
        default="^XZ"
    )
    precision = fields.Integer(
        string=_("Precision"), default=128
    )
    overlay = fields.Boolean(
        string=_("Overlay"), default=True
    )
    data_type = fields.Char(
        string=_("Data Type"), default="raw"
    )
    data_format = fields.Char(
        string=_("Data Format"), default="image"
    )
    epl_x = fields.Integer(
        string=_("X (EPL Option)"), default=0
    )
    epl_y = fields.Integer(
        string=_("Y (EPL Option)"), default=0
    )
    print_data_type = fields.Selection([
        ("path", "File PATH"),
        ("base64", "BASE64"),
    ], string=_("Printer Data Type"), default="base64")

    @api.onchange('printer_lang')
    def onchange_printer_lang(self):
        if not self.printer_lang:
            self.header_data = ''
            self.footer_data = ''
        if self.printer_lang == 'ZPL':
            self.header_data = "^XA"
            self.footer_data = "^XZ"
        elif self.printer_lang == 'EPL':
            self.header_data = "N"
            self.footer_data = "P1"
        elif self.printer_lang == 'EVOLIS':
            self.header_data = "Pps;0,Pwr;0,Wcb;k;0,Ss"
            self.footer_data = "Se"

    def create_json_print_data(self, datas=[]):
        print_data_dict = {}
        index = 0
        for index, data in enumerate(datas):
            if self.printer_lang == 'EPL':
                print_data = []
                headerarray = self.header_data.split(',')
                for hindex, i in enumerate(headerarray):
                    print_data.append("\n"+headerarray[hindex]+"\n")
                print_data.append({
                    'type': self.data_type, 'format': self.data_format,
                    'data': data,
                    'options': {
                        'language': self.printer_lang,
                        'x': self.epl_x,
                        'y': self.epl_y
                    },
                    'index': index
                })
                footerarray = self.footer_data.split(',')
                for findex, j in enumerate(footerarray):
                    print_data.append("\n"+footerarray[findex]+"\n")
                print_data_dict.update({
                    index: print_data
                })
            elif self.printer_lang == 'ZPL':
                print_data = []
                headerarray = self.header_data.split(',')
                for hindex, i in enumerate(headerarray):
                    print_data.append(headerarray[hindex]+"\n")
                print_data.append({
                    'type': self.data_type, 'format': self.data_format,
                    'data': data,
                    'options': {'language': self.printer_lang},
                    'index': index
                })
                footerarray = self.footer_data.split(',')
                for findex, j in enumerate(footerarray):
                    print_data.append(footerarray[findex]+"\n")
                print_data_dict.update({
                    index: print_data
                })
            elif self.printer_lang == 'EVOLIS':
                print_data = []
                headerarray = self.header_data.split(',')
                for hindex, i in enumerate(headerarray):
                    print_data.append('\x1B' + headerarray[hindex] + "\x0D")
                print_data.append({
                    'type': self.data_type,
                    'format': self.data_format,
                    'data': data,
                    'options': {
                        'language': self.printer_lang,
                        'precision': self.precision,
                        'overlay': self.overlay
                    },
                    'index': index
                })
                footerarray = self.footer_data.split(',')
                for findex, j in footerarray:
                    print_data.append('\x1B' + footerarray[findex] + "\x0D")
                print_data_dict.update({
                    index: print_data
                })
        return index, print_data_dict

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
            path, data_file, base64_datas = self.render_png(svg_file_name, rec.body_html, '_front_side')
            if rec.print_data_type == 'path':
                data = 'card_design/static/src/export_files/' + path
            else:
                data = 'data:image/png;base64,' + base64_datas
            index, print_data = self.create_json_print_data([data, data])
            action = {
                "type": "ir.actions.print.data",
                "res_model": self._name,
                "res_id": printer.id,
                "printer_name": printer_name,
                "print_data": print_data,
                'print_data_len': index,
                "printer_config_dict": printer_config_dict,
                "context": self.env.context,
                "language": rec.printer_lang,
                "data_type": rec.data_type,
                "data_format": rec.data_format,
                "header_data": rec.header_data,
                "footer_data": rec.footer_data,
                "jobName": rec.name,
            }
            if rec.printer_lang == 'EPL':
                action.update({
                    'epl_x': rec.epl_x,
                    'epl_y': rec.epl_y,
                })
            elif rec.printer_lang == 'EVOLIS':
                action.update({
                    'precision': rec.precision,
                    'overlay': rec.overlay,
                })
            return action

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
            path, data_file, base64_datas = self.render_png(svg_file_name, rec.back_body_html, '_back_side')
            if rec.print_data_type == 'path':
                data = 'card_design/static/src/export_files/' + path
            else:
                data = 'data:image/png;base64,' + base64_datas
            index, print_data = self.create_json_print_data([data])
            action = {
                "type": "ir.actions.print.data",
                "res_model": self._name,
                "res_id": printer.id,
                "printer_name": printer_name,
                "print_data": print_data,
                'print_data_len': index,
                "printer_config_dict": printer_config_dict,
                "context": self.env.context,
                "language": rec.printer_lang,
                "data_type": rec.data_type,
                "data_format": rec.data_format,
                "header_data": rec.header_data,
                "footer_data": rec.footer_data,
                "jobName": rec.name,
            }
            if rec.printer_lang == 'EPL':
                action.update({
                    'epl_x': rec.epl_x,
                    'epl_y': rec.epl_y,
                })
            elif rec.printer_lang == 'EVOLIS':
                action.update({
                    'precision': rec.precision,
                    'overlay': rec.overlay,
                })
            return action
