# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# Part of LICENSE file for copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)
import datetime
from odoo import models, fields, _, api
from ast import literal_eval


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
    is_mag_strip = fields.Boolean("Enable  Magnetic Stripe")
    mag_strip_track1 = fields.Char("Track1")
    mag_strip_track2 = fields.Char("Track2")
    mag_strip_track3 = fields.Char("Track3")
    is_manually_duplex = fields.Boolean(string="Manually Body Data")
    manually_body_data_duplex = fields.Text(string="Manually Body Data")

    def update_manually_json_duplex(self):
        print_data = ''
        print_data += "('type', '%s')," % self.data_type
        print_data += "('format', '%s')," % self.data_format
        if self.print_data_type == 'path':
            print_data += "('flavor', 'file'),"
        else:
            print_data += "('flavor', 'base64'),"
        print_data += "('options', {'language': '%s'})," % self.printer_lang
        return print_data

    @api.multi
    def update_manually_data_duplex(self):
        for rec in self:
            manually_data = rec.update_manually_json_duplex()
            rec.manually_body_data_duplex = manually_data
        return True

    def get_manually_data_duplex(self):
        print_data_dict = {}
        if not self.is_manually_duplex:
            raise("Please select the manually print data.")
        try:
            datas = literal_eval(self.manually_body_data_duplex)
            for data in datas:
                print_data_dict.update({
                    data[0]: data[1]
                })
        except:
            raise("Manually data is not correctly data. please check and try again.")
        return print_data_dict

    def create_json_duplex_data(self, front_side_data, back_side_data):
        print_data_dict = {}
        index = 0
        for index, rec in enumerate(self):
            print_data = []
            headerarray = rec.double_print_front_data.split(',')
            for hindex, i in enumerate(headerarray):
                print_data.append('\x1B' + headerarray[hindex] + '\x0D')

            if rec.is_mag_strip:
                print_data.append('\x1B' + rec.mag_strip_track1 + '\x0D')
                print_data.append('\x1B' + rec.mag_strip_track2 + '\x0D')
                print_data.append('\x1B' + rec.mag_strip_track3 + '\x0D')
                print_data.append('\x1B' + 'smw' + '\x0D')

            if self.is_manually_duplex:
                print_evl_front_data_dict = self.get_manually_data_duplex()
                print_evl_front_data_dict.update({
                    'index': index
                })
                print_evl_front_data_dict['options'].update({
                    'precision': rec.double_print_precision,
                    'overlay': True
                })
            else:
                print_evl_front_data_dict = {
                    'type': rec.double_print_data_type,
                    'format': rec.double_print_data_format,
                    'options': {
                        'language': 'EVOLIS',
                        'precision': rec.double_print_precision,
                        'overlay': True
                    },
                    'index': index
                }

            print_evl_back_data_dict = {
                'type': rec.double_print_data_type,
                'format': rec.double_print_data_format,
                'options': {
                    'language': 'EVOLIS',
                    'precision': rec.double_print_precision,
                    'overlay': [literal_eval(rec.double_print_overlay)[0], literal_eval(rec.double_print_overlay)[1]]
                },
                'index': index
            }

            if rec.double_print_data_type == 'path':
                if rec.double_print_data_format == 'pdf':
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
                if rec.double_print_data_format == 'pdf':
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

            backarray = rec.double_print_back_data.split(',')
            for bindex, i in enumerate(backarray):
                print_data.append('\x1B' + backarray[bindex] + '\x0D')

            if rec.double_print_data_type == 'path':
                if rec.double_print_data_format == 'pdf':
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
                if rec.double_print_data_format == 'pdf':
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

            footerarray = rec.double_print_footer_data.split(',')
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
            current_obj_name = rec.name.replace(' ', '_').replace('.', '_').lower() + '_'
            print_data = False
            index = False
            if rec.double_print_data_format == 'pdf':
                svg_file_name = current_obj_name + 'front_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.pdf'
                front_path, front_data_file, front_base64_datas = rec.render_pdf(svg_file_name, rec.body_html, '_front_side')
                svg_file_name = current_obj_name + 'back_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.pdf'
                back_path, back_data_file, back_base64_datas = rec.render_pdf(svg_file_name, rec.back_body_html, '_back_side')
            else:
                svg_file_name = current_obj_name + 'front_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.png'
                front_path, front_data_file, front_base64_datas = rec.render_png(svg_file_name, rec.back_body_html, '_front_side')
                svg_file_name = current_obj_name + 'back_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.png'
                back_path, back_data_file, back_base64_datas = rec.render_png(svg_file_name, rec.back_body_html, '_back_side')
            if rec.double_print_data_type == 'path':
                index, print_data = self.create_json_duplex_data(front_path, back_path)
            else:
                index, print_data = self.create_json_duplex_data(front_base64_datas, back_base64_datas)
            action = {
                "type": "ir.actions.multi.printduplex",
                "res_model": self._name,
                "res_id": rec.id,
                "printer_name": printer_name,
                "print_data": print_data,
                'print_data_len': index,
                "printer_config_dict": printer_config_dict,
                "context": self.env.context,
                "jobName": rec.name,
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
                'overlay': [literal_eval(self.double_print_overlay)[0], literal_eval(self.double_print_overlay)[1]]
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

        if self.is_mag_strip:
            print_data.append('\x1B' + self.mag_strip_track1 + '\x0D')
            print_data.append('\x1B' + self.mag_strip_track2 + '\x0D')
            print_data.append('\x1B' + self.mag_strip_track3 + '\x0D')
            print_data.append('\x1B' + 'smw' + '\x0D')

        if self.is_manually_duplex:
            print_evl_front_data_dict = self.get_manually_data_duplex()
            print_evl_front_data_dict.update({
                'index': index
            })
            print_evl_front_data_dict['options'].update({
                'precision': self.double_print_precision,
                'overlay': True
            })
        else:
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
            current_obj_name = rec.name.replace(' ', '_').replace('.', '_').lower() + '_'
            print_data = False
            if rec.double_print_data_format == 'pdf':
                svg_file_name = current_obj_name + 'front_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.pdf'
                front_path, front_data_file, front_base64_datas = rec.render_pdf(svg_file_name, rec.body_html, '_front_side')
            else:
                svg_file_name = current_obj_name + 'front_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.png'
                front_path, front_data_file, front_base64_datas = rec.render_png(svg_file_name, rec.body_html, '_front_side_')

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
            current_obj_name = rec.name.replace(' ', '_').replace('.', '_').lower() + '_'
            print_data = False
            if rec.double_print_data_format == 'pdf':
                svg_file_name = current_obj_name + 'back_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.pdf'
                back_path, data_file, back_base64_datas = rec.render_pdf(
                    svg_file_name, rec.back_body_html, '_back_side'
                )
            else:
                svg_file_name = current_obj_name + 'back_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.png'
                back_path, data_file, back_base64_datas = rec.render_png(
                    svg_file_name, rec.back_body_html, '_back_side'
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
