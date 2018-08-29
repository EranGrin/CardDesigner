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
                path_data = False
                base64_data = False
                svg_file_name = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
                context = dict(self.env.context or {})
                context.update({
                    'product_coupon': True,
                    'product_coupon_name': coupon.name,
                })
                current_obj_name = coupon.name.replace(' ', '_').replace('.', '_').lower() + '_'
                if self.position == 'f':
                    if self.template_id.data_format == 'pdf':
                        svg_file_name = current_obj_name + 'front_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.pdf'
                        path, data_file, base64_datas = self.template_id.with_context(context).render_pdf(
                            svg_file_name, self.template_id.body_html, '_front_side'
                        )
                    else:
                        svg_file_name = current_obj_name + 'front_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.png'
                        path, data_file, base64_datas = self.template_id.with_context(context).render_png(
                            svg_file_name, self.template_id.body_html, '_front_side'
                        )
                else:
                    if self.template_id.data_format == 'pdf':
                        svg_file_name = current_obj_name + 'back_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.pdf'
                        path, data_file, base64_datas = self.template_id.with_context(context).render_pdf(
                            svg_file_name, self.template_id.back_body_html, '_back_side'
                        )
                    else:
                        svg_file_name = current_obj_name + 'back_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.png'
                        path, data_file, base64_datas = self.template_id.with_context(context).render_png(
                            svg_file_name, self.template_id.back_body_html, '_back_side'
                        )
                path_data = path
                base64_data = base64_datas
                data_list.append((path_data, base64_data))
            if self.position == 'f':
                context.update({
                    'front_side': True,
                })
            index, print_data = self.template_id.with_context(context).create_json_print_data(data_list)
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
