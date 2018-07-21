# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# See LICENSE file for copyright and licensing details.
from odoo import models, fields, api
import imgkit
from bs4 import BeautifulSoup
from lxml import etree


class CardPrintWizard(models.TransientModel):
    _name = 'card.print.wizard'

    @api.model
    def _get_model(self):
        model = self._context.get('active_model')
        model_id = self.env['ir.model'].search([('model', '=', model)], limit=1)
        return model_id

    @api.model
    def get_template(self):
        card_template = self.env['card.template'].search(
            [('card_model', '=', self._context.get('active_model'))],
            limit=1
        )
        return card_template

    template_id = fields.Many2one(
        'card.template', 'Card Template', required=1, ondelete='cascade',
    )
    printers = fields.Selection([('A', "Printer A"), ('B', "Printer B")], "Printers")
    model = fields.Many2one('ir.model', default=_get_model)
    position = fields.Selection([
        ('f', 'Front'), ('b', 'Back')
    ], "Position", default='f')
    body = fields.Html("Card Body")

    @api.onchange('template_id')
    def _preview_body(self):
        if self.template_id:
            model = self._context.get('active_model')
            res_ids = self._context.get('active_ids')
            if len(res_ids) == 1:
                if self.template_id.front_side:
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
        if len(res_ids) == 1:
            if self.template_id.front_side:
                if self.position != 'f':
                    template = self.env['card.template'].render_template(
                        self.template_id.back_body_html, model, res_ids
                    )
                else:
                    template = self.env['card.template'].render_template(
                        self.template_id.body_html, model, res_ids
                    )
                self.body = template.get(res_ids[0])

    @api.multi
    def action_send_email(self):
        self.ensure_one()
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
        attachment = self.template_id.pdf_generate(self.template_id.body_html, 'front_side')
        attachment_list.append(attachment.id)
        if self.template_id.back_side:
            attachment = self.template_id.pdf_generate(self.template_id.back_body_html, 'back_side')
            attachment_list.append(attachment.id)
        template = self.env['mail.template'].browse(template_id)
        template.attachment_ids = [(6, 0, attachment_list)]
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

    @api.multi
    def print_card(self):
        for rec in self:
            import urlparse
            template_body = rec.body
            soup = BeautifulSoup(template_body, 'html.parser')

            # converts relative image urls to absolute url for img tag
            for img in soup.find_all('img'):
                formatted_url = urlparse.urljoin('http://0.0.0.0:8010/', img['src'])
                img['src'] = formatted_url.encode('utf-8')
            template_body = str(soup)

            # converts relative backgroung-image sytle urls to absolute url for section tag
            soup = BeautifulSoup(template_body, 'html.parser')
            section_list = soup.find_all('section')

            for section in section_list:
                if not section.get('style'):
                    continue
                div_style = section['style']
                css_styles = div_style.split(';')
                for style in css_styles:
                    if 'background-image' in style:
                        s = style.split(':')[-1].strip()
                        start = s.find("url('")
                        end = s.find("');")
                        url = s[start + len("url('") + 1:end - 1]
                        formatted_url = urlparse.urljoin('http://0.0.0.0:8010/', url)
                        css_styles[css_styles.index(style)] = "background-image: url(%s)" % (formatted_url)
                section['style'] = ';'.join(css_styles)
            template_body = str(soup)

            body_lxml = BeautifulSoup(template_body, 'lxml')
            doc = etree.XML(str(body_lxml))
            i = 1
            for node in doc.xpath("//div[contains(@class, 'o_designer_wrapper_td')]"):
                to_image = etree.tostring(node, method='xml')
                config = imgkit.config(wkhtmltoimage='/usr/local/bin/wkhtmltoimage')
                options = {'--format': 'jpg',
                           # '--height': 550,
                           '--width': 350
                           }
                imgkit.from_string(to_image, '/tmp/card_%d.jpg' % i, options=options, config=config)
                i += 1

    @api.multi
    def print_both_side(self):
        context = dict(self.env.context or {})
        context['active_id'] = self.template_id.id
        context['both_side'] = True
        return {
            'name': 'Enter file name with out extension',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'card.export.wizard',
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new',
            'nodestroy': True,
        }

    @api.multi
    def print_png(self):
        context = dict(self.env.context or {})
        context['active_id'] = self.template_id.id
        if self.position and self.position == 'b':
            context['back_side'] = True
        context['png'] = True
        return {
            'name': 'Enter file name with out extension',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'card.export.wizard',
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new',
            'nodestroy': True,
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
