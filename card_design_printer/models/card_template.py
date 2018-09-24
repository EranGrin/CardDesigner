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

    print_ref_ir_act_window_id = fields.Many2one(
        'ir.actions.act_window',
        'Print Sidebar action',
        readonly=True,
        help="Action to make this "
        "template available on "
        "records of the related "
        "document model."
    )
    print_ref_ir_value_id = fields.Many2one(
        'ir.values', 'Print Sidebar',
        readonly=True,
        help="Sidebar button to open "
        "the sidebar action."
    )
    type = fields.Selection([
        ("card", "Card"),
        ("label", "Label"),
    ], string="Type",
        default="label", required="1"
    )
    zebra_lang = fields.Selection([
        ("ZPL", "ZPL"),
        ("EPL", "EPL"),
    ], string="Language")
    evolis_lang = fields.Selection([
        ("EVOLIS", "EVOLIS"),
    ], string="Language", default="EVOLIS")
    enable_printer = fields.Boolean(
        string=_("Enable Printer"),
    )
    printer_id = fields.Many2one(
        "printer.lines",
        string=_("Printer"),
        ondelete='set null',
    )
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
    front_overlay_type = fields.Selection([
        ("full", "Full"),
        ("custom", "Custom"),
    ], string=_("Front Overlay"), default="full")
    back_overlay_type = fields.Selection([
        ("full", "Full"),
        ("custom", "Custom"),
    ], string=_("Back Overlay"), default="full")
    front_custom_overlay = fields.Text(
        string=_("Custom"), default="[0, 0, 439, 1016],[588, 0, 648, 1016]"
    )
    back_custom_overlay = fields.Text(
        string=_("Custom"), default="[0, 0, 439, 1016],[588, 0, 648, 1016]"
    )
    data_type = fields.Char(
        string=_("Data Type"), default="raw"
    )
    data_format = fields.Selection([
        ("pdf", "PDF"),
        ("image", "IMAGE")],
        string=_("Data Format"), default="image"
    )
    epl_x = fields.Integer(
        string=_("X (EPL Option)"), default=0
    )
    epl_y = fields.Integer(
        string=_("Y (EPL Option)"), default=0
    )
    is_mag_strip = fields.Boolean("Enable Magnetic Stripe")
    mag_strip_track1 = fields.Char("Track1", size=79, index=True, help="Alpha (ASCII Range 20-95) len: 79)")
    mag_strip_track2 = fields.Char("Track2", size=40, help="Numeric Len 40")
    mag_strip_track3 = fields.Char("Track3", size=107, help="Numeric Len 107")
    print_data_type = fields.Selection([
        ("path", "File Path"),
        ("base64", "Base64")
    ], string=_("Printer Data Type"), default="path")
    is_manually = fields.Boolean(string="Manually Syntax")
    manually_body_data = fields.Text(string="Manually Syntax")
    check_manually_data = fields.Text(string="Check Syntax")
    is_printed = fields.Boolean('Printed')

    @api.multi
    def unlink_action(self):
        res = super(CardTemplate, self).unlink_action()
        self.mapped('print_ref_ir_act_window_id').sudo().unlink()
        self.mapped('print_ref_ir_value_id').sudo().unlink()
        return res

    @api.multi
    def create_action(self):
        res = super(CardTemplate, self).create_action()
        vals = {}
        action_obj = self.env['ir.actions.act_window']
        src_obj = self.card_model
        select_name = dict(
            self._fields['card_model'].selection(self)).get(
                self.card_model
            )
        print_button_name = _('Print Card for %s') % select_name
        action = action_obj.search([
            ('src_model', '=', src_obj),
            ('name', '=', print_button_name)
        ], limit=1)
        if len(action):  # if action found than it will not create new action for model
            return True
        vals['print_ref_ir_act_window_id'] = action_obj.create({
            'name': print_button_name,
            'type': 'ir.actions.act_window',
            'res_model': 'card.print.wizard',
            'src_model': src_obj,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref("card_design_printer.card_design_action_print_wizard").id,
            'target': 'new',
        }).id
        vals['print_ref_ir_value_id'] = self.env['ir.values'].sudo().create({
            'name': print_button_name,
            'model': src_obj,
            'key2': 'client_action_multi',
            'value': "ir.actions.act_window," +
                     str(vals['print_ref_ir_act_window_id']),
        }).id
        self.write(vals)
        return res

    @api.onchange('type')
    def onchange_type(self):
        for rec in self:
            if rec.type == 'label':
                rec.back_side = False
                rec.onchange_printer_lang()
            else:
                rec.header_data = "Pps;0,Pwr;0,Wcb;k;0,Ss"
                rec.footer_data = "Se"
                if rec.is_mag_strip:
                    rec.mag_strip_track1 = 'foo'
                    rec.mag_strip_track2 = 12459
                    rec.mag_strip_track3 = 55555

    @api.onchange('zebra_lang')
    def onchange_zebra_lang(self):
        for rec in self:
            if rec.zebra_lang:
                rec.printer_lang = rec.zebra_lang
                rec.onchange_printer_lang()
            else:
                rec.printer_lang = False

    @api.onchange('evolis_lang')
    def onchange_evolis_lang(self):
        for rec in self:
            if rec.evolis_lang:
                rec.printer_lang = rec.evolis_lang
                rec.onchange_printer_lang()
            else:
                rec.printer_lang = False

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
            if self.is_mag_strip:
                self.mag_strip_track1 = 'foo'
                self.mag_strip_track2 = 12459
                self.mag_strip_track3 = 55555

    @api.one
    def update_manually_json(self):
        print_data = ''
        print_data += "('type', '%s')," % self.data_type
        print_data += "('format', '%s')," % self.data_format
        print_data += "('data', '$Value'),"
        print_data += "('options', {'language': '%s'})," % self.printer_lang
        return print_data

    @api.multi
    def update_manually_data(self):
        for rec in self:
            manually_data = rec.update_manually_json()
            rec.manually_body_data = manually_data and manually_data[0] or ''
        return True

    def get_evolis_string(self):
        print_data = ''
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

    @api.multi
    def check_manually_body_data(self):
        for rec in self:
            rec.update_manually_data()
            print_data = ''
            if rec.type == 'label':
                if rec.printer_lang == 'EPL':
                    headerarray = self.header_data.split(',')
                    for hindex, i in enumerate(headerarray):
                        print_data += "#n" + headerarray[hindex] + "#n\n"
                    print_data_dict = rec.get_manually_data()
                    print_data_dict = print_data_dict and print_data_dict[0] or {}
                    print_data_dict.get('options', False).update({
                        'language': 'EPL',
                        'x': rec.epl_x,
                        'y': rec.epl_y,
                    })
                    print_data += '%s\n' % print_data_dict
                    footerarray = rec.footer_data.split(',')
                    for findex, j in enumerate(footerarray):
                        print_data += "#n" + footerarray[findex] + "#n\n"
                elif rec.printer_lang == 'ZPL':
                    headerarray = rec.header_data.split(',')
                    for hindex, i in enumerate(headerarray):
                        print_data += headerarray[hindex] + "#n\n"
                    print_data_dict = rec.get_manually_data()
                    print_data_dict = print_data_dict and print_data_dict[0] or {}
                    print_data_dict.get('options', False).update({
                        'language': 'ZPL',
                    })
                    print_data += '%s\n' % print_data_dict
                    footerarray = rec.footer_data.split(',')
                    for findex, j in enumerate(footerarray):
                        print_data += footerarray[findex]+"#n\n"
            elif rec.type == 'card':
                print_data = rec.get_evolis_string()
            rec.check_manually_data = print_data
        return True

    @api.one
    def get_manually_print_data(self, datas):
        print_data = []
        URL = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        if not self.is_manually:
            raise UserError("Please select the manually print data.")
        try:
            for data in self.check_manually_data.split("\n"):
                if self.type == 'label':
                    if self.printer_lang in ['EPL', 'ZPL']:
                        try:
                            data_dict = literal_eval(data)
                            if self.print_data_type == 'path':
                                data_dict.update({
                                    'data': URL + datas[0].encode("utf-8"),
                                })
                            else:
                                data_dict.update({
                                    'data': datas[1],
                                })
                            print_data.append(data_dict)
                        except:
                            if data:
                                print_data.append(data.replace("#n", "\n").encode("utf-8"))
                else:
                    try:
                        if type(literal_eval(data)) is dict:
                            data_dict = literal_eval(data)
                            if self.print_data_type == 'path':
                                data_dict.update({
                                    'data': URL + datas[0].encode("utf-8"),
                                })
                            else:
                                data_dict.update({
                                    'data': datas[1],
                                })
                            print_data.append(data_dict)
                        else:
                            print_data.append(literal_eval(data))
                    except:
                        if 'Dm;1;' in data and len(datas) == 3:
                            data = '#x1BDm;1;' + str(datas[2]) + '#x0D'
                        if 'Dm;2;' in data and len(datas) == 3:
                            data = '#x1BDm;2;' + str(datas[2]) + '#x0D'
                        if 'Dm;3;' in data and len(datas) == 3:
                            data = '#x1BDm;3;' + str(datas[2]) + '#x0D'
                        if data:
                            print_data.append(data.replace("#x1B", "\x1B").replace("#x0D", "\x0D").encode("utf-8"))
        except:
            raise UserError("Manually data is not correctly data. please check and try again.")
        return print_data

    @api.one
    def get_manually_data(self):
        print_data_dict = {}
        if not self.is_manually:
            raise UserError("Please select the manually print data.")
        try:
            datas = literal_eval(self.manually_body_data)
            for data in datas:
                print_data_dict.update({
                    data[0]: data[1]
                })
        except:
            raise UserError("Manually data is not correctly data. please check and try again.")
        return print_data_dict

    def create_json_print_data(self, datas=[]):
        URL = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        print_data_dict = {}
        index = 0
        for index, data in enumerate(datas):
            if self.type == 'label':
                if self.printer_lang == 'EPL':
                    print_data = []
                    if self.is_manually:
                        print_data = self.get_manually_print_data(data)
                        print_data = print_data and print_data[0] or ''
                    else:
                        headerarray = self.header_data.split(',')
                        for hindex, i in enumerate(headerarray):
                            print_data.append("\n"+headerarray[hindex]+"\n")
                        print_epl_data_dict = {
                            'type': self.data_type,
                            'format': self.data_format,
                            'options': {
                                'language': 'EPL',
                                'x': int(self.epl_x),
                                'y': int(self.epl_y),
                            },
                            'index': index
                        }
                        if self.print_data_type == 'path':
                            print_epl_data_dict.update({
                                'data': URL + data[0]
                            })
                        else:
                            print_epl_data_dict.update({
                                'data': data[1]
                            })
                        print_data.append(print_epl_data_dict)
                        footerarray = self.footer_data.split(',')
                        for findex, j in enumerate(footerarray):
                            print_data.append("\n"+footerarray[findex]+"\n")
                    print_data_dict.update({
                        index: print_data
                    })
                elif self.printer_lang == 'ZPL':
                    print_data = []
                    if self.is_manually:
                        print_data = self.get_manually_print_data(data)
                        print_data = print_data and print_data[0] or ''
                    else:
                        headerarray = self.header_data.split(',')
                        for hindex, i in enumerate(headerarray):
                            print_data.append(headerarray[hindex]+"\n")

                        print_zpl_data_dict = {
                            'type': self.data_type,
                            'format': self.data_format,
                            'options': {
                                'language': 'ZPL',
                            },
                            'index': index
                        }
                        if self.print_data_type == 'path':
                            print_zpl_data_dict.update({
                                'data': URL + data[0]
                            })
                        else:
                            print_zpl_data_dict.update({
                                'data': data[1]
                            })
                        print_data.append(print_zpl_data_dict)
                        footerarray = self.footer_data.split(',')
                        for findex, j in enumerate(footerarray):
                            print_data.append(footerarray[findex]+"\n")
                    print_data_dict.update({
                        index: print_data
                    })
            elif self.type == 'card':
                context = dict(self.env.context or {})
                print_data = []
                if self.is_manually:
                    print_data = self.get_manually_print_data(data)
                    print_data = print_data and print_data[0] or []
                else:
                    headerarray = self.header_data.split(',')
                    for hindex, i in enumerate(headerarray):
                        if headerarray[hindex] == 'Pwr;0':
                            if context.get('front_side', False):
                                print_data.append('\x1BPwr;' + self.front_rotation + "\x0D")
                            else:
                                print_data.append('\x1BPwr;' + self.back_rotation + "\x0D")
                        else:
                            print_data.append('\x1B' + headerarray[hindex] + "\x0D")
                    if self.is_mag_strip and context.get('front_side', False):
                        if self.mag_strip_track1:
                            if '{' in self.mag_strip_track1 and len(data) == 3:
                                print_data.append('\x1BDm;1;' + str(data[2]) + '\x0D')
                            else:
                                print_data.append('\x1BDm;1;' + str(self.mag_strip_track1) + '\x0D')
                        if self.mag_strip_track2:
                            if '{' in self.mag_strip_track2 and len(data) == 3:
                                print_data.append('\x1BDm;2;' + str(data[2]) + '\x0D')
                            else:
                                print_data.append('\x1BDm;2;' + str(self.mag_strip_track2) + '\x0D')
                        if self.mag_strip_track3:
                            if '{' in self.mag_strip_track3 and len(data) == 3:
                                print_data.append('\x1BDm;3;' + str(data[2]) + '\x0D')
                            else:
                                print_data.append('\x1BDm;3;' + str(self.mag_strip_track3) + '\x0D')
                        if self.mag_strip_track1 or self.mag_strip_track2 or self.mag_strip_track3:
                            print_data.append('\x1B' + 'smw' + '\x0D')

                    overlay = True
                    if context.get('front_side', False):
                        if self.front_overlay_type == 'custom':
                            try:
                                overlay = [literal_eval(self.front_custom_overlay)[0], literal_eval(self.front_custom_overlay)[1]]
                            except:
                                raise UserError(_("overlay customer data is not proper. please enter like data [0],[0] "))
                    else:
                        if self.back_overlay_type == 'custom':
                            try:
                                overlay = [literal_eval(self.back_custom_overlay)[0], literal_eval(self.back_custom_overlay)[1]]
                            except:
                                raise UserError(_("overlay customer data is not proper. please enter like data [0],[0] "))
                    print_evl_data_dict = {
                        'type': self.data_type,
                        'format': self.data_format,
                        'options': {
                            'language': 'EVOLIS',
                            'precision': self.precision,
                            'overlay': overlay
                        },
                        'index': index
                    }
                    if self.print_data_type == 'path':
                        print_evl_data_dict.update({
                            'data': URL + data[0]
                        })
                    else:
                        print_evl_data_dict.update({
                            'data': data[1],
                        })
                    print_data.append(print_evl_data_dict)
                    footerarray = self.footer_data.split(',')
                    for findex, j in enumerate(footerarray):
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
            if printer.keypair_id:
                printer_config_dict.update({
                    'keypair': {'keys': printer.keypair_id.certificate},
                })
            printer_name = printer.default_printer.name
            current_obj_name = self.name.replace(' ', '_').replace('.', '_').lower() + '_'
            path_data = False
            base64_data = False
            data_list = []
            if rec.data_format == 'pdf':
                svg_file_name = current_obj_name + 'front_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.pdf'
                path, data_file, base64_datas = rec.render_pdf(svg_file_name, rec.body_html, '_front_side')
            else:
                svg_file_name = current_obj_name + 'front_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.png'
                path, data_file, base64_datas = rec.render_png(svg_file_name, rec.body_html, '_front_side')
            path_data = path
            base64_data = base64_datas
            data_list.append((path_data, base64_data))
            context = dict(self.env.context or {})
            context.update({
                'front_side': True,
            })
            index, print_data = rec.with_context(context).create_json_print_data(data_list)
            printer_option = rec.get_printer_option()
            action = {
                "type": "ir.actions.print.data",
                "res_model": self._name,
                "res_id": printer.id,
                "printer_name": rec.printer_id.name,
                "print_data": print_data,
                'print_data_len': index,
                "printer_config_dict": printer_config_dict,
                "context": self.env.context,
                "printer_option": printer_option,
            }
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
            if printer.keypair_id:
                printer_config_dict.update({
                    'keypair': {'keys': printer.keypair_id.certificate},
                })
            printer_name = printer.default_printer.name
            current_obj_name = rec.name.replace(' ', '_').replace('.', '_').lower() + '_'
            data_list = []
            if rec.data_format == 'pdf':
                svg_file_name = current_obj_name + 'back_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.pdf'
                path, data_file, base64_datas = rec.render_pdf(svg_file_name, rec.back_body_html, '_back_side')
            else:
                svg_file_name = current_obj_name + 'back_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.png'
                path, data_file, base64_datas = rec.render_png(svg_file_name, rec.back_body_html, '_back_side')
            path_data = path
            base64_data = base64_datas
            data_list.append((path_data, base64_data))
            index, print_data = self.create_json_print_data(data_list)
            printer_option = self.get_printer_option()
            action = {
                "type": "ir.actions.print.data",
                "res_model": self._name,
                "res_id": printer.id,
                "printer_name": rec.printer_id.name,
                "print_data": print_data,
                'print_data_len': index,
                "printer_config_dict": printer_config_dict,
                "context": self.env.context,
                "printer_option": printer_option,
            }
            return action
