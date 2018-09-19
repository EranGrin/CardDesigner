# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# See LICENSE file for copyright and licensing details.
from odoo import models, api
import datetime


class CardTemplate(models.Model):
    _inherit = 'card.template'

    @api.multi
    def qz_double_nonduplex_gift(self):
        URL = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        index = 0
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
            print_data_dict = {}
            dict_context = dict(self.env.context or {})
            i = 0
            for i, coupon in enumerate(self.env['product.coupon'].browse(dict_context.get('gift_card_ids'))):
                context = dict(self.env.context or {})
                context.update({
                    'product_coupon': True,
                    'product_coupon_name': coupon.name,
                })
                current_obj_name = coupon.name.replace(' ', '_').replace('.', '_').lower() + '_'
                if rec.data_format == 'pdf':
                    svg_file_name = current_obj_name + 'back_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.pdf'
                    back_path, data_file, back_base64_datas = rec.with_context(context).render_pdf(
                        svg_file_name, rec.back_body_html, '_back_side'
                    )
                else:
                    svg_file_name = current_obj_name + 'back_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.png'
                    back_path, data_file, back_base64_datas = rec.with_context(context).render_png(
                        svg_file_name, rec.back_body_html, '_back_side'
                    )
                if rec.print_data_type == 'path':
                    index, print_data = rec.create_json_nonduplex_back_data(URL + back_path)
                else:
                    index, print_data = rec.create_json_nonduplex_back_data(back_base64_datas)
                print_data_dict.update({
                    index + i: print_data
                })

            printer_option = rec.get_printer_option()
            action = {
                "type": "ir.actions.multi.backnonduplex",
                "res_model": self._name,
                "res_id": rec.id,
                "printer_name": rec.printer_id.name,
                "print_data": print_data_dict,
                "print_data_len": i,
                "printer_config_dict": printer_config_dict,
                "context": self.env.context,
                "jobName": rec.name,
                "printer_option": printer_option,
            }
            return action
