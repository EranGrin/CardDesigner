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
                        'format': 'image',
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
                        'format': 'image',
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
                        'format': 'image',
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
                        'format': 'image',
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
            data = 'data:image/png;base64,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'
            language = context.get('language', 'ZPL')
            data_list = [data]
            if context.get('multi', False):
                data = 'data:image/png;base64,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'
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
