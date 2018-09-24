# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# See LICENSE file for copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import datetime


class CardPrintWizard(models.TransientModel):
    _inherit = 'card.print.wizard'

    nondulpex_type = fields.Selection([
        ('bulk', 'Bulk'), ('nobulk', 'Nonbulk')
    ], "Duplex Type", default='bulk')
    type = fields.Selection(
        related='template_id.type',
        string="Type",
        store=True,
        readonly=True
    )
    duplex_type = fields.Selection(
        related='template_id.duplex_type',
        string="Duplex Typr",
        store=True,
        readonly=True
    )

    @api.multi
    def print_douplex(self):
        URL = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
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
            if printer.keypair_id:
                printer_config_dict.update({
                    'keypair': {'keys': printer.keypair_id.certificate},
                })
            printer_name = rec.printer_id.name
            context = dict(self.env.context or {})
            print_data_dict = {}
            for i, coupon in enumerate(self.env['product.coupon'].browse(context.get('active_ids'))):
                context = dict(self.env.context or {})
                context.update({
                    'product_coupon': True,
                    'product_coupon_name': coupon.name,
                })
                current_obj_name = coupon.name.replace(' ', '_').replace('.', '_').lower() + '_'
                if rec.template_id.data_format == 'pdf':
                    svg_file_name = current_obj_name + 'front_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.pdf'
                    front_path, front_data_file, front_base64_datas = rec.template_id.with_context(context).render_pdf(
                        svg_file_name, rec.template_id.body_html, '_front_side'
                    )
                    svg_file_name = current_obj_name + 'back_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.pdf'
                    back_path, back_data_file, back_base64_datas = rec.template_id.with_context(context).render_pdf(
                        svg_file_name, rec.template_id.back_body_html, '_back_side'
                    )
                else:
                    svg_file_name = current_obj_name + 'front_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.png'
                    front_path, front_data_file, front_base64_datas = rec.template_id.with_context(context).render_png(
                        svg_file_name, rec.template_id.body_html, '_front_side'
                    )
                    svg_file_name = current_obj_name + 'back_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.png'
                    back_path, back_data_file, back_base64_datas = rec.template_id.with_context(context).render_png(
                        svg_file_name, rec.template_id.back_body_html, '_back_side'
                    )
                if rec.template_id.print_data_type == 'path':
                    index, print_data = rec.template_id.create_json_duplex_data(URL + front_path, URL + back_path)
                else:
                    index, print_data = rec.template_id.create_json_duplex_data(front_base64_datas, back_base64_datas)
                print_data_dict.update({
                    index + i: print_data[0]
                })

            action_type = "ir.actions.multi.printduplex"
            context = dict(self.env.context or {})
            if context.get('active_ids', []):
                if len(context.get('active_ids')) >= 2:
                    action_type = 'ir.actions.print.multiduplex'

            action = {
                "type": action_type,
                "res_model": self._name,
                "res_id": printer.id,
                "printer_name": printer_name,
                "print_data": print_data_dict,
                'print_data_len': i,
                "printer_config_dict": printer_config_dict,
                "context": self.env.context,
            }
            context = dict(self.env.context or {})
            for rec in self.env[context.get('active_model')].browse(context.get('active_ids')):
                if self.template_id and self.template_id.is_printed:
                    query = """UPDATE %s SET printed=true WHERE id = %s""" % (
                        self.env[context.get('active_model')]._table, rec.id
                    )
                    self.env.cr.execute(query)
            return action

    @api.multi
    def print_nondouplex(self):
        URL = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
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
            if printer.keypair_id:
                printer_config_dict.update({
                    'keypair': {'keys': printer.keypair_id.certificate},
                })
            printer_name = rec.printer_id.name
            context = dict(self.env.context or {})
            print_data_dict = {}
            for i, coupon in enumerate(self.env['product.coupon'].browse(context.get('active_ids'))):
                context = dict(self.env.context or {})
                context.update({
                    'product_coupon': True,
                    'product_coupon_name': coupon.name,
                })
                current_obj_name = coupon.name.replace(' ', '_').replace('.', '_').lower() + '_'
                if rec.template_id.data_format == 'pdf':
                    svg_file_name = current_obj_name + 'front_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.pdf'
                    front_path, front_data_file, front_base64_datas = rec.template_id.with_context(context).render_pdf(
                        svg_file_name, rec.template_id.body_html, '_front_side'
                    )
                else:
                    svg_file_name = current_obj_name + 'front_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.png'
                    front_path, front_data_file, front_base64_datas = rec.template_id.with_context(context).render_png(
                        svg_file_name, rec.template_id.body_html, '_front_side'
                    )
                if rec.template_id.print_data_type == 'path':
                    index, print_data = rec.template_id.create_json_nonduplex_front_data(URL + front_path)
                else:
                    index, print_data = rec.template_id.create_json_nonduplex_front_data(front_base64_datas)
                print_data_dict.update({
                    index + i: print_data
                })
            dict_context = dict(self.env.context or {})
            dict_context.update({'is_gift_card': True})
            dict_context.update({'gift_card_ids': context.get('active_ids')})
            printer_option = rec.template_id.get_printer_option()
            action_type = "ir.actions.multi.printnonduplex"
            context = dict(self.env.context or {})
            if context.get('active_ids', []):
                if len(context.get('active_ids')) >= 2:
                    action_type = 'ir.actions.multi.printmultinonduplex'

            action = {
                "type": action_type,
                "res_model": self._name,
                "res_id": rec.template_id.id,
                "printer_name": printer_name,
                "print_data": print_data_dict,
                'print_data_len': i,
                "printer_config_dict": printer_config_dict,
                "context": dict_context,
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

    @api.multi
    def print_nondouplex_nobulk(self):
        context = dict(self.env.context or ())
        next_ids = context.get('active_ids', [])
        if not self.printer_id:
            raise UserError(_("Please select the printer"))
        if not next_ids:
            raise UserError(_("Please select the gift card record"))
        for coupon in self.env['product.coupon'].browse(next_ids):
            context.update({
                'default_template_id': self.template_id.id,
                'default_is_front_side': True,
                'next_ids': next_ids,
                'default_coupon_id': coupon.id,
                'default_printer_id': self.printer_id.id,
            })
            cxt = dict(self.env.context or {})
            for rec in self.env[cxt.get('active_model')].browse(cxt.get('active_ids')):
                if self.template_id and self.template_id.is_printed:
                    query = """UPDATE %s SET printed=true WHERE id = %s""" % (
                        self.env[cxt.get('active_model')]._table, rec.id
                    )
                    self.env.cr.execute(query)
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'wizard.non.duplex.print',
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new',
                'context': context,
            }


