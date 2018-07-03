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
    def export_pdf(self):
        pdf_file = False
        context = dict(self.env.context or {})
        if context.get('back_side', False):
            pdf_file = self.template_id.print_back_side_pdf(self.name)
        elif context.get('both_side', False):
            pdf_file = self.template_id.print_both_side_pdf(self.name)
        else:
            pdf_file = self.template_id.print_pdf(self.name)
        return pdf_file
