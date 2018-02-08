# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# See LICENSE file for copyright and licensing details.

from odoo import models,  _


class Employee(models.Model):

    _inherit = 'hr.employee'

    _card_designer = _('Employee')


# class Coupons(models.Model):
#
#     _inherit = 'product.coupon'
#
#     _card_designer = _('Coupons')
