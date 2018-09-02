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

    type = fields.Selection([
        ("card", "Card"),
        ("label", "Label"),
    ], string="Type",
        default="label", required="1"
    )
    # print_type = fields.Selection([
    #     ("zebra", "Zebra"),
    #     ("evolis", "Evolis"),
    # ], string="Printer Type", default="zebra")
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
    )
    dotDensity = fields.Char(string="dotDensity", default="single")
    xml_tag = fields.Char(string="XML Tag", default="v7:Image")
    pageHeight = fields.Integer(
        string=_("Render Height")
    )
    pageWidth = fields.Integer(
        string=_("Render Width"), default=480
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
        string=_("Data Format"), default="pdf"
    )
    epl_x = fields.Integer(
        string=_("X (EPL Option)"), default=0
    )
    epl_y = fields.Integer(
        string=_("Y (EPL Option)"), default=0
    )
    is_mag_strip = fields.Boolean("Enable  Magnetic Stripe")
    mag_strip_track1 = fields.Char("Track1")
    mag_strip_track2 = fields.Integer("Track2")
    mag_strip_track3 = fields.Integer("Track3")
    print_data_type = fields.Selection([
        ("path", "File Path"),
        ("base64", "Base64")
    ], string=_("Printer Data Type"), default="path")
    is_manually = fields.Boolean(string="Manually Syntax")
    manually_body_data = fields.Text(string="Manually Syntax")
    check_manually_data = fields.Text(string="Check Syntax")

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

    @api.multi
    def change_template_size(self):
        res = super(CardTemplate, self).change_template_size()
        for rec in self:
            if rec.template_size and \
                rec.enable_printer and \
                    rec.printer_lang != 'EVOLIS':
                        rec.pageHeight = rec.template_size.size_height_px
                        rec.pageWidth = rec.template_size.size_width_px
        return res

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
        if self.print_data_type == 'path':
            print_data += "('flavor', 'file'),"
        else:
            print_data += "('flavor', 'base64'),"
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
            overlay = [literal_eval(self.front_custom_overlay)[0], literal_eval(self.front_custom_overlay)[1]]
        print_data_dict['options'].update({
            'precision': self.precision,
            'overlay': overlay,
            'language': 'EVOLIS',
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
                        'dotDensity': rec.dotDensity.encode("utf-8"),
                        'pageHeight': rec.pageHeight,
                        'pageWidth': rec.pageWidth,
                        'xmlTag': rec.xml_tag.encode("utf-8"),
                        'x': rec.epl_x,
                        'y': rec.epl_y
                    })
                    if rec.print_data_type == 'path':
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
                        'dotDensity': rec.dotDensity.encode("utf-8"),
                        'pageHeight': rec.pageHeight,
                        'pageWidth': rec.pageWidth,
                        'xmlTag': rec.xml_tag.encode("utf-8"),
                    })
                    if rec.print_data_type == 'path':
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
        if not self.is_manually:
            raise("Please select the manually print data.")
        try:
            for data in self.check_manually_data.split("\n"):
                if self.printer_lang in ['EPL', 'ZPL']:
                    try:
                        data_dict = literal_eval(data)
                        if self.print_data_type == 'path':
                            data_dict.update({
                                'flavor': 'file',
                                'data': datas[0].encode("utf-8"),
                            })
                        else:
                            data_dict.update({
                                'flavor': 'base64',
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
                                    'flavor': 'file',
                                    'data': datas[0].encode("utf-8"),
                                })
                            else:
                                data_dict.update({
                                    'flavor': 'base64',
                                    'data': datas[1],
                                })
                            print_data.append(data_dict)
                        else:
                            print_data.append(literal_eval(data))
                    except:
                        if data:
                            print_data.append(data.replace("#x1B", "\x1B").replace("#x0D", "\x0D").encode("utf-8"))
        except:
            raise("Manually data is not correctly data. please check and try again.")
        return print_data

    @api.one
    def get_manually_data(self):
        print_data_dict = {}
        if not self.is_manually:
            raise("Please select the manually print data.")
        try:
            datas = literal_eval(self.manually_body_data)
            for data in datas:
                print_data_dict.update({
                    data[0]: data[1]
                })
        except:
            raise("Manually data is not correctly data. please check and try again.")
        return print_data_dict

    def create_json_print_data(self, datas=[]):
        print_data_dict = {}
        index = 0
        for index, data in enumerate(datas):
            if self.type == 'label':
                if self.printer_lang == 'EPL':
                    print_data = []
                    if self.is_manually:
                        print_data = self.get_manually_print_data(data)
                    else:
                        headerarray = self.header_data.split(',')
                        for hindex, i in enumerate(headerarray):
                            print_data.append("\n"+headerarray[hindex]+"\n")
                        print_epl_data_dict = {
                            'type': self.data_type,
                            'format': self.data_format,
                            'options': {
                                'dotDensity': self.dotDensity.encode("utf-8"),
                                'pageHeight': int(self.pageHeight),
                                'pageWidth': int(self.pageWidth),
                                'xmlTag': self.xml_tag.encode("utf-8"),
                                'language': 'EPL',
                                'x': int(self.epl_x),
                                'y': int(self.epl_y),
                            },
                            'index': index
                        }
                        if self.print_data_type == 'path':
                            print_epl_data_dict.update({
                                'flavor': 'file',
                                'data': data[0]
                            })
                        else:
                            print_epl_data_dict.update({
                                'flavor': 'base64',
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
                    else:
                        headerarray = self.header_data.split(',')
                        for hindex, i in enumerate(headerarray):
                            print_data.append(headerarray[hindex]+"\n")

                        print_zpl_data_dict = {
                            'type': self.data_type,
                            'format': self.data_format,
                            'options': {
                                'language': 'ZPL',
                                'dotDensity': self.dotDensity,
                                'pageHeight': int(self.pageHeight),
                                'pageWidth': int(self.pageWidth),
                                'xmlTag': self.xml_tag,
                            },
                            'index': index
                        }
                        if self.print_data_type == 'path':
                            if self.data_format == 'pdf':
                                print_zpl_data_dict.update({
                                    'flavor': 'file',
                                    'data': data[0]
                                })
                            else:
                                print_zpl_data_dict.update({
                                    'flavor': 'file',
                                    'data': data[0]
                                })
                        else:
                            if self.data_format == 'pdf':
                                print_zpl_data_dict.update({
                                    'flavor': 'base64',
                                    'data': data[1],
                                })
                            else:
                                print_zpl_data_dict.update({
                                    'flavor': 'base64',
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
                else:
                    headerarray = self.header_data.split(',')
                    for hindex, i in enumerate(headerarray):
                        print_data.append('\x1B' + headerarray[hindex] + "\x0D")
                    if self.is_mag_strip and context.get('front_side', False):
                        if self.mag_strip_track1:
                            print_data.append('\x1BDm;1;' + str(self.mag_strip_track1) + '\x0D')
                        if self.mag_strip_track2:
                            print_data.append('\x1BDm;2;' + str(self.mag_strip_track2) + '\x0D')
                        if self.mag_strip_track3:
                            print_data.append('\x1BDm;3;' + str(self.mag_strip_track3) + '\x0D')
                        if self.mag_strip_track1 or self.mag_strip_track2 or self.mag_strip_track3:
                            print_data.append('\x1B' + 'smw' + '\x0D')

                    overlay = True
                    if context.get('front_side', False):
                        if self.front_overlay_type == 'custom':
                            overlay = [literal_eval(self.front_custom_overlay)[0], literal_eval(self.front_custom_overlay)[1]]
                    else:
                        if self.back_overlay_type == 'custom':
                            overlay = [literal_eval(self.back_custom_overlay)[0], literal_eval(self.back_custom_overlay)[1]]

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
                            'flavor': 'file',
                            'data': data[0]
                        })
                    else:
                        print_evl_data_dict.update({
                            'flavor': 'base64',
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
            current_obj_name = rec.name.replace(' ', '_').replace('.', '_').lower() + '_'
            data_list = []
            if rec.data_format == 'pdf':
                svg_file_name = current_obj_name + 'front_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.pdf'
                path, data_file, base64_datas = rec.render_pdf(svg_file_name, rec.back_body_html, '_back_side')
            else:
                svg_file_name = current_obj_name + 'front_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.png'
                path, data_file, base64_datas = rec.render_png(svg_file_name, rec.back_body_html, '_back_side')
            path_data = path
            base64_data = base64_datas
            data_list.append((path_data, base64_data))
            index, print_data = self.create_json_print_data(data_list)
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
