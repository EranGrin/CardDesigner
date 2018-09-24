# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# See LICENSE file for copyright and licensing details.
from odoo import models, fields, _, api
from odoo.exceptions import UserError
import datetime


class CardPrintErrorWizard(models.TransientModel):
    _name = 'card.print.error.wizard'

    name = fields.Text(string="Name")


class CardPrintWizard(models.TransientModel):
    _inherit = 'card.print.wizard'

    printer_id = fields.Many2one(
        "printer.lines",
        string=_("Printer"),
    )
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
    label_front = fields.Selection([
        ("f", "Front"),
    ], string="Position", default="f")
    card_type = fields.Selection(
        related='template_id.type',
        string="Printer Lang",
        store=True,
        readonly=True
    )

    @api.onchange('template_id')
    def _preview_body(self):
        res = super(CardPrintWizard, self)._preview_body()
        for rec in self:
            if rec.template_id and rec.template_id.type == 'label':
                rec.position = 'f'
            else:
                rec.position = 'f'
            rec.file_config = 'f'
            rec.file_separator = "single"
        return res

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
            if printer.keypair_id:
                printer_config_dict.update({
                    'keypair': {'keys': printer.keypair_id.certificate},
                })
            printer_name = rec.printer_id.name
            context = dict(self.env.context or {})
            data_list = []
            for coupon in self.env[context.get('active_model')].browse(context.get('active_ids')):
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
                data_list.append((path_data, base64_data, coupon.name))
            if self.position == 'f':
                context.update({
                    'front_side': True,
                })
            index, print_data = self.template_id.with_context(context).create_json_print_data(data_list)
            printer_option = self.template_id.get_printer_option()
            action_type = self.get_action_type()
            action = {
                "type": action_type,
                "res_model": self._name,
                "res_id": printer.id,
                "printer_name": printer_name,
                "print_data": print_data,
                'print_data_len': index,
                "printer_config_dict": printer_config_dict,
                "context": self.env.context,
                "printer_option": printer_option,
            }

            context = dict(self.env.context or {})
            for rec in self.env[context.get('active_model')].browse(context.get('active_ids')):
                if self.template_id and self.template_id.is_printed:
                    query = """UPDATE %s SET printed=true WHERE id = %s""" % (
                        self.env[context.get('active_model')]._table, rec.id
                    )
                    self.env.cr.execute(query)
            return action

    def get_action_type(self):
        action = "ir.actions.print.data"
        context = dict(self.env.context or {})
        if context.get('active_ids', []):
            if len(context.get('active_ids')) >= 2:
                action = 'ir.actions.print.multidata'
        return action
