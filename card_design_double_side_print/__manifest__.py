# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# Part of LICENSE file for copyright and licensing details.
{
    'name': "Double Side Print Data",
    'version': '10.0.2018.08.30.1',
    'summary': """
        Double Side Print Data""",
    'description': """
        Double Side Print Data
    """,
    'author': "Inceptus.io",
    'website': "http://www.inceptus.io",
    'category': 'Tools',
    "depends": [
        'card_design_printer'
    ],
    'data': [
        "views/printer_template.xml",
        "wizard/card_print_view.xml",
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
}
