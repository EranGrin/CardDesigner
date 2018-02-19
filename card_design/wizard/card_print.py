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
        default=get_template
    )
    printers = fields.Selection([('A', "Printer A"), ('B', "Printer B")], "Printers")
    model = fields.Many2one('ir.model', default=_get_model)
    body = fields.Html("Card Body")

    @api.onchange('template_id')
    def _preview_body(self):
        model = self._context.get('active_model')
        res_ids = self._context.get('active_ids')
        if len(res_ids) == 1:
            template = self.env['card.template'].render_template(
                self.template_id.body_html, model, res_ids
            )
            self.body = template.get(res_ids[0])

    @api.multi
    def print_card(self):
        for rec in self:
            import urlparse
            template_body = rec.body
            print "template_body", template_body
            soup = BeautifulSoup(template_body, 'html.parser')

            # converts relative image urls to absolute url for img tag
            for img in soup.find_all('img'):
                formatted_url = urlparse.urljoin('http://0.0.0.0:8010/', img['src'])
                img['src'] = formatted_url.encode('utf-8')
            template_body = str(soup)

            # converts relative backgroung-image sytle urls to absolute url for section tag
            soup = BeautifulSoup(template_body, 'html.parser')
            print dir(soup)
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
