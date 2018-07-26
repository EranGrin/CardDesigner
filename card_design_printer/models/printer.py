# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# Part of LICENSE file for copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)
from odoo import models, fields, _, api


class Printer(models.Model):
    _name = 'printer.printer'

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
        string=_("usingSecure")
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
        string="Delay",
        required=True,
        default=0
    )

    @api.multi
    def check_connection(self):
        return True

    @api.multi
    def get_printer_list(self):
        return True

    @api.multi
    def set_default_printer(self):
        return True
