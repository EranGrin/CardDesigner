# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# See LICENSE file for copyright and licensing details.
from odoo import models, api, _
from odoo.exceptions import UserError
import datetime


class CardPrintWizard(models.TransientModel):
    _inherit = 'card.print.wizard'

    @api.multi
    def print_douplex(self):
        for rec in self:
            if not rec.printer_id:
                raise UserError(_("Please select the printer"))
            if not rec.template_id.back_side:
                raise UserError(_("Please select the back side design."))
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
            print_data_dict = {}
            for i, coupon in enumerate(self.env['product.coupon'].browse(context.get('active_ids'))):
                svg_file_name = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
                context = dict(self.env.context or {})
                context.update({
                    'product_coupon': True,
                    'product_coupon_name': coupon.name,
                })
                if rec.template_id.data_format == 'pdf':
                    svg_file_name += '.pdf'
                    front_path, front_data_file, front_base64_datas = rec.template_id.with_context(context).render_pdf(
                        svg_file_name, rec.template_id.body_html, '_front_side'
                    )
                    back_path, back_data_file, back_base64_datas = rec.template_id.with_context(context).render_pdf(
                        svg_file_name, rec.template_id.back_body_html, '_back_side'
                    )
                else:
                    svg_file_name += '.png'
                    front_path, front_data_file, front_base64_datas = rec.template_id.with_context(context).render_png(
                        svg_file_name, rec.template_id.body_html, '_front_side'
                    )
                    back_path, back_data_file, back_base64_datas = rec.template_id.with_context(context).render_png(
                        svg_file_name, rec.template_id.back_body_html, '_back_side'
                    )
                if rec.template_id.double_print_data_type == 'path':
                    index, print_data = rec.template_id.create_json_duplex_data(front_path, back_path)
                else:
                    index, print_data = rec.template_id.create_json_duplex_data(front_base64_datas, back_base64_datas)
                print_data_dict.update({
                    index + i: print_data[0]
                })
            action = {
                "type": "ir.actions.multi.printduplex",
                "res_model": self._name,
                "res_id": printer.id,
                "printer_name": printer_name,
                "print_data": print_data_dict,
                'print_data_len': i,
                "printer_config_dict": printer_config_dict,
                "context": self.env.context,
            }
            return action

    @api.multi
    def print_nondouplex(self):
        for rec in self:
            if not rec.printer_id:
                raise UserError(_("Please select the printer"))
            if not rec.template_id.back_side:
                raise UserError(_("Please select the back side design."))
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
            print_data_dict = {}
            for i, coupon in enumerate(self.env['product.coupon'].browse(context.get('active_ids'))):
                svg_file_name = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
                context = dict(self.env.context or {})
                context.update({
                    'product_coupon': True,
                    'product_coupon_name': coupon.name,
                })
                if rec.template_id.double_print_data_format == 'pdf':
                    svg_file_name += '.pdf'
                    front_path, front_data_file, front_base64_datas = rec.template_id.with_context(context).render_pdf(
                        svg_file_name, rec.template_id.body_html, '_front_side'
                    )
                else:
                    svg_file_name += '.png'
                    front_path, front_data_file, front_base64_datas = rec.template_id.with_context(context).render_png(
                        svg_file_name, rec.template_id.body_html, '_front_side'
                    )
                if rec.template_id.double_print_data_type == 'path':
                    index, print_data = rec.template_id.create_json_nonduplex_front_data(front_path)
                else:
                    index, print_data = rec.template_id.create_json_nonduplex_front_data(front_base64_datas)
                print_data_dict.update({
                    index + i: print_data
                })
            dict_context = dict(self.env.context or {})
            dict_context.update({'is_gift_card': True})
            dict_context.update({'gift_card_ids': context.get('active_ids')})
            action = {
                "type": "ir.actions.multi.printnonduplex",
                "res_model": self._name,
                "res_id": rec.template_id.id,
                "printer_name": printer_name,
                "print_data": print_data_dict,
                'print_data_len': i,
                "printer_config_dict": printer_config_dict,
                "context": dict_context,
            }
            return action


class WizardDoubleSidePrint(models.TransientModel):
    _inherit = 'wizard.double.side.print'

    @api.multi
    def print_data(self):
        context = dict(self.env.context or {})
        if self.template_id:
            if context.get('is_gift_card', False):
                return self.template_id.with_context(context).qz_double_nonduplex_gift()
        return super(WizardDoubleSidePrint, self).print_data()