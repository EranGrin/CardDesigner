# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# See LICENSE file for copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from BeautifulSoup import BeautifulSoup
import os
from os.path import basename
import datetime
import zipfile
import csv
import tempfile
import base64


class CardCouponWizard(models.TransientModel):
    _name = 'wiz.card.coupon'

    template_id = fields.Many2one(
        'card.template', 'Card Template', required=1, ondelete='cascade',
    )
    position = fields.Selection([
        ('f', 'Front'), ('b', 'Back'), ('both', 'Both')
    ], "Position", default='f')
    body = fields.Html("Card Body")

    @api.onchange('template_id')
    def _preview_body(self):
        if self.template_id:
            model = self._context.get('active_model')
            res_ids = self._context.get('active_ids')
            if len(res_ids) >= 1:
                res_ids = [res_ids[0]]
            if self.position == 'b' and res_ids:
                template = self.env['card.template'].render_template(
                    self.template_id.back_body_html, model, res_ids
                )
                self.body = template.get(res_ids[0])
            else:
                body = self.template_id.body_html
                body = body.replace('background: url(/web/static/src/img/placeholder.png) no-repeat center;', '')
                template = self.env['card.template'].render_template(
                    body, model, res_ids
                )
                self.body = template.get(res_ids[0])

    @api.onchange('position')
    def _onchange_position(self):
        model = self._context.get('active_model')
        res_ids = self._context.get('active_ids')
        if len(res_ids) >= 1:
            res_ids = [res_ids[0]]
        if self.template_id.front_side and res_ids:
            if self.position == 'b':
                template = self.env['card.template'].render_template(
                    self.template_id.back_body_html, model, res_ids
                )
                self.body = template.get(res_ids[0])
            else:
                template = self.env['card.template'].render_template(
                    self.template_id.body_html, model, res_ids
                )
                self.body = template.get(res_ids[0])

    @api.multi
    def action_send_email(self):
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference(
                'card_design', 'email_template_card_design'
            )[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(
                'mail', 'email_compose_message_wizard_form'
            )[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        attachment_list = []
        context = dict(self.env.context or {})
        context.update({'product_coupon': True})
        for rec in self.env['product.coupon'].browse(context.get('active_ids')):
            if self.position == 'f' or self.position == 'both':
                context.update({'product_coupon_name': rec.name})
                attachment = self.template_id.with_context(context).pdf_generate(self.template_id.body_html, '_front_side')
                attachment_list.append(attachment.id)
            if (self.position == 'b' or self.position == 'both') and self.template_id.back_side:
                context.update({'product_coupon_name': rec.name})
                attachment = self.template_id.with_context(context).pdf_generate(self.template_id.back_body_html, '_back_side')
                attachment_list.append(attachment.id)
            elif self.position == 'b' and not self.template_id.back_side:
                raise UserError(_("Please select back side design in template"))
        template = self.env['mail.template'].browse(template_id)
        URL = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        body_html = template.body_html
        soup = BeautifulSoup(body_html)
        for tag in soup.findAll("table", {'id': 'attachment_link'}):
            tag.replaceWith('')
        body_html = str(soup)
        current_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__))
        ).replace('/gift_card_design/wizard', '/card_design/static/src/export_files/')
        current_obj_name = self.template_id.name.replace(' ', '_').replace('.', '_').lower() + '_'
        zip_file_name = current_obj_name + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.zip'
        current_path = current_path + 'zip_files/'
        if not os.path.exists(current_path):
            os.makedirs(current_path)
        zip_file = current_path + zip_file_name
        attachment_zipfile = zipfile.ZipFile(zip_file, 'w')
        for attachment in attachment_list:
            attachment = self.env['ir.attachment'].browse(attachment)
            temp_file_name = current_path.split('/card_design')[0] + attachment.card_temp_path
            attachment_zipfile.write(temp_file_name, basename(temp_file_name))
        attachment_zipfile.close()
        base64_datas = open(current_path + zip_file_name, 'rb').read().encode('base64')
        attachment = self.env['ir.attachment'].create({
            'name': zip_file_name,
            'type': 'binary',
            'mimetype': 'application/zip',
            'datas': base64_datas,
            'res_model': 'card.template',
            'res_id': self.template_id.id,
            'datas_fname': zip_file_name,
            'card_temp_path': "/card_design" + current_path.split('/card_design')[1] + zip_file_name,
            'public': True
        })
        render_html = """ <table id='attachment_link'>
                <tr>
                    <td>
                        <a href='%s/web/content/%s?download=true' data-original-title='%s' title='%s'>%s</a>
                    </td>
                </tr>
                </table>
        """  % (URL, attachment.id, attachment.name, attachment.name, attachment.name)
        body_html += render_html
        template.body_html = body_html
        tmp_dir = tempfile.mkdtemp()
        sequence = self.env['ir.sequence'].next_by_code('product.coupon.csv')
        export_file = tmp_dir + '/' + str(sequence) + '_gift_card.csv'
        csv_file = open(export_file, "wb")
        writer = csv.writer(csv_file)
        writer.writerow([
            'Sequence', 'Gift Card Number', 'Card Template Name', 'Design Side'
        ])
        for att_csv in attachment_list:
            att_csv = self.env['ir.attachment'].browse(att_csv)
            name = att_csv.name.split("_")
            writer.writerow([
                name[0], name[1], self.template_id.name, name[2]
            ])
        csv_file.close()

        fn = open(export_file, 'rb')
        file_data = base64.encodestring(fn.read())
        fn.close()
        csv_attachment = self.env['ir.attachment'].create({
            'name': str(sequence) + '_gift_card.csv',
            'type': 'binary',
            'mimetype': 'text/csv',
            'datas': file_data,
            'res_model': 'card.template',
            'res_id': self.template_id.id,
            'datas_fname': str(sequence) + '_gift_card.csv',
        })
        template.attachment_ids = [(6, 0, [attachment.id, csv_attachment.id])]
        ctx.update({
            'default_model': 'card.template',
            'default_res_id': self.template_id.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
