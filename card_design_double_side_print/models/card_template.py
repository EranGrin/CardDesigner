# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# Part of LICENSE file for copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)
import datetime
from odoo import models, fields, _, api
import ast


class CardTemplate(models.Model):
    _inherit = 'card.template'

    enable_double_printer = fields.Boolean(
        string=_("Enable Double Print"),
    )
    double_print_precision = fields.Integer(
        string=_("Precision"), default=128
    )
    double_print_overlay = fields.Text(
        string=_("Overlay"), default="[0, 0, 439, 1016],[588, 0, 648, 1016]"
    )
    double_print_data_type = fields.Char(
        string=_("Data Type"), default="raw"
    )
    double_print_data_format = fields.Selection([
        ("pdf", "PDF"),
        ("image", "IMAGE")],
        string=_("Data Format"), default="image"
    )
    duplex_type = fields.Selection([
        ("duplex", "Duplex"),
        ("noduplex", "Non-Duplex")],
        string=_("Type"), default="noduplex"
    )
    double_print_data_type = fields.Selection([
        ("path", "File Path"),
        ("base64", "Base64")
    ], string=_("Printer Data Type"), default="path")
    double_print_front_data = fields.Text(
        string=_("Front Side Data"),
        default="Pps;0,Pwr;0,Pwr;0,Ss,Sr"
    )
    double_print_back_data = fields.Text(
        string=_("Back Side Data"),
        default="Sv"
    )
    double_print_footer_data = fields.Text(
        string=_("Footer Data"),
        default="Se"
    )

    def create_json_duplex_data(self, front_side_data, back_side_data):
        print_data_dict = {}
        index = 0
        print_data = []

        headerarray = self.double_print_front_data.split(',')
        for hindex, i in enumerate(headerarray):
            print_data.append('\x1B' + headerarray[hindex] + '\x0D')

        print_evl_front_data_dict = {
            'type': self.double_print_data_type,
            'format': self.double_print_data_format,
            'options': {
                'language': 'EVOLIS',
                'precision': self.double_print_precision,
                'overlay': True
            },
            'index': index
        }
        print_evl_back_data_dict = {
            'type': self.double_print_data_type,
            'format': self.double_print_data_format,
            'options': {
                'language': 'EVOLIS',
                'precision': self.double_print_precision,
                'overlay': [ast.literal_eval(self.double_print_overlay)[0], ast.literal_eval(self.double_print_overlay)[1]]
            },
            'index': index
        }

        if self.double_print_data_type == 'path':
            if self.double_print_data_format == 'pdf':
                print_evl_front_data_dict.update({
                    'flavor': 'file',
                    'data': front_side_data
                })
            else:
                print_evl_front_data_dict.update({
                    'flavor': 'file',
                    'data': front_side_data
                })
        else:
            if self.double_print_data_format == 'pdf':
                print_evl_front_data_dict.update({
                    'flavor': 'base64',
                    'data': front_side_data,
                })
            else:
                print_evl_front_data_dict.update({
                    'flavor': 'base64',
                    'data': front_side_data,
                })
        print_data.append(print_evl_front_data_dict)

        backarray = self.double_print_back_data.split(',')
        for hindex, i in enumerate(backarray):
            print_data.append('\x1B' + backarray[hindex] + '\x0D')

        if self.double_print_data_type == 'path':
            if self.double_print_data_format == 'pdf':
                print_evl_back_data_dict.update({
                    'flavor': 'file',
                    'data': back_side_data
                })
            else:
                print_evl_back_data_dict.update({
                    'flavor': 'file',
                    'data': back_side_data
                })
        else:
            if self.double_print_data_format == 'pdf':
                print_evl_back_data_dict.update({
                    'flavor': 'base64',
                    'data': back_side_data,
                })
            else:
                print_evl_back_data_dict.update({
                    'flavor': 'base64',
                    'data': back_side_data,
                })
        print_data.append(print_evl_back_data_dict)

        footerarray = self.double_print_footer_data.split(',')
        for findex, j in enumerate(footerarray):
            print_data.append('\x1B' + footerarray[findex] + '\x0D')

        print_data_dict.update({
            index: print_data
        })
        return index, print_data_dict

    @api.multi
    def qz_double_duplex_print(self):
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
            svg_file_name = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            print_data = False
            index = False
            if rec.double_print_data_format == 'pdf':
                svg_file_name += '.pdf'
                front_path, front_data_file, front_base64_datas = rec.render_pdf('_front_side_' + svg_file_name, rec.body_html, '_front_side')
                back_path, data_file, back_base64_datas = rec.render_pdf('_back_side_' + svg_file_name, rec.back_body_html, '_back_side')
            else:
                svg_file_name += '.png'
                front_path, front_data_file, front_base64_datas = rec.render_png('_front_side_' + svg_file_name, rec.back_body_html, '_back_side')
                back_path, data_file, back_base64_datas = rec.render_png('_back_side_' + svg_file_name, rec.back_body_html, '_back_side')
            if rec.double_print_data_type == 'path':
                index, print_data = self.create_json_duplex_data(front_path, back_path)
            else:
                index, print_data = self.create_json_duplex_data(front_base64_datas, back_base64_datas)
            action = {
                "type": "ir.actions.multi.printduplex",
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
                'precision': rec.precision,
                'overlay': rec.overlay,
            }
            return action

    def create_json_nonduplex_back_data(self, side_data):
        index = 0
        print_data = []

        headerarray = self.double_print_front_data.split(',')
        for hindex, i in enumerate(headerarray):
            print_data.append('\x1B' + headerarray[hindex] + '\x0D')

        print_evl_back_data_dict = {
            'type': self.double_print_data_type,
            'format': self.double_print_data_format,
            'options': {
                'language': 'EVOLIS',
                'precision': self.double_print_precision,
                'overlay': [ast.literal_eval(self.double_print_overlay)[0], ast.literal_eval(self.double_print_overlay)[1]]
            },
            'index': index
        }

        if self.double_print_data_type == 'path':
            if self.double_print_data_format == 'pdf':
                print_evl_back_data_dict.update({
                    'flavor': 'file',
                    'data': side_data
                })
            else:
                print_evl_back_data_dict.update({
                    'flavor': 'file',
                    'data': side_data
                })
        else:
            if self.double_print_data_format == 'pdf':
                print_evl_back_data_dict.update({
                    'flavor': 'base64',
                    'data': side_data,
                })
            else:
                print_evl_back_data_dict.update({
                    'flavor': 'base64',
                    'data': side_data,
                })
        print_data.append(print_evl_back_data_dict)

        footerarray = self.double_print_footer_data.split(',')
        for findex, j in enumerate(footerarray):
            print_data.append('\x1B' + footerarray[findex] + '\x0D')

        return index, print_data

    def create_json_nonduplex_front_data(self, side_data):
        index = 0
        print_data = []

        headerarray = self.double_print_front_data.split(',')
        for hindex, i in enumerate(headerarray):
            print_data.append('\x1B' + headerarray[hindex] + '\x0D')

        print_evl_front_data_dict = {
            'type': self.double_print_data_type,
            'format': self.double_print_data_format,
            'options': {
                'language': 'EVOLIS',
                'precision': self.double_print_precision,
                'overlay': True
            },
            'index': index
        }

        if self.double_print_data_type == 'path':
            if self.double_print_data_format == 'pdf':
                print_evl_front_data_dict.update({
                    'flavor': 'file',
                    'data': side_data
                })
            else:
                print_evl_front_data_dict.update({
                    'flavor': 'file',
                    'data': side_data
                })
        else:
            if self.double_print_data_format == 'pdf':
                print_evl_front_data_dict.update({
                    'flavor': 'base64',
                    'data': side_data,
                })
            else:
                print_evl_front_data_dict.update({
                    'flavor': 'base64',
                    'data': side_data,
                })
        print_data.append(print_evl_front_data_dict)

        footerarray = self.double_print_footer_data.split(',')
        for findex, j in enumerate(footerarray):
            print_data.append('\x1B' + footerarray[findex] + '\x0D')

        return index, print_data

    @api.multi
    def qz_double_nonduplex_front_print(self):
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
            svg_file_name = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            print_data = False
            if rec.double_print_data_format == 'pdf':
                svg_file_name += '.pdf'
                front_path, front_data_file, front_base64_datas = rec.render_pdf('_front_side_' + svg_file_name, rec.body_html, '_front_side')
            else:
                svg_file_name += '.png'
                front_path, front_data_file, front_base64_datas = rec.render_png('_front_side_' + svg_file_name, rec.back_body_html, '_back_side')

            if rec.double_print_data_type == 'path':
                index, print_data = self.create_json_nonduplex_front_data(front_path)
            else:
                index, print_data = self.create_json_nonduplex_front_data(front_base64_datas)
            action = {
                "type": "ir.actions.multi.printnonduplex",
                "res_model": self._name,
                "res_id": rec.id,
                "printer_name": printer_name,
                "print_data": print_data,
                "printer_config_dict": printer_config_dict,
                "context": self.env.context,
                "jobName": rec.name,
            }
            return action

    @api.multi
    def qz_double_nonduplex_back_print(self):
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
            svg_file_name = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            print_data = False
            if rec.double_print_data_format == 'pdf':
                svg_file_name += '.pdf'
                back_path, data_file, back_base64_datas = rec.render_pdf(
                    '_back_side_' + svg_file_name, rec.back_body_html, '_back_side'
                )
            else:
                svg_file_name += '.png'
                back_path, data_file, back_base64_datas = rec.render_png(
                    '_back_side_' + svg_file_name, rec.back_body_html, '_back_side'
                )
            if rec.double_print_data_type == 'path':
                index, print_data = self.create_json_nonduplex_back_data(back_path)
            else:
                index, print_data = self.create_json_nonduplex_back_data(back_base64_datas)
            action = {
                "type": "ir.actions.multi.backnonduplex",
                "res_model": self._name,
                "res_id": rec.id,
                "printer_name": printer_name,
                "print_data": print_data,
                "printer_config_dict": printer_config_dict,
                "context": self.env.context,
                "jobName": rec.name,
            }
            return action
