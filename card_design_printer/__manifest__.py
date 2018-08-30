# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# Part of LICENSE file for copyright and licensing details.
{
    'name': "Print Card Template",
    'version': '10.0.2018.08.30.1',
    'summary': """Print Card Template""",
    'description': """Print Card Template""",
    'author': "Inceptus.io",
    'website': "http://www.inceptus.io",
    'category': 'Tools',
    "depends": [
        'card_design',
    ],
    'data': [
        "security/ir.model.access.csv",
        "views/printer_template.xml",
        "views/printer_view.xml",
        "wizard/card_print_view.xml",
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
}
