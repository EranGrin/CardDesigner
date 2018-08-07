# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# Part of LICENSE file for copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)
from odoo import models, fields, _, api


class PrinterLines(models.Model):
    _name = 'printer.lines'

    name = fields.Char(
        string=_("Name"),
        required=True,
    )
    printer_id = fields.Many2one(
        "printer.printer",
        string=_("Printer"),
        required=True,
    )
    default_printer = fields.Boolean(
        string=_('Default Printer')
    )

    @api.multi
    def set_default_printer(self):
        for rec in self:
            get_default_printer_id = self.search([
                ('default_printer', '=', True)
            ])
            if get_default_printer_id:
                get_default_printer_id.default_printer = False
            rec.default_printer = True


class Printer(models.Model):
    _name = 'printer.printer'

    @api.multi
    @api.depends('line_ids', 'line_ids.default_printer')
    def _get_default_printer(self):
        for rec in self:
            default_printer_id = rec.line_ids.filtered(
                lambda r: r.default_printer
            )
            if default_printer_id:
                rec.default_printer = default_printer_id.id

    name = fields.Char(
        string=_("Name"),
        required=True
    )
    host = fields.Char(
        string=_("Host"),
        required=True,
        default="localhost"
    )
    secure_port = fields.Char(
        string=_("Secure Port"),
        required=True,
        default="8181, 8282, 8383, 8484"
    )
    insecure_port = fields.Char(
        string=_("Insecure Port"),
        required=True,
        default="8182, 8283, 8384, 8485"
    )
    using_secure = fields.Boolean(
        string=_("usingSecure"),
        default=True
    )
    keep_alive = fields.Integer(
        string=_("KeepAlive"),
        required=True,
        default=60
    )
    retries = fields.Integer(
        string=_("Retries"),
        required=True,
        default=0
    )
    delay = fields.Integer(
        string=_("Delay"),
        required=True,
        default=0
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'connected')
    ], string=_('State'), default='draft')
    line_ids = fields.One2many(
        "printer.lines",
        "printer_id",
        string=_("Printer List")
    )
    error = fields.Char(string=_("Error"))
    is_error = fields.Boolean(string=_("IS Error"))
    active_msg = fields.Char(string=_("Active Message"))
    is_active = fields.Boolean(string=_("IS Active"))
    default_printer = fields.Many2one(
        "printer.lines",
        string=_("Default Printer"),
        compute="_get_default_printer",
        store=True
    )

    @api.multi
    def reset_connection(self):
        self.write({
            'state': 'draft',
            'error': '',
            'is_error': False,
            'active_msg': '',
            'is_active': ''
        })
        return True

    @api.multi
    def check_connection(self):
        self.ensure_one()
        for rec in self:
            printer_config_dict = {
                "host": rec.host,
                "port": {
                    "secure": [int(secure_port) for secure_port in rec.secure_port.split(",")],
                    "insecure": [int(secure_port) for secure_port in rec.secure_port.split(",")],
                },
                'use_secure': rec.using_secure,
                "keep_alive": rec.keep_alive,
                "retries": rec.retries,
                "delay": rec.delay,
            }
            return {
                "type": "ir.actions.printer.connect",
                "res_model": self._name,
                "res_id": rec.id,
                "printer_config_dict": printer_config_dict,
                "context": self.env.context,
            }

    @api.multi
    def get_printer_list(self):
        self.ensure_one()
        for rec in self:
            printer_config_dict = {
                "host": rec.host,
                "port": {
                    "secure": [int(secure_port) for secure_port in rec.secure_port.split(",")],
                    "insecure": [int(secure_port) for secure_port in rec.secure_port.split(",")],
                },
                'use_secure': rec.using_secure,
                "keep_alive": rec.keep_alive,
                "retries": rec.retries,
                "delay": rec.delay,
            }
            return {
                "type": "ir.actions.printer.list",
                "res_model": self._name,
                "res_id": rec.id,
                "printer_config_dict": printer_config_dict,
                "context": self.env.context,
            }

    @api.model
    def update_printer_list(self, res_id, dict_data):
        if not res_id or not 'printer_names' in dict_data:
            return True
        line_obj = self.env['printer.lines']
        printer_list = dict_data.get('printer_names', [])
        for printer_name in printer_list:
            line_ids = line_obj.search([
                ('name', '=', printer_name),
                ('printer_id', '=', res_id)
            ])
            if line_ids:
                line_ids.write({
                    'name': printer_name
                })
            else:
                line_obj.create({
                    'name': printer_name,
                    'printer_id': res_id
                })
        return True

    def create_json_print_data(self, language, datas=[]):
        print_data_dict = {}
        index = 0
        for index, data in enumerate(datas):
            if language == 'ZPL':
                print_data = [
                    '^XA\n',
                    {
                        'type': 'raw',
                        'format': 'pdf',
                        'flavor': 'file',
                        'data': data,
                        'options': {'language': language}
                    },
                    '^XZ\n'
                ]
                print_data_dict.update({
                    index: print_data
                })
            elif self.printer_lang == 'EPL':
                print_data = [
                    '\nN\n',
                    {
                        'type': 'raw',
                        'format': 'pdf',
                        'flavor': 'file',
                        'data': data,
                        'options': {'language': language}
                    },
                    '\nP1\n'
                ]
                print_data_dict.update({
                    index: print_data
                })
            elif language == 'EVOLIS':
                print_data = [
                    '\x1BPps;0\x0D',
                    '\x1BPwr;0\x0D',
                    '\x1BWcb;k;0\x0D',
                    '\x1BSs\x0D',
                    {
                        'type': 'raw',
                        'format': 'pdf',
                        'flavor': 'file',
                        'data': data,
                        'options': {
                            'language': language
                        }
                    },
                    '\x1BSe\x0D'
                ]
                print_data_dict.update({
                    index: print_data
                })
            else:
                print_data = [
                    {
                        'type': 'raw',
                        'format': 'pdf',
                        'flavor': 'file',
                        'data': data,
                    },
                ]
                print_data_dict.update({
                    index: print_data
                })
        return index, print_data_dict

    @api.multi
    def test_language(self):
        context = dict(self.env.context or {})
        for printer in self:
            if not printer.default_printer:
                return True
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
            URL = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            data = URL + '/card_design_printer/static/src/file/test_card.pdf'
            language = context.get('language', 'ZPL')
            data_list = [data]
            if context.get('multi', False):
                data = URL + '/card_design_printer/static/src/file/pdf_sample.pdf'
                data_list.append(data)
            index, print_data = self.create_json_print_data(language, data_list)
            action = {
                "type": "ir.actions.print.data",
                "res_model": self._name,
                "res_id": printer.id,
                "printer_name": printer_name,
                "print_data": print_data,
                'print_data_len': index,
                "printer_config_dict": printer_config_dict,
                "context": self.env.context,
            }
            return action
