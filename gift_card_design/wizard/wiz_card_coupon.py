# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# See LICENSE file for copyright and licensing details.
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CardCouponWizard(models.TransientModel):
    _name = 'wiz.card.coupon'

    template_id = fields.Many2one(
        'card.template', 'Card Template', required=1, ondelete='cascade',
    )
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
        if len(res_ids) >= 1:
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
        for rec in self.env['product.coupon'].browse(context.get('active_ids')):
            if self.template_id and self.template_id.combine_pdf_page:
                context.update({'product_coupon_name': rec.name})
                attachment = self.template_id.with_context(context).print_merge_pdf_export(rec.name)
                attachment_list.append(attachment.id)
            else:
                if self.position == 'f':
                    context.update({'product_coupon_name': rec.name + '_front'})
                    attachment = self.template_id.with_context(context).pdf_generate(self.template_id.body_html, 'front_side')
                    attachment_list.append(attachment.id)
                if self.position == 'b' and self.template_id.back_side:
                    context.update({'product_coupon_name': rec.name + '_back'})
                    attachment = self.template_id.with_context(context).pdf_generate(self.template_id.back_body_html, 'back_side')
                    attachment_list.append(attachment.id)
                elif self.position == 'b' and not self.template_id.back_side:
                    raise UserError(_("Please select back side design in template"))
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
