# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# See LICENSE file for copyright and licensing details.
from odoo import models, fields


class CardPrintWizard(models.TransientModel):
    _inherit = 'card.print.wizard'

    printer_lang = fields.Selection(
        related='template_id.printer_lang',
        string="Printer Lang",
        store=True,
        readonly=True
    )
    enable_printer = fields.Boolean(
        related='template_id.enable_printer',
        string="Enable Printer",
        store=True,
        readonly=True,
        default=False
    )
