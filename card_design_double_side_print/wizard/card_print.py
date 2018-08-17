# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# See LICENSE file for copyright and licensing details.
from odoo import models, fields, api


class WizardDoubleSidePrint(models.TransientModel):
    _name = 'wizard.double.side.print'
    _rec_name = 'template_id'

    template_id = fields.Many2one(
        'card.template',
        string='Template'
    )

    @api.model
    def default_get(self, fields):
        context = dict(self.env.context or {})
        res = super(WizardDoubleSidePrint, self).default_get(fields)
        res.update({
            'template_id': context.get('default_template_id', False)
        })
        return res

    @api.multi
    def print_data(self):
        if self.template_id:
            return self.template_id.qz_double_nonduplex_back_print()
        return True
