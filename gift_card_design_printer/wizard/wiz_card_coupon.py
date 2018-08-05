# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# See LICENSE file for copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime


class CardPrintWizard(models.TransientModel):
    _inherit = 'card.print.wizard'

    printer_id = fields.Many2one(
        "printer.lines",
        string=_("Printer"),
    )

    @api.multi
    def print_coupons(self):
        for rec in self:
            if not rec.printer_id:
                raise UserError(_("Please select the printer"))
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
            printer_name = rec.printer_id.name
            context = dict(self.env.context or {})
            data_list = []
            for coupon in self.env['product.coupon'].browse(context.get('active_ids')):
                svg_file_name = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                context.update({
                    'product_coupon': True,
                    'product_coupon_name': coupon.name,
                })
                if self.position == 'f':
                    path, data_file, base64_datas = self.template_id.with_context(context).render_png(
                        svg_file_name, self.template_id.body_html, '_front_side'
                    )
                else:
                    path, data_file, base64_datas = self.template_id.with_context(context).render_png(
                        svg_file_name, self.template_id.back_body_html, '_back_side'
                    )
                if self.template_id.print_data_type == 'path':
                    data = 'card_design/static/src/export_files/' + path
                else:
                    data = 'data:image/png;base64,' + base64_datas
                data_list.append(data)
            index, print_data = self.template_id.create_json_print_data(data_list)
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
            if self.template_id.printer_lang == 'EPL':
                action.update({
                    'epl_x': self.template_id.epl_x,
                    'epl_y': self.template_id.epl_y,
                })
            elif self.template_id.printer_lang == 'EVOLIS':
                action.update({
                    'precision': self.template_id.precision,
                    'overlay': self.template_id.overlay,
                })
            return action
