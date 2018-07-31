# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# Part of LICENSE file for copyright and licensing details.
{
    'name': "Card Template to Printer",
    'version': '10.0.2018.07.31.1',
    'summary': """
        Card Template to printer""",
    'description': """
        Card Template to printer
    """,
    'author': "Inceptus.io",
    'website': "http://www.inceptus.io",
    'category': 'Tools',
    "depends": [
        'card_design'
    ],
    'data': [
        "security/ir.model.access.csv",
        "views/printer_template.xml",
        "views/printer_view.xml",
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
}
