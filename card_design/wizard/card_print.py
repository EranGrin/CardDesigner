# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# See LICENSE file for copyright and licensing details.
from odoo import models, fields, api


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
            if len(res_ids) >= 1:
                res_ids = [res_ids[0]]
            if self.template_id.front_side and res_ids:
                body = self.template_id.body_html
                body = body.replace(
                    'background: url(/web/static/src/img/placeholder.png) no-repeat center;', ''
                )
                template = self.env['card.template'].render_template(
                    body, model, res_ids
                )
                self.body = template.get(res_ids[0])
            if self.position != 'f' and res_ids:
                template = self.env['card.template'].render_template(
                    self.template_id.back_body_html, model, res_ids
                )
                self.body = template.get(res_ids[0])

    @api.onchange('position')
    def _onchange_position(self):
        model = self._context.get('active_model')
        res_ids = self._context.get('active_ids')
        if len(res_ids) >= 1:
            res_ids = [res_ids[0]]
        if self.template_id.front_side and res_ids:
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
    def print_pdf(self):
        context = dict(self.env.context or {})
        context['active_id'] = self.template_id.id
        if self.position and self.position == 'b':
            context['back_side'] = True
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
