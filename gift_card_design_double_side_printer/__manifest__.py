# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# Part of LICENSE file for copyright and licensing details.
{
    'name': "Print Gift Card Double Side",
    'version': '10.0.2018.08.30.1',
    'summary': """Print Gift Card Double Side""",
    'description': """Print Gift Card Double Side""",
    'author': "Inceptus.io",
    'website': "http://www.inceptus.io",
    'category': 'Tools',
    "depends": [
        'card_design',
        'gift_card_design',
        'gift_card_design_printer',
        'card_design_double_side_print',
    ],
    'data': [
        'wizard/wiz_card_coupon_view.xml',
        'views/printer_template.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
}
