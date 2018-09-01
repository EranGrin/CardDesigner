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

    # enable_double_printer = fields.Boolean(
    #     string=_("Enable Evoils"),
    # )
    # precision = fields.Integer(
    #     string=_("Precision"), default=128
    # )
    double_print_overlay = fields.Text(
        string=_("Back Overlay"), default="[0, 0, 439, 1016],[588, 0, 648, 1016]"
    )
    # double_print_data_type = fields.Char(
    #     string=_("Data Type"), default="raw"
    # )
    # double_print_data_format = fields.Selection([
    #     ("pdf", "PDF"),
    #     ("image", "IMAGE")],
    #     string=_("Data Format"), default="image"
    # )
    duplex_type = fields.Selection([
        ("normal", "Normal"),
        ("duplex", "Duplex"),
        ("noduplex", "Non-Duplex")],
        string=_("Type"), default="normal"
    )
    # data_type = fields.Selection([
    #     ("path", "File Path"),
    #     ("base64", "Base64")
    # ], string=_("Printer Data Type"), default="path")
    # header_data = fields.Text(
    #     string=_("Front Side Data"),
    #     default="Pps;0,Pwr;0,Pwr;0,Ss,Sr"
    # )
    double_print_back_data = fields.Text(
        string=_("Back Side Data"),
        default="Sv"
    )
    # footer_data = fields.Text(
    #     string=_("Footer Data"),
    #     default="Se"
    # )
    # is_manually_duplex = fields.Boolean(string="Manually Syntax")
    # manually_body_data_duplex = fields.Text(string="Manually Syntax")
    # check_manually_data_duplex = fields.Text(string="Check Syntax")

    # @api.onchange('printer_lang')
    # def onchange_printer_lang(self):
    #     super(CardTemplate, self).onchange_printer_lang()
    #     for rec in self:
    #         if rec.printer_lang == 'EVOLIS':
    #             rec.enable_double_printer = True
    #         else:
    #             rec.enable_double_printer = False

    # @api.onchange('enable_printer')
    # def onchange_enable_printer(self):
    #     for rec in self:
    #         if not rec.enable_printer:
    #             rec.enable_double_printer = False

    def get_evolis_string(self):
        print_data = ''
        if self.type != 'card':
            return super(CardTemplate, self).get_evolis_string()
        if self.duplex_type == 'duplex' and self.type == 'card':
            headerarray = self.header_data.split(',')
            for hindex, i in enumerate(headerarray):
                print_data += '#x1B' + headerarray[hindex] + "#x0D\n"
            if self.is_mag_strip:
                print_data += '#x1B' + self.mag_strip_track1 + '#x0D\n'
                print_data += '#x1B' + self.mag_strip_track2 + '#x0D\n'
                print_data += '#x1B' + self.mag_strip_track3 + '#x0D\n'
                print_data += '#x1B' + 'smw' + '#x0D\n'
            print_data_dict = self.get_manually_data()
            print_data_dict = print_data_dict and print_data_dict[0] or {}
            print_data_dict['options'].update({
                'precision': self.precision,
                'overlay': self.overlay
            })
            if self.print_data_type == 'path':
                print_data_dict.update({
                    'flavor': 'file',
                    'data': '$value',
                })
            else:
                print_data_dict.update({
                    'flavor': 'base64',
                    'data': '$value',
                })
            print_data += '%s\n' % print_data_dict

            backarray = self.double_print_back_data.split(',')
            for bindex, i in enumerate(backarray):
                print_data += '#x1B' + backarray[bindex] + '#x0D\n'

            print_data_dict = self.get_manually_data()
            print_data_dict = print_data_dict and print_data_dict[0] or {}
            print_data_dict['options'].update({
                'precision': self.precision,
                'overlay': [literal_eval(self.double_print_overlay)[0], literal_eval(self.double_print_overlay)[1]]
            })
            if self.print_data_type == 'path':
                print_data_dict.update({
                    'flavor': 'file',
                    'data': '$value',
                })
            else:
                print_data_dict.update({
                    'flavor': 'base64',
                    'data': '$value',
                })
            print_data += '%s\n' % print_data_dict
            footerarray = self.footer_data.split(',')
            for findex, j in enumerate(footerarray):
                print_data += '#x1B' + footerarray[findex] + "#x0D\n"
        else:
            headerarray = self.header_data.split(',')
            for hindex, i in enumerate(headerarray):
                print_data += '#x1B' + headerarray[hindex] + "#x0D\n"
            if self.is_mag_strip:
                print_data += '#x1B' + self.mag_strip_track1 + '#x0D\n'
                print_data += '#x1B' + self.mag_strip_track2 + '#x0D\n'
                print_data += '#x1B' + self.mag_strip_track3 + '#x0D\n'
                print_data += '#x1B' + 'smw' + '#x0D\n'
            print_data_dict = self.get_manually_data()
            print_data_dict = print_data_dict and print_data_dict[0] or {}
            print_data_dict['options'].update({
                'precision': self.precision,
                'overlay': True
            })
            if self.print_data_type == 'path':
                print_data_dict.update({
                    'flavor': 'file',
                    'data': '$value',
                })
            else:
                print_data_dict.update({
                    'flavor': 'base64',
                    'data': '$value',
                })
            print_data += '%s\n' % print_data_dict
            footerarray = self.footer_data.split(',')
            for findex, j in enumerate(footerarray):
                print_data += '#x1B' + footerarray[findex] + "#x0D\n"
        return print_data

    def create_json_duplex_data(self, front_side_data, back_side_data):
        print_data_dict = {}
        index = 0
        for index, rec in enumerate(self):
            print_data = []
            if self.is_manually:
                print_data = self.get_manually_print_data([
                    front_side_data, front_side_data
                ])
                # print_evl_front_data_dict.update({
                #     'index': index
                # })
                # print_evl_front_data_dict['options'].update({
                #     'precision': rec.precision,
                #     'overlay': True
                # })
            else:
                headerarray = rec.header_data.split(',')
                for hindex, i in enumerate(headerarray):
                    print_data.append('\x1B' + headerarray[hindex] + '\x0D')

                if rec.is_mag_strip:
                    print_data.append('\x1B' + rec.mag_strip_track1 + '\x0D')
                    print_data.append('\x1B' + rec.mag_strip_track2 + '\x0D')
                    print_data.append('\x1B' + rec.mag_strip_track3 + '\x0D')
                    print_data.append('\x1B' + 'smw' + '\x0D')

                print_evl_front_data_dict = {
                    'type': rec.data_type,
                    'format': rec.data_format,
                    'options': {
                        'language': 'EVOLIS',
                        'precision': rec.precision,
                        'overlay': True
                    },
                    'index': index
                }

                print_evl_back_data_dict = {
                    'type': rec.data_type,
                    'format': rec.data_format,
                    'options': {
                        'language': 'EVOLIS',
                        'precision': rec.precision,
                        'overlay': [literal_eval(rec.double_print_overlay)[0], literal_eval(rec.double_print_overlay)[1]]
                    },
                    'index': index
                }

                if rec.print_data_type == 'path':
                    print_evl_front_data_dict.update({
                        'flavor': 'file',
                        'data': front_side_data
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

                if rec.print_data_type == 'path':
                    print_evl_back_data_dict.update({
                        'flavor': 'file',
                        'data': back_side_data
                    })
                else:
                    print_evl_back_data_dict.update({
                        'flavor': 'base64',
                        'data': back_side_data,
                    })
                print_data.append(print_evl_back_data_dict)

                footerarray = rec.footer_data.split(',')
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
            if rec.data_format == 'pdf':
                svg_file_name = current_obj_name + 'front_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.pdf'
                front_path, front_data_file, front_base64_datas = rec.render_pdf(svg_file_name, rec.body_html, '_front_side')
                svg_file_name = current_obj_name + 'back_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.pdf'
                back_path, back_data_file, back_base64_datas = rec.render_pdf(svg_file_name, rec.back_body_html, '_back_side')
            else:
                svg_file_name = current_obj_name + 'front_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.png'
                front_path, front_data_file, front_base64_datas = rec.render_png(svg_file_name, rec.back_body_html, '_front_side')
                svg_file_name = current_obj_name + 'back_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.png'
                back_path, back_data_file, back_base64_datas = rec.render_png(svg_file_name, rec.back_body_html, '_back_side')
            if rec.print_data_type == 'path':
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

        headerarray = self.header_data.split(',')
        for hindex, i in enumerate(headerarray):
            print_data.append('\x1B' + headerarray[hindex] + '\x0D')

        print_evl_back_data_dict = {
            'type': self.data_type,
            'format': self.data_format,
            'options': {
                'language': 'EVOLIS',
                'precision': self.precision,
                'overlay': [literal_eval(self.double_print_overlay)[0], literal_eval(self.double_print_overlay)[1]]
            },
            'index': index
        }

        if self.data_type == 'path':
            if self.data_format == 'pdf':
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
            if self.data_format == 'pdf':
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

        footerarray = self.footer_data.split(',')
        for findex, j in enumerate(footerarray):
            print_data.append('\x1B' + footerarray[findex] + '\x0D')

        return index, print_data

    def create_json_nonduplex_front_data(self, side_data):
        index = 0
        print_data = []
        if self.is_manually:
            print_data = self.get_manually_print_data([
                side_data, side_data
            ])
            # print_evl_front_data_dict.update({
            #     'index': index
            # })
            # print_evl_front_data_dict['options'].update({
            #     'precision': self.precision,
            #     'overlay': True
            # })
        else:
            headerarray = self.header_data.split(',')
            for hindex, i in enumerate(headerarray):
                print_data.append('\x1B' + headerarray[hindex] + '\x0D')

            if self.is_mag_strip:
                print_data.append('\x1B' + self.mag_strip_track1 + '\x0D')
                print_data.append('\x1B' + self.mag_strip_track2 + '\x0D')
                print_data.append('\x1B' + self.mag_strip_track3 + '\x0D')
                print_data.append('\x1B' + 'smw' + '\x0D')

            print_evl_front_data_dict = {
                'type': self.data_type,
                'format': self.data_format,
                'options': {
                    'language': 'EVOLIS',
                    'precision': self.precision,
                    'overlay': True
                },
                'index': index
            }

            if self.data_type == 'path':
                print_evl_front_data_dict.update({
                    'flavor': 'file',
                    'data': side_data
                })
            else:
                print_evl_front_data_dict.update({
                    'flavor': 'base64',
                    'data': side_data,
                })
            print_data.append(print_evl_front_data_dict)

            footerarray = self.footer_data.split(',')
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
            if rec.data_format == 'pdf':
                svg_file_name = current_obj_name + 'front_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.pdf'
                front_path, front_data_file, front_base64_datas = rec.render_pdf(svg_file_name, rec.body_html, '_front_side')
            else:
                svg_file_name = current_obj_name + 'front_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.png'
                front_path, front_data_file, front_base64_datas = rec.render_png(svg_file_name, rec.body_html, '_front_side_')

            if rec.print_data_type == 'path':
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
            if rec.data_format == 'pdf':
                svg_file_name = current_obj_name + 'back_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.pdf'
                back_path, data_file, back_base64_datas = rec.render_pdf(
                    svg_file_name, rec.back_body_html, '_back_side'
                )
            else:
                svg_file_name = current_obj_name + 'back_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.png'
                back_path, data_file, back_base64_datas = rec.render_png(
                    svg_file_name, rec.back_body_html, '_back_side'
                )
            if rec.print_data_type == 'path':
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