class WizardDoubleSidePrint(models.TransientModel):
    _inherit = 'wizard.double.side.print'

    @api.multi
    def print_data(self):
        context = dict(self.env.context or {})
        if self.template_id:
            if context.get('is_gift_card', False):
                return self.template_id.with_context(context).qz_double_nonduplex_gift()
        return super(WizardDoubleSidePrint, self).print_data()


class WizardnondupluexPrint(models.TransientModel):
    _name = 'wizard.non.duplex.print'
    _rec_name = 'template_id'

    printer_id = fields.Many2one(
        "printer.lines",
        string=_("Printer"),
    )
    template_id = fields.Many2one(
        'card.template',
        string='Template'
    )
    is_front_side = fields.Boolean("is front side")
    coupon_id = fields.Many2one(
        "product.coupon",
        string=_("Gift Card"),
    )

    @api.model
    def default_get(self, fields):
        context = dict(self.env.context or {})
        res = super(WizardnondupluexPrint, self).default_get(fields)
        res.update({
            'template_id': context.get('default_template_id', False),
            'is_front_side': context.get('default_is_front_side', False),
            'printer_id': context.get('default_printer_id', False),
            'coupon_id': context.get('default_coupon_id', False),
        })
        return res

    @api.multi
    def print_data_front(self):
        URL = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
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
            printer_name = rec.printer_id.name
            print_data_dict = {}
            context = dict(self.env.context or {})
            context.update({
                'product_coupon': True,
                'product_coupon_name': rec.coupon_id.name,
            })
            current_obj_name = rec.coupon_id.name.replace(' ', '_').replace('.', '_').lower() + '_'
            if rec.template_id.data_format == 'pdf':
                svg_file_name = current_obj_name + 'front_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.pdf'
                front_path, front_data_file, front_base64_datas = rec.template_id.with_context(context).render_pdf(
                    svg_file_name, rec.template_id.body_html, '_front_side'
                )
            else:
                svg_file_name = current_obj_name + 'front_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.png'
                front_path, front_data_file, front_base64_datas = rec.template_id.with_context(context).render_png(
                    svg_file_name, rec.template_id.body_html, '_front_side'
                )
            if rec.template_id.print_data_type == 'path':
                index, print_data = rec.template_id.create_json_nonduplex_front_data(URL + front_path)
            else:
                index, print_data = rec.template_id.create_json_nonduplex_front_data(front_base64_datas)
            print_data_dict.update({
                0: print_data
            })
            context.update({
                'template_id': rec.template_id.id,
                'is_front_side': True,
                'printer_id': rec.printer_id.id,
                'coupon_id': rec.coupon_id.id,
                'next_ids': context.get('next_ids', [])
            })
            printer_option = rec.template_id.get_printer_option()
            action = {
                "type": "ir.actions.multi.nonbulk",
                "res_model": self._name,
                "res_id": rec.template_id.id,
                "printer_name": printer_name,
                "print_data": print_data_dict,
                'print_data_len': 1,
                "printer_config_dict": printer_config_dict,
                "context": context,
                "printer_option": printer_option,
            }
            return action

    @api.multi
    def print_data_back(self):
        URL = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
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
            printer_name = rec.printer_id.name
            print_data_dict = {}
            context = dict(self.env.context or {})
            context.update({
                'product_coupon': True,
                'product_coupon_name': rec.coupon_id.name,
            })
            current_obj_name = rec.coupon_id.name.replace(' ', '_').replace('.', '_').lower() + '_'
            if rec.template_id.data_format == 'pdf':
                svg_file_name = current_obj_name + 'back_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.pdf'
                front_path, front_data_file, front_base64_datas = rec.template_id.with_context(context).render_pdf(
                    svg_file_name, rec.template_id.back_body_html, '_back_side'
                )
            else:
                svg_file_name = current_obj_name + 'back_side_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.png'
                front_path, front_data_file, front_base64_datas = rec.template_id.with_context(context).render_png(
                    svg_file_name, rec.template_id.back_body_html, '_back_side'
                )
            if rec.template_id.print_data_type == 'path':
                index, print_data = rec.template_id.create_json_nonduplex_front_data(URL + front_path)
            else:
                index, print_data = rec.template_id.create_json_nonduplex_front_data(front_base64_datas)
            print_data_dict.update({
                0: print_data
            })
            next_ids = context.get('next_ids', [])
            next_id = []
            if next_ids:
                if rec.coupon_id.id in next_ids:
                    next_ids.remove(rec.coupon_id.id)
                if next_ids:
                    next_id = next_ids[0]
            context.update({
                'template_id': rec.template_id.id,
                'is_front_side': False,
                'printer_id': rec.printer_id.id,
                'coupon_id': next_id,
                'next_ids': next_ids
            })
            printer_option = rec.template_id.get_printer_option()
            action = {
                "type": "ir.actions.multi.nonbulk",
                "res_model": self._name,
                "res_id": rec.template_id.id,
                "printer_name": printer_name,
                "print_data": print_data_dict,
                'print_data_len': 1,
                "printer_config_dict": printer_config_dict,
                "context": context,
                "printer_option": printer_option,
            }
            return action
