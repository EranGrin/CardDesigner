# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# Part of LICENSE file for copyright and licensing details.
from odoo import models, fields, _


class CardTemplate(models.Model):
    _inherit = 'card.template'

    colorType = fields.Selection([
        ("color", "Color"),
        ("grayscale", "Grayscale"),
        ("blackwhite", "Black White"),
    ], string=_("Color Type"), default="color")
    interpolation = fields.Selection([
        ("none", "Null"),
        ("bicubic", "bicubic"),
        ("bilinear", "bilinear"),
        ("nearest-neighbor", "nearest-neighbor"),
    ], string=_("Interpolation"), default="none")
    paperThickness = fields.Integer(
        string=_("Paper Thickness")
    )
    printerTray = fields.Char(
        string=_("Printer Tray")
    )
    rotation = fields.Integer(
        string=_("Rotation")
    )
    scaleContent = fields.Boolean(
        string=_("Scale Content"),
    )
    encoding = fields.Char(
        string=_("Encoding")
    )
    endOfDoc = fields.Char(
        string=_("EndOfDoc")
    )
    perSpool = fields.Integer(
        string=_("perSpool")
    )

    def get_printer_option(self):
        if self.interpolation:
            if self.interpolation == 'none':
                interpolation = ''
            else:
                interpolation = self.interpolation
        else:
            interpolation = ''
        return {
            "colorType": self.colorType and self.colorType or 'color',
            "interpolation": interpolation,
            "paperThickness": self.paperThickness or '',
            "printerTray": self.printerTray or '',
            "rotation": self.rotation or 0,
            "scaleContent": self.scaleContent,
            "encoding": self.encoding or '',
            "endOfDoc": self.endOfDoc or '',
            "perSpool": self.perSpool or 1
        }
