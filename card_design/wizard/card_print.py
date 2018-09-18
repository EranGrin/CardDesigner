# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# See LICENSE file for copyright and licensing details.
from odoo import models, fields, api, _
import base64
import zipfile
from BeautifulSoup import BeautifulSoup
import tempfile
import csv
from odoo.exceptions import UserError
import os
from os.path import basename
import datetime


class CardPrintWizard(models.TransientModel):
    _name = 'card.print.wizard'

    @api.model
    def default_get(self, fields):
        res = super(CardPrintWizard, self).default_get(fields)
        context = dict(self.env.context) or {}
        if context.get('active_model', False):
            model_ids = self.env['ir.model'].search([
                ('model', '=', context.get('active_model'))
            ], limit=1)
            if model_ids:
                res.update({
                    'model': model_ids and model_ids[0].id or False,
                })
        return res

    template_id = fields.Many2one(
        'card.template', 'Card Template',
        required=1, ondelete='cascade',
    )
    model = fields.Many2one('ir.model')
    position = fields.Selection([
        ('f', 'Front'),
        ('b', 'Back'),
        ('both', 'Both')
    ], "Position", default='f')
    file_separator = fields.Selection([
        ('single', 'Single'),
        ('combine', 'Combine'),
    ], "Separate Files", default='single',
        help="This Future use only for PDF and also use in Email"
    )
    file_config = fields.Selection([
        ('f', 'Only first front + all back'),
        ('b', ' Only first back + all front'),
        ('both', 'All files'),
        ('combine', 'Combine Front & Back'),
    ], "Type", default='both')
    body = fields.Html("Front Design")
    back_body = fields.Html("Back Design")

    @api.onchange('file_config')
    def onchange_file_config(self):
        for rec in self:
            if rec.file_config == 'combine':
                rec.file_separator = 'combine'
            else:
                rec.file_separator = 'single'

    @api.onchange('template_id')
    def _preview_body(self):
        if self.template_id:
            model = self._context.get('active_model')
            res_ids = self._context.get('active_ids')
            if len(res_ids) >= 1:
                res_ids = [res_ids[0]]
            if res_ids:
                body = self.template_id.body_html
                body = body.replace(
                    'background: url(/web/static/src/img/placeholder.png) no-repeat center;', ''
                )
                template = self.env['card.template'].render_template(
                    body, model, res_ids
                )
                self.body = template.get(res_ids[0])
                if self.position in ['b', 'both'] and self.template_id.back_side:
                    template = self.env['card.template'].render_template(
                        self.template_id.back_body_html, model, res_ids
                    )
                    self.back_body = template.get(res_ids[0])

    @api.onchange('position')
    def _onchange_position(self):
        model = self._context.get('active_model')
        res_ids = self._context.get('active_ids')
        if len(res_ids) >= 1:
            res_ids = [res_ids[0]]
        if res_ids:
            template = self.env['card.template'].render_template(
                self.template_id.body_html, model, res_ids
            )
            self.body = template.get(res_ids[0])
            if self.position in ['b', 'both'] and self.template_id.back_side:
                template = self.env['card.template'].render_template(
                    self.template_id.back_body_html, model, res_ids
                )
                self.back_body = template.get(res_ids[0])

    @api.multi
    def print_pdf(self):
        export_file_path = self.env.ref('card_design.export_file_path').value
        context = dict(self.env.context or {})
        allow_to_zip = self.env.ref('card_design.allow_to_zip').value
        if not self.template_id:
            return True
        attachment_tuple = []
        attachment_list = []
        for cid in context.get('active_ids'):
            context.update({
                'remianing_ids': [cid]
            })
            if self.position == 'both' and self.file_separator == 'combine' and self.template_id.back_side:
                attachment_id = self.template_id.with_context(context).print_merge_pdf_export('_combine')
                attachment_list.append(attachment_id.id)
                attachment_tuple.append(
                    ('f', attachment_id.id)
                )
            else:
                if self.position in ['f', 'both']:
                    attachment_id = self.template_id.with_context(context).pdf_generate(
                        self.template_id.body_html, '_front_side'
                    )
                    attachment_list.append(attachment_id.id)
                    attachment_tuple.append(
                        ('f', attachment_id.id)
                    )
                if self.position in ['b', 'both'] and self.template_id.back_side:
                    attachment_id = self.template_id.with_context(context).pdf_generate(
                        self.template_id.back_body_html, '_back_side'
                    )
                    attachment_tuple.append(('b', attachment_id.id))
                    attachment_list.append(attachment_id.id)
        if self.position in ['both']:
            if self.file_config != 'both' and self.file_separator == 'single':
                front_side_list = filter(lambda x: x[0] == 'f', attachment_tuple)
                back_side_list = filter(lambda x: x[0] == 'b', attachment_tuple)
                updated_attach_list = []
                if self.file_config == 'f':
                    for position, attachment in attachment_tuple:
                        if position == 'f':
                            updated_attach_list.append(attachment)
                            for ps, attch in back_side_list:
                                updated_attach_list.append(attch)
                            break
                if self.file_config == 'b':
                    for position, attachment in attachment_tuple:
                        if position == 'b':
                            updated_attach_list.append(attachment)
                            for ps, attch in front_side_list:
                                updated_attach_list.append(attch)
                            break
                attachment_list = updated_attach_list
        actions = []
        if allow_to_zip:
            maximum_file_downalod = int(allow_to_zip)
            if maximum_file_downalod <= len(attachment_list):
                current_path = os.path.join(os.path.dirname(
                    os.path.abspath(__file__))
                ).replace('/wizard', '/static/src/export_files/')
                # current_path = export_file_path + '/export_files/'
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
                    'card_temp_path': current_path + zip_file_name,
                    'public': True
                })
                attachment_list = []
                attachment_list.append(attachment.id)
        for attachment in attachment_list:
            actions.append({
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s?download=true' % (attachment)
            })
        return {
            'type': 'ir.actions.multi.print',
            'actions': actions,
        }

    @api.multi
    def print_png(self):
        if self.file_separator != 'single':
            raise UserError(_(
                "Combine option will use only for pdf.")
            )
        context = dict(self.env.context or {})
        export_file_path = self.env.ref('card_design.export_file_path').value
        allow_to_zip = self.env.ref('card_design.allow_to_zip').value
        if not self.template_id:
            return True
        attachment_tuple = []
        attachment_list = []
        for cid in context.get('active_ids'):
            context.update({
                'remianing_ids': [cid]
            })
            if self.position in ['f', 'both']:
                attachment_id = self.template_id.with_context(context).png_generate(self.template_id.body_html, '_front_side')
                attachment_list.append(attachment_id.id)
                attachment_tuple.append(('f', attachment_id.id))
            if self.position in ['b', 'both'] and self.template_id.back_side:
                attachment_id = self.template_id.with_context(context).png_generate(self.template_id.back_body_html, '_back_side')
                attachment_list.append(attachment_id.id)
                attachment_tuple.append(('b', attachment_id.id))
        if self.position in ['both']:
            if self.file_config != 'both' and self.file_separator == 'single':
                front_side_list = filter(lambda x: x[0] == 'f', attachment_tuple)
                back_side_list = filter(lambda x: x[0] == 'b', attachment_tuple)
                updated_attach_list = []
                if self.file_config == 'f':
                    for position, attachment in attachment_tuple:
                        if position == 'f':
                            updated_attach_list.append(attachment)
                            for ps, attch in back_side_list:
                                updated_attach_list.append(attch)
                            break
                if self.file_config == 'b':
                    for position, attachment in attachment_tuple:
                        if position == 'b':
                            updated_attach_list.append(attachment)
                            for ps, attch in front_side_list:
                                updated_attach_list.append(attch)
                            break
                attachment_list = updated_attach_list
        actions = []
        if allow_to_zip:
            maximum_file_downalod = int(allow_to_zip)
            if maximum_file_downalod <= len(attachment_list):
                current_path = os.path.join(os.path.dirname(
                    os.path.abspath(__file__))
                ).replace('/wizard', '/static/src/export_files/')
                # current_path = export_file_path + '/export_files/'
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
                    'card_temp_path': current_path.split('/card_design')[1] + zip_file_name,
                    'public': True
                })
                attachment_list = []
                attachment_list.append(attachment.id)
        for attachment in attachment_list:
            actions.append({
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s?download=true' % (attachment)
            })
        return {
            'type': 'ir.actions.multi.print',
            'actions': actions,
        }

    @api.multi
    def action_send_email(self):
        ir_model_data = self.env['ir.model.data']
        export_file_path = self.env.ref('card_design.export_file_path').value
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

        context = dict(self.env.context or {})
        if not self.template_id:
            return True
        attachment_tuple = []
        attachment_list = []
        for cid in context.get('active_ids'):
            context.update({
                'remianing_ids': [cid]
            })
            if self.position == 'both' and self.file_separator == 'combine' and self.template_id.back_side:
                attachment_id = self.template_id.with_context(context).print_merge_pdf_export('_combine')
                attachment_list.append(attachment_id.id)
                attachment_tuple.append(
                    ('f', attachment_id.id)
                )
            else:
                if self.position in ['f', 'both']:
                    attachment_id = self.template_id.with_context(context).pdf_generate(
                        self.template_id.body_html, '_front_side'
                    )
                    attachment_list.append(attachment_id.id)
                    attachment_tuple.append(
                        ('f', attachment_id.id)
                    )
                if self.position in ['b', 'both'] and self.template_id.back_side:
                    attachment_id = self.template_id.with_context(context).pdf_generate(
                        self.template_id.back_body_html, '_back_side'
                    )
                    attachment_tuple.append(('b', attachment_id.id))
                    attachment_list.append(attachment_id.id)

        if self.position in ['both']:
            if self.file_config != 'both' and self.file_separator == 'single':
                front_side_list = filter(lambda x: x[0] == 'f', attachment_tuple)
                back_side_list = filter(lambda x: x[0] == 'b', attachment_tuple)
                updated_attach_list = []
                if self.file_config == 'f':
                    for position, attachment in attachment_tuple:
                        if position == 'f':
                            updated_attach_list.append(attachment)
                            for ps, attch in back_side_list:
                                updated_attach_list.append(attch)
                            break
                if self.file_config == 'b':
                    for position, attachment in attachment_tuple:
                        if position == 'b':
                            updated_attach_list.append(attachment)
                            for ps, attch in front_side_list:
                                updated_attach_list.append(attch)
                            break
                attachment_list = updated_attach_list

        template = self.env['mail.template'].browse(template_id)
        URL = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        body_html = template.body_html
        soup = BeautifulSoup(body_html)
        for tag in soup.findAll("table", {'id': 'attachment_link'}):
            tag.replaceWith('')
        body_html = str(soup)
        current_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__))
        ).replace('/wizard', '/static/src/export_files/')
        # current_path = export_file_path + '/export_files/'
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
        sequence = self.env['ir.sequence'].next_by_code('card.template.csv')
        export_file = tmp_dir + '/' + str(sequence) + '_card_template.csv'
        csv_file = open(export_file, "wb")
        writer = csv.writer(csv_file)
        writer.writerow([
            'Sequence', 'Number', 'Template Name', 'Design Side'
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
            'name': str(sequence) + '_card_template.csv',
            'type': 'binary',
            'mimetype': 'text/csv',
            'datas': file_data,
            'res_model': 'card.template',
            'res_id': self.template_id.id,
            'datas_fname': str(sequence) + '_card_template.csv',
        })
        template.attachment_ids = [(6, 0, [attachment.id, csv_attachment.id])]
        ctx = dict()
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


class CardExportWizard(models.TransientModel):
    _name = 'card.export.wizard'

    name = fields.Char('Name', required=1)
    template_id = fields.Many2one(
        'card.template', 'Card Template', required=1, ondelete='cascade',
    )

    @api.model
    def default_get(self, fields):
        res = super(CardExportWizard, self).default_get(fields)
        context = dict(self.env.context) or {}
        if context.get('active_id', False):
            res.update({
                'template_id': context.get('active_id'),
            })
        return res

    @api.multi
    def export(self):
        file = False
        context = dict(self.env.context or {})
        if context.get('back_side', False):
            if context.get('png', False):
                file = self.template_id.print_back_side_png_export(self.name)
            else:
                file = self.template_id.print_back_side_pdf(self.name)
        elif context.get('both_side', False):
            if context.get('png', False):
                file = self.template_id.print_both_side_png_export(self.name)
            else:
                file = self.template_id.print_both_side_pdf(self.name)
        else:
            if context.get('png', False):
                file = self.template_id.print_png_export(self.name)
            else:
                file = self.template_id.print_pdf(self.name)
        return file
