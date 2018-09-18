# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# Part of LICENSE file for copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)
import datetime
from odoo import models, fields, _, api
from ast import literal_eval
from odoo.exceptions import UserError


class CardTemplate(models.Model):
    _inherit = 'card.template'

    duplex_type = fields.Selection([
        ("normal", "Normal"),
        ("duplex", "Duplex"),
        ("noduplex", "Non-Duplex")],
        string=_("Type"), default="normal"
    )
    double_print_back_data = fields.Text(
        string=_("Back Side Data"),
        default="Sv"
    )
    front_feeder = fields.Boolean(string="Front Feeder")
    back_feeder = fields.Boolean(string="Back Feeder")
    front_feeder_type = fields.Selection([
        ("F", "(F) Feeder"),
        ("N", "(N) No feeder insertion"),
        ("C", "(C) Manual insertion, only by command Reverse insertion"),
        ("R", "(R) Reverse insertion"),
        ("M", "(M) Manual insertion"),
        ("B", "(B) Dual mode; both feeder and manual")],
        string=_("Front Feeder"), default="F"
    )
    back_feeder_type = fields.Selection([
        ("F", "(F) Feeder"),
        ("N", "(N) No feeder insertion"),
        ("C", "(C) Manual insertion, only by command Reverse insertion"),
        ("R", "(R) Reverse insertion"),
        ("M", "(M) Manual insertion"),
        ("B", "(B) Dual mode; both feeder and manual")],
        string=_("Back Feeder"), default="F"
    )
    front_ejection_type = fields.Selection([
        ("D", "(D) Output hopper"),
        ("M", "(M) Manual insertion"),
        ("R", "(R) Reverse insertion"),
        ("N", "(N) No feeder insertion")
    ], string=_("Front Ejection"), default="D"
    )
    back_ejection_type = fields.Selection([
        ("D", "(D) Output hopper"),
        ("M", "(M) Manual insertion"),
        ("R", "(R) Reverse insertion"),
        ("N", "(N) No feeder insertion")
    ], string=_("Back Ejection"), default="D"
    )

    manually_body_data_duplex = fields.Text(string="Manually Syntax")
    check_manually_data_duplex = fields.Text(string="Check Syntax")

    def get_evolis_string_back(self):
        print_data = ''
        if self.duplex_type == 'noduplex' and self.type == 'card' and self.back_side:
            if self.back_feeder:
                if self.back_feeder_type:
                    print_data += '#x1BPcim;' + self.back_feeder_type + '#x0D\n'
                if self.back_ejection_type:
                    print_data += '#x1BPcem;' + self.back_ejection_type + '#x0D\n'

            headerarray = self.header_data.split(',')
            for hindex, i in enumerate(headerarray):
                if headerarray[hindex] == 'Pwr;0':
                    print_data += '#x1BPwr;' + self.back_rotation + "#x0D\n"
                else:
                    print_data += '#x1B' + headerarray[hindex] + "#x0D\n"
            print_data_dict = self.get_manually_data()
            print_data_dict = print_data_dict and print_data_dict[0] or {}
            overlay = True
            if self.back_overlay_type == 'custom':
                try:
                    overlay = [literal_eval(self.back_custom_overlay)[0], literal_eval(self.back_custom_overlay)[1]]
                except:
                    raise UserError(_("overlay customer data is not proper. please enter like data [0],[0] "))
            print_data_dict['options'].update({
                'language': 'EVOLIS',
                'precision': self.precision,
                'overlay': overlay,
            })
            print_data += '%s\n' % print_data_dict
            footerarray = self.footer_data.split(',')
            for findex, j in enumerate(footerarray):
                print_data += '#x1B' + footerarray[findex] + "#x0D\n"
        return print_data

    @api.multi
    def check_manually_body_data_duplex(self):
        for rec in self:
            print_data = rec.get_evolis_string_back()
            rec.check_manually_data_duplex = print_data
        return True

    @api.onchange('back_side')
    def onchange_back_side(self):
        for rec in self:
            rec.duplex_type = 'normal'

    def get_evolis_string(self):
        print_data = ''
        if self.type != 'card':
            return super(CardTemplate, self).get_evolis_string()
        if self.duplex_type == 'duplex' and self.type == 'card':
            if self.front_feeder:
                if self.front_feeder_type:
                    print_data += '#x1BPcim;' + self.front_feeder_type + '#x0D\n'
                if self.front_ejection_type:
                    print_data += '#x1BPcem;' + self.front_ejection_type + '#x0D\n'

            headerarray = self.header_data.split(',')
            for hindex, i in enumerate(headerarray):
                if headerarray[hindex] == 'Pwr;0':
                    print_data += '#x1BPwr;' + self.front_rotation + "#x0D\n"
                else:
                    print_data += '#x1B' + headerarray[hindex] + "#x0D\n"
            if self.is_mag_strip:
                if self.mag_strip_track1:
                    print_data += '#x1BDm;1;' + str(self.mag_strip_track1) + '#x0D\n'
                if self.mag_strip_track2:
                    print_data += '#x1BDm;2;' + str(self.mag_strip_track2) + '#x0D\n'
                if self.mag_strip_track3:
                    print_data += '#x1BDm;3;' + str(self.mag_strip_track3) + '#x0D\n'
                if self.mag_strip_track1 or self.mag_strip_track2 or self.mag_strip_track3:
                    print_data += '#x1B' + 'smw' + '#x0D\n'
            print_data_dict = self.get_manually_data()
            print_data_dict = print_data_dict and print_data_dict[0] or {}
            overlay = True
            if self.front_overlay_type == 'custom':
                try:
                    overlay = [literal_eval(self.front_custom_overlay)[0], literal_eval(self.front_custom_overlay)[1]]
                except:
                    raise UserError(_("overlay customer data is not proper. please enter like data [0],[0] "))
            print_data_dict['options'].update({
                'language': 'EVOLIS',
                'precision': self.precision,
                'overlay': overlay,
            })
            print_data += '%s\n' % print_data_dict

            if self.back_feeder:
                if self.back_feeder_type:
                    print_data += '#x1BPcim;' + self.back_feeder_type + '#x0D\n'
                if self.back_ejection_type:
                    print_data += '#x1BPcem;' + self.back_ejection_type + '#x0D\n'

            backarray = self.double_print_back_data.split(',')
            for bindex, i in enumerate(backarray):
                print_data += '#x1B' + backarray[bindex] + '#x0D\n'

            print_data_dict = self.get_manually_data()
            print_data_dict = print_data_dict and print_data_dict[0] or {}
            back_overlay = True
            if self.back_overlay_type == 'custom':
                try:
                    back_overlay = [literal_eval(self.back_custom_overlay)[0], literal_eval(self.back_custom_overlay)[1]]
                except:
                    raise UserError(_("overlay customer data is not proper. please enter like data [0],[0] "))
            print_data_dict['options'].update({
                'language': 'EVOLIS',
                'precision': self.precision,
                'overlay': back_overlay,
            })
            print_data += '%s\n' % print_data_dict
            footerarray = self.footer_data.split(',')
            for findex, j in enumerate(footerarray):
                print_data += '#x1B' + footerarray[findex] + "#x0D\n"
        else:
            if self.front_feeder and self.duplex_type != 'normal':
                if self.front_feeder_type:
                    print_data += '#x1BPcim;' + self.front_feeder_type + '#x0D\n'
                if self.front_ejection_type:
                    print_data += '#x1BPcem;' + self.front_ejection_type + '#x0D\n'

            headerarray = self.header_data.split(',')
            for hindex, i in enumerate(headerarray):
                if headerarray[hindex] == 'Pwr;0':
                    print_data += '#x1BPwr;' + self.front_rotation + "#x0D\n"
                else:
                    print_data += '#x1B' + headerarray[hindex] + "#x0D\n"
            if self.is_mag_strip:
                if self.mag_strip_track1:
                    print_data += '#x1BDm;1;' + str(self.mag_strip_track1) + '#x0D\n'
                if self.mag_strip_track2:
                    print_data += '#x1BDm;2;' + str(self.mag_strip_track2) + '#x0D\n'
                if self.mag_strip_track3:
                    print_data += '#x1BDm;3;' + str(self.mag_strip_track3) + '#x0D\n'
                if self.mag_strip_track1 or self.mag_strip_track2 or self.mag_strip_track3:
                    print_data += '#x1B' + 'smw' + '#x0D\n'
            print_data_dict = self.get_manually_data()
            print_data_dict = print_data_dict and print_data_dict[0] or {}
            overlay = True
            if self.front_overlay_type == 'custom':
                try:
                    overlay = [literal_eval(self.front_custom_overlay)[0], literal_eval(self.front_custom_overlay)[1]]
                except:
                    raise UserError(_("overlay customer data is not proper. please enter like data [0],[0] "))
            print_data_dict['options'].update({
                'precision': self.precision,
                'overlay': overlay,
                'language': 'EVOLIS',
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
                print_data = print_data and print_data[0] or ''
            else:
                if rec.front_feeder and rec.duplex_type != 'normal':
                    if rec.front_feeder_type:
                        print_data.append('\x1BPcim;' + rec.front_feeder_type + '\x0D')
                    if rec.front_ejection_type:
                        print_data.append('\x1BPcem;' + rec.front_ejection_type + '\x0D')
                headerarray = rec.header_data.split(',')
                for hindex, i in enumerate(headerarray):
                    if headerarray[hindex] == 'Pwr;0':
                        print_data.append('\x1BPwr;' + rec.front_rotation + "\x0D")
                    else:
                        print_data.append('\x1B' + headerarray[hindex] + "\x0D")

                if rec.is_mag_strip:
                    if rec.mag_strip_track1:
                        print_data += '#x1BDm;1;' + str(rec.mag_strip_track1) + '#x0D\n'
                    if rec.mag_strip_track2:
                        print_data += '#x1BDm;2;' + str(rec.mag_strip_track2) + '#x0D\n'
                    if rec.mag_strip_track3:
                        print_data += '#x1BDm;3;' + str(rec.mag_strip_track3) + '#x0D\n'
                    if rec.mag_strip_track1 or rec.mag_strip_track2 or rec.mag_strip_track3:
                        print_data += '#x1B' + 'smw' + '#x0D\n'
                overlay = True
                if rec.front_overlay_type == 'custom':
                    try:
                        overlay = [literal_eval(rec.front_custom_overlay)[0], literal_eval(rec.front_custom_overlay)[1]]
                    except:
                        raise UserError(_("overlay customer data is not proper. please enter like data [0],[0] "))

                print_evl_front_data_dict = {
                    'type': rec.data_type,
                    'format': rec.data_format,
                    'data': front_side_data,
                    'options': {
                        'language': 'EVOLIS',
                        'precision': rec.precision,
                        'overlay': overlay
                    },
                    'index': index
                }
                back_overlay = True
                if rec.back_overlay_type == 'custom':
                    try:
                        back_overlay = [literal_eval(rec.back_custom_overlay)[0], literal_eval(rec.back_custom_overlay)[1]]
                    except:
                        raise UserError(_("overlay customer data is not proper. please enter like data [0],[0] "))

                if rec.back_feeder and rec.duplex_type != 'normal':
                    if rec.back_feeder_type:
                        print_data += '#x1BPcim;' + rec.back_feeder_type + '#x0D\n'
                    if rec.back_ejection_type:
                        print_data += '#x1BPcem;' + rec.back_ejection_type + '#x0D\\n'

                print_evl_back_data_dict = {
                    'type': rec.data_type,
                    'format': rec.data_format,
                    'data': back_side_data,
                    'options': {
                        'language': 'EVOLIS',
                        'precision': rec.precision,
                        'overlay': back_overlay
                    },
                    'index': index
                }
                print_data.append(print_evl_front_data_dict)

                backarray = rec.double_print_back_data.split(',')
                for bindex, i in enumerate(backarray):
                    print_data.append('\x1B' + backarray[bindex] + '\x0D')

                print_evl_back_data_dict.update({
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
            if printer.keypair_id:
                printer_config_dict.update({
                    'keypair': {'keys': printer.keypair_id.certificate},
                })
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
                index, print_data = rec.create_json_duplex_data(front_path, back_path)
            else:
                index, print_data = rec.create_json_duplex_data(front_base64_datas, back_base64_datas)
            printer_option = rec.get_printer_option()
            action = {
                "type": "ir.actions.multi.printduplex",
                "res_model": self._name,
                "res_id": rec.id,
                "printer_name": rec.printer_id.name,
                "print_data": print_data,
                'print_data_len': index,
                "printer_config_dict": printer_config_dict,
                "context": self.env.context,
                "jobName": rec.name,
                "printer_option": printer_option,
            }
            return action

    @api.one
    def get_back_manually_print_data(self, datas):
        print_data = []
        if not self.is_manually:
            raise UserError("Please select the manually print data.")
        try:
            for data in self.check_manually_data_duplex.split("\n"):
                try:
                    if type(literal_eval(data)) is dict:
                        data_dict = literal_eval(data)
                        if self.print_data_type == 'path':
                            data_dict.update({
                                'data': datas[0].encode("utf-8"),
                            })
                        else:
                            data_dict.update({
                                'data': datas[1],
                            })
                        print_data.append(data_dict)
                    else:
                        print_data.append(literal_eval(data))
                except:
                    if data:
                        print_data.append(data.replace("#x1B", "\x1B").replace("#x0D", "\x0D").encode("utf-8"))
        except:
            raise UserError("Manually data is not correctly data. please check and try again.")
        return print_data

    def create_json_nonduplex_back_data(self, side_data):
        index = 0
        print_data = []
        if self.duplex_type == 'noduplex' and self.is_manually:
            print_data = self.get_back_manually_print_data([
                side_data, side_data
            ])
            print_data = print_data and print_data[0] or ''
        else:
            if self.back_feeder and self.duplex_type != 'normal':
                if self.back_feeder_type:
                    print_data.append('\x1BPcim;' + self.back_feeder_type + '\x0D')
                if self.back_ejection_type:
                    print_data.append('\x1BPcem;' + self.back_ejection_type + '\x0D')

            headerarray = self.header_data.split(',')
            for hindex, i in enumerate(headerarray):
                if headerarray[hindex] == 'Pwr;0':
                    print_data.append('\x1BPwr;' + self.back_rotation + "\x0D")
                else:
                    print_data.append('\x1B' + headerarray[hindex] + "\x0D")

            back_overlay = True
            if self.back_overlay_type == 'custom':
                try:
                    back_overlay = [literal_eval(self.back_custom_overlay)[0], literal_eval(self.back_custom_overlay)[1]]
                except:
                    raise UserError(_("overlay customer data is not proper. please enter like data [0],[0] "))
            print_evl_back_data_dict = {
                'type': self.data_type,
                'format': self.data_format,
                'data': side_data,
                'options': {
                    'language': 'EVOLIS',
                    'precision': self.precision,
                    'overlay': back_overlay
                },
                'index': index
            }
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
            print_data = print_data and print_data[0] or ''
        else:
            if self.front_feeder and self.duplex_type != 'normal':
                if self.front_feeder_type:
                    print_data.append('\x1BPcim;' + self.front_feeder_type + '\x0D')
                if self.front_ejection_type:
                    print_data.append('\x1BPcem;' + self.front_ejection_type + '\x0D')

            headerarray = self.header_data.split(',')
            for hindex, i in enumerate(headerarray):
                if headerarray[hindex] == 'Pwr;0':
                    print_data.append('\x1BPwr;' + self.front_rotation + "\x0D")
                else:
                    print_data.append('\x1B' + headerarray[hindex] + "\x0D")

            if self.is_mag_strip:
                if self.mag_strip_track1:
                    print_data.append('\x1BDm;1;' + str(self.mag_strip_track1) + '\x0D')
                if self.mag_strip_track2:
                    print_data.append('\x1BDm;2;' + str(self.mag_strip_track2) + '\x0D')
                if self.mag_strip_track3:
                    print_data.append('\x1BDm;3;' + str(self.mag_strip_track3) + '\x0D')
                if self.mag_strip_track1 or self.mag_strip_track2 or self.mag_strip_track3:
                    print_data.append('\x1Bsmw\x0D')

            overlay = True
            if self.front_overlay_type == 'custom':
                try:
                    overlay = [literal_eval(print_data.front_custom_overlay)[0], literal_eval(print_data.front_custom_overlay)[1]]
                except:
                    raise UserError(_("overlay customer data is not proper. please enter like data [0],[0] "))
            print_evl_front_data_dict = {
                'type': self.data_type,
                'format': self.data_format,
                'data': side_data,
                'options': {
                    'language': 'EVOLIS',
                    'precision': self.precision,
                    'overlay': overlay
                },
                'index': index
            }
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
            if printer.keypair_id:
                printer_config_dict.update({
                    'keypair': {'keys': printer.keypair_id.certificate},
                })
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
            printer_option = self.get_printer_option()
            action = {
                "type": "ir.actions.multi.printnonduplex",
                "res_model": self._name,
                "res_id": rec.id,
                "printer_name": rec.printer_id.name,
                "print_data": {index: print_data},
                'print_data_len': index,
                "printer_config_dict": printer_config_dict,
                "context": self.env.context,
                "jobName": rec.name,
                "printer_option": printer_option,
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
            if printer.keypair_id:
                printer_config_dict.update({
                    'keypair': {'keys': printer.keypair_id.certificate},
                })
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
            printer_option = self.get_printer_option()
            action = {
                "type": "ir.actions.multi.backnonduplex",
                "res_model": self._name,
                "res_id": rec.id,
                "printer_name": rec.printer_id.name,
                "print_data": {index: print_data},
                'print_data_len': index,
                "printer_config_dict": printer_config_dict,
                "context": self.env.context,
                "jobName": rec.name,
                "printer_option": printer_option,
            }
            return action
