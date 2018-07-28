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

    # @api.multi
    # def test_print_data(self):
    #     self.ensure_one()
    #     for rec in self:
    #         printer = rec.printer_id
    #         printer_name = rec.name
    #         printer_config_dict = {
    #             "host": printer.host,
    #             "port": {
    #                 "secure": [int(secure_port) for secure_port in printer.secure_port.split(",")],
    #                 "insecure": [int(secure_port) for secure_port in printer.secure_port.split(",")],
    #             },
    #             'use_secure': printer.using_secure,
    #             "keep_alive": printer.keep_alive,
    #             "retries": printer.retries,
    #             "delay": printer.delay,
    #         }
    #         return {
    #             "type": "ir.actions.print.data",
    #             "res_model": self._name,
    #             "res_id": rec.id,
    #             "printer_name": printer_name,
    #             "file_path": "/card_design_printer/static/src/file/test_card.pdf",
    #             "printer_config_dict": printer_config_dict,
    #             "context": self.env.context,
    #         }


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

    @api.multi
    def test_print_data(self):
        self.ensure_one()
        for printer in self:
            if not printer.default_printer:
                return True
            printer_name = printer.default_printer.name
            data = 'Ck4KcTYwOQpRMjAzLDI2CkI1LDI2LDAsMUEsMyw3LDE1MixCLCIxMjM0IgpBMzEwLDI2LDAsMywx' + \
                'LDEsTiwiU0tVIDAwMDAwIE1GRyAwMDAwIgpBMzEwLDU2LDAsMywxLDEsTiwiUVogUFJJTlQgQVBQ' + \
                'TEVUIgpBMzEwLDg2LDAsMywxLDEsTiwiVEVTVCBQUklOVCBTVUNDRVNTRlVMIgpBMzEwLDExNiww' + \
                'LDMsMSwxLE4sIkZST00gU0FNUExFLkhUTUwiCkEzMTAsMTQ2LDAsMywxLDEsTiwiUVpJTkRVU1RS' + \
                'SUVTLkNPTSIKR1cxNTAsMzAwLDMyLDEyOCz/////////6SSSX///////////////////////////' + \
                '//////////6UlUqX////////////////////////////////////8kqkpKP/////////////////' + \
                '//////////////////6JUpJSVf//////////////////////////////////9KpKVVU+////////' + \
                '//////////////////////////8KSSlJJf5/////////////////////////////////9KUqpVU/' + \
                '/7////////////////////////////////9KqUkokf//P///////////////////////////////' + \
                '+VKUqpZP//+P///////////////////////////////ElKUlSf///9f/////////////////////' + \
                '////////+ipSkqin////y/////////////////////////////+lVUpUlX/////r////////////' + \
                '/////////////////qlJKUql/////+n////////////////////////////BFKVKUl//////8v//' + \
                '/////////////////////////zVSlKUp///////0f//////////////////////////wiSlSUpf/' + \
                '//////q///////////////////////////KqlJUpV///////+R//////////////////////////' + \
                '4UlKSpSX///////9T/////////6L///////////////BKlKpSqP///////1X////////0qg/23/V' + \
                'VVVVVVf//8CSlJKklf///////kv///////+pS0/JP8AAAAAAB///wFSlSSpV///////+pf//////' + \
                '/pUoq+qfwAAAAAAH//+AClSqpUT///////9S///////8pJUlkr+AAAAAAA///4AFJSSSUv//////' + \
                '/yl///////KVUpTUv8AAAAAAH///gBKSqlVU////////lX//////6UkqoiU/wAAAAAA///+ABKpJ' + \
                'Uko////////JH//////UpIiqlJ/AAAAAAD///wACkSUpJX///////6q//////6pVVSqiv4AAAAAA' + \
                'f///AAJVVIqpP///////pI//////pSVtSSq/wAAAAAD///8AAJSlVJVf///////Sp/////8Sq//U' + \
                'qL/ttttoAP///wAAUpVSpJ///////+pT/////qkn//UlH/////AB////AABKUSpSX///////5Sn/' + \
                '///+lJ//+pS/////4AP///8AABKUkpVP///////ylP////1Kv//+qr/////AA////4AAKVVJUl//' + \
                '/////+lKf////KS///8kv////8AH////gAAKSSpJR///////9Kq////9Kv///5Kf////gAf///+A' + \
                'AAUlUqov///////1JT////lS////qn////8AD////4AABKpKSqf///////Skj///+kr////JH///' + \
                '/wAf////wAACkqUlK///////8pKv///ypf///9V////+AD/////AAAFKUVSj///////wqlP///JT' + \
                '////yR////wAP////8AAAFKqkpv///////JSlf//9Sv////U/////AB/////4AAAVIpKRf//////' + \
                '+ElV///pS////8of///4AP/////gAAASZVKr///////4qkj///Sn////0v////AA//////AAABUS' + \
                'VJH///////glJn//8pP////KH///8AH/////+AAACtUlVf//////+ClRP//qV////9K////gA///' + \
                '///4AAACEpJK///////8BSqf/+lX////yr///8AD//////wAAAVUqVH///////gUlU//5Rf////R' + \
                'P///gAf//////gAAApKqTP//////8AVSV//pU////6qf//+AD//////+AAAAqkki//////8AEpVL' + \
                '/+qP////1L///wAP//////4AAACSVVB/////+AFUpKX/9KP////Sv//+AB///////AAAAEqSgH//' + \
                '//+ACkpSUv/lV////6k///4AP//////+AAAAUlSgf////gAJKRUpf/ST////1J///AA///////4A' + \
                'AAAVJVB////gAtVFUpV/8lX///+Vf//4AH///////gAAABKSSD///wASSVVJSR/1Vf///8kf//gA' + \
                '///////+AAAABVUof//4AElUpKqqv/SL////1L//8AD///////4AAAABJJQ//8AFVJKVKSSP+qj/' + \
                '///Kv//gAf///////gAAAAKSpT/+ACkqSlKUkqf5Rf///6S//+AD///////+AAAAAKqpP/ABJKVS' + \
                'klKqU/xUf///qp//wAP///////4AAAAAkko+gASVKUlVKlKX/VK///9Sf/+AB////////gAAAACp' + \
                'UrgAKqVKVJKSlKf+Sl///0kf/4AP///////+AAAAABSVIAFJUlKqSUpKV/0pX//8qr//AA//////' + \
                '//8AAAAACklACSopKSVUqVKX/qpH//okv/4AH////////gAAAAAVVKBUpUqUkkpKSk//SSv/xVK/' + \
                '/AAAAAAD////AAAAAAJKWSUpVKVVUqVSp/+qqH9SlR/8AAAAAAH///4AAAAABSUklJSSlJJKUkpf' + \
                '/8klQFSo//gAAAAAA////wAAAAABVKqlUkqlSqkqqU//6pUqkkof8AAAAAAB/r//AAAAAAElEpSK' + \
                'qSlSSpJKL//pUqpVKr/wAAAAAAP8v/8AAAAAAJLKUqkkpSqkqSVf//yUkpKSv+AAAAAAAfqf/wAA' + \
                'AAAAVClKVVUoklUqqp///UpKVVS/wAAAAAAD+S//AAAAAAAlpSkkkpVKkpKSX///JVKTpR+AAAAA' + \
                'AAH9X/8AAAAAABRUpVJUqqSpSUlf///SSk/Sv4AAAAAAA/y//wAAAAAAFSVUlSUkUkpUqr////VS' + \
                'v9S/AAAAAAAB/3//AAAAAAAFUkpSlJMqqUpJP////13/pT////////////8AAAAAAAEpJSlSqUkk' + \
                'pVS////////Un////////////wAAAAAABJVSlSpUqpUpJX///////8q/////////////gAAAAAAC' + \
                'pSqkkpKSUpSSP///////5L////////////+AAAAAAACSkVVKSklKpVV///////+SX///////////' + \
                '/4AAAAAAAFSqJKlSqqiVSX///////9U/////////////gAAAAAAASpVSlSkklVJU////////yr//' + \
                '//////////+AAAAAAAAkpJSklKpKSUp////////kn////////////4AAAAAAABJSqlKqkqUqVf//' + \
                '/////5K/////////////gAAAAAAACpUlKpJKUqlI////////1L////////////+AAAAAAAAFSVKS' + \
                'SqkpFKX////////SX////////////4AAAAAAAAiklKlSSpTKKv///////9U/////////////wAAA' + \
                'AAAABSpSlSqlSiVJ////////pV/////////////AAAAAAAAVUpSkklSlUqX////////Uv///////' + \
                '/////8AAAAAAAAkqUpVJJSqpVf///////8pf////////////4AAAAAAAFJKUpKqUpJUT////////' + \
                '4r/////////////wAAAAAAAKqVKVKUqSSVX///////+Uv/////////////gAAAAAAASUlKSkpKql' + \
                'S////////+qf/////////////AAAAAAAEkpKUlUpJJCn////////iH///////////wAAAAAAAAAA' + \
                'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' + \
                'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' + \
                'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' + \
                'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH/4B+A8AH/AAAAA' + \
                'AAAAAAAAAAAAAA//AAfwD4H4HwAAf/4H4DwB//gAAAAAAAAAAAAAAAAAD/+AB/APgfgfAAB//wfw' + \
                'PAf/+AAAAAAAAAAAAAgAAAAP/8AH8AfB+D4AAH//B/g8D//4AAAAAAAAAAAADwAAAA//4A/4B8H4' + \
                'PgAAfB+H+DwP4HgAAAAAAAAAAAAPwAAAD4fgD/gHw/w+AAB8D4f8PB+AGAAAAAAAAAAAAA/wAAAP' + \
                'g+Af/AfD/D4AAHwPh/48HwAAAAAAAAAAAAAAB/4AAA+D4B98A+P8PAAAfA+Hvjw+AAAAAAAAAAAA' + \
                'AAAB/4AAD4PgH3wD4/x8AAB8H4e/PD4AAAAAAAAAAAAAAAB/8AAPh8A+PgPn/nwAAH//B5+8Pg/4' + \
                'AH/j/x/4/8f+AA/8AA//wD4+A+eefAAAf/4Hj7w+D/gAf+P/H/j/x/4AA/wAD/+APj4B5554AAB/' + \
                '/AeP/D4P+AB/4/8f+P/H/gAD/AAP/wB8HwH3nvgAAH/wB4f8Pw/4AH/j/x/4/8f+AA/8AA//AH//' + \
                'Af+f+AAAfAAHg/wfAPgAAAAAAAAAAAAAf/AAD5+A//+B/w/4AAB8AAeD/B+A+AAAAAAAAAAAAAH/' + \
                'gAAPj8D//4D/D/AAAHwAB4H8H+D4AAAAAAAAAAAAB/4AAA+H4P//gP8P8AAAfAAHgPwP//gAAAAA' + \
                'AAAAAAAP8AAAD4fh+A/A/w/wAAB8AAeA/Af/+AAAAAAAAAAAAA/AAAAPg/HwB8B+B+AAAHwAB4B8' + \
                'Af/4AAAAAAAAAAAADwAAAA+B+fAHwH4H4AAAfAAHgHwAf4AAAAAAAAAAAAAIAAAAD4H/8Afgfgfg' + \
                'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' + \
                'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' + \
                'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' + \
                'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' + \
                'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' + \
                'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' + \
                'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' + \
                'AAAAAAAAAAAAAAAAAAAAAAAAClAxLDEK'
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
            return {
                "type": "ir.actions.print.data",
                "res_model": self._name,
                "res_id": printer.id,
                "printer_name": printer_name,
                "file_path": data,
                "printer_config_dict": printer_config_dict,
                "context": self.env.context,
            }
