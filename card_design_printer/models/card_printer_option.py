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
    ], string=_("Color Type"),
        default="color",
        help="Valid values [color | grayscale | blackwhite]"
    )
    interpolation = fields.Selection([
        ("none", "Null"),
        ("bicubic", "bicubic"),
        ("bilinear", "bilinear"),
        ("nearest-neighbor", "nearest-neighbor"),
    ], string=_("Interpolation"), default="none", help="Valid \
    values [bicubic | bilinear | nearest-neighbor]. \
    Controls how images are handled when resized.")
    orientation = fields.Selection([
        ("none", "Null"),
        ("portrait", "Portrait"),
        ("landscape", "Landscape"),
        ("reverse-landscape", "Reverse-landscape"),
    ], string=_("orientation"), default="none", help="Valid values [portrait | landscape | reverse-landscape]")
    paperThickness = fields.Integer(
        string=_("Paper Thickness")
    )
    printerTray = fields.Char(
        string=_("Printer Tray")
    )
    rotation = fields.Integer(
        string=_("Rotation"),
        help="Image rotation in degrees."
    )
    rasterize = fields.Boolean(
        string=_("Rasterize"),
        help="Whether documents should be rasterized before printing. \
        Forced TRUE if [options.density] is specified.", default=True
    )
    scaleContent = fields.Boolean(
        string=_("Scale Content"), default=True,
        help="Scales print content to page size, keeping ratio."
    )
    encoding = fields.Char(
        string=_("Encoding")
    )
    endOfDoc = fields.Char(
        string=_("EndOfDoc")
    )
    perSpool = fields.Integer(
        string=_("perSpool"),
        help="Number of pages per spool."
    )
    copies = fields.Integer(
        string=_("Copies"),
        help="Number of copies to be printed."
    )
    density = fields.Integer(
        string=_("Density"),
        help="Pixel density (DPI, DPMM, or DPCM depending on [options.units]). \
        If provided as an array, uses the first supported density found \
        (or the first entry if none found)."
    )
    duplex = fields.Boolean(
        string=_("Duplex"),
        help="Double sided printing"
    )
    fallbackDensity = fields.Integer(
        string=_("FallbackDensity"),
        help="Value used when default density value cannot be read,\
         or in cases where reported as 'Normal' \
         by the driver, (in DPI, DPMM, or DPCM depending on [options.units])."
    )
    top_margin = fields.Integer(
        string=_("Top Margin")
    )
    bottom_margin = fields.Integer(
        string=_("Bottom Margin")
    )
    left_margin = fields.Integer(
        string=_("Left Margin")
    )
    right_margin = fields.Integer(
        string=_("Right Margin"),
    )
    width = fields.Integer(
        string=_("Width"),
        help="Paper size."
    )
    height = fields.Integer(
        string=_("Height"),
        help="Paper size."
    )
    units = fields.Selection([
        ("in", "Inches"),
        ("cm", "cm"),
    ], string=_("Units"), default="in", help="Page units, applies to paper size, \
    margins, and density. ")
    jobName = fields.Char(
        string=_("Job Name"),
        help="Name to display in print queue."
    )
    altPrinting = fields.Boolean(
        string=_("AltPrinting"),
        help="Print the specified file using CUPS \
        command line arguments. Has no effect on Windows."
    )
    legacy = fields.Boolean(
        string=_("Legacy"),
    )

    def get_printer_option(self):
        if self.interpolation:
            if self.interpolation == 'none':
                interpolation = ''
            else:
                interpolation = self.interpolation
        else:
            interpolation = ''

        if self.orientation:
            if self.orientation == 'none':
                orientation = ''
            else:
                orientation = self.orientation
        else:
            orientation = ''

        size = []
        if self.width:
            size.append(self.width)
        if self.height:
            size.append(self.height)

        margins = []
        if self.top_margin:
            margins.append(self.top_margin)
        if self.right_margin:
            margins.append(self.right_margin)
        if self.bottom_margin:
            margins.append(self.bottom_margin)
        if self.left_margin:
            margins.append(self.lefy_margin)

        return {
            "colorType": self.colorType and self.colorType or 'color',
            "interpolation": interpolation,
            "orientation": orientation,
            "paperThickness": self.paperThickness or '',
            "printerTray": self.printerTray or '',
            "rotation": self.rotation and str(self.rotation) or str(0),
            "scaleContent": self.scaleContent or False,
            "encoding": self.encoding and str(self.encoding) or '',
            "endOfDoc": self.endOfDoc or '',
            "perSpool": self.perSpool and str(self.perSpool) or str(1),
            "copies": self.copies and str(self.copies) or str(1),
            "density": self.density and str(self.density) or '',
            "duplex": self.duplex or False,
            "fallbackDensity": self.fallbackDensity and str(self.fallbackDensity) or '',
            "margins": margins and str(margins) or str(0),
            "size": size and str(size) or None,
            "units": self.units or 'in',
            "jobName": self.jobName or self.name or 'Demo',
            "altPrinting": self.altPrinting or False,
            "rasterize": self.rasterize or False,
            "legacy": self.legacy or False,
        }
