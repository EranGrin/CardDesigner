# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# See LICENSE file for copyright and licensing details.
from odoo import _, models


class ProductCoupon(models.Model):
    _inherit = 'product.coupon'
    _card_designer = _('Coupon')


class card_template(models.Model):
    _inherit = 'card.template'

    def get_name(self, value, extension):
        context = dict(self.env.context or {})
        if context.get('product_coupon', False):
            if context.get('product_coupon_name', False):
                sequence = self.env['ir.sequence'].next_by_code('product.coupon.export')
                value = str(sequence) + '_' + context.get('product_coupon_name') + value
        elif context.get('active_model', False):
            if context.get('active_model') == 'product.coupon':
                if context.get('remianing_ids', False):
                    coupon_id = context.get('remianing_ids')[0]
                    context.update({
                        'remianing_ids': context.get('remianing_ids')[1:]
                    })
                else:
                    active_ids = context.get('active_ids')
                    coupon_id = active_ids[0]
                    context.update({
                        'remianing_ids': active_ids[1:]
                    })
                coupon = self.env['product.coupon'].browse(coupon_id)
                if coupon:
                    sequence = self.env['ir.sequence'].next_by_code('product.coupon.export')
                    value = str(sequence) + '_' + str(coupon.name) + value
        return super(card_template, self).get_name(value, extension)

    def get_image(self, value, width, height):
        context = dict(self.env.context or {})
        if context.get('product_coupon', False):
            if context.get('product_coupon_name', False):
                value = context.get('product_coupon_name')
        elif context.get('active_model', False):
            if context.get('active_model') == 'product.coupon':
                if context.get('remianing_ids', False):
                    coupon_id = context.get('remianing_ids')[0]
                    context.update({
                        'remianing_ids': context.get('remianing_ids')[1:]
                    })
                else:
                    active_ids = context.get('active_ids')
                    coupon_id = active_ids[0]
                    context.update({
                        'remianing_ids': active_ids[1:]
                    })
                coupon = self.env['product.coupon'].browse(coupon_id)
                if coupon:
                    value = coupon.name
        return super(card_template, self.with_context(context)).get_image(value, width, height)
