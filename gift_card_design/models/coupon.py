# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# See LICENSE file for copyright and licensing details.
from odoo import _, models, fields
import datetime


class ProductCoupon(models.Model):
    _inherit = 'product.coupon'
    _card_designer = _('Coupon')


class card_template(models.Model):
    _inherit = 'card.template'

    combine_pdf_page = fields.Boolean('Combine Pdf Page')

    def get_name(self, value, extension):
        context = dict(self.env.context or {})
        name = super(card_template, self).get_name(value, extension)
        if context.get('product_coupon', False):
            if context.get('product_coupon_name', False):
                name = context.get('product_coupon_name') + '_' + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + extension
        return name

    def get_image(self, value, width, height):
        context = dict(self.env.context or {})
        if context.get('product_coupon', False):
            if context.get('product_coupon_name', False):
                value = context.get('product_coupon_name')
        return super(card_template, self).get_image(value, width, height)
