# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# Part of LICENSE file for copyright and licensing details.
{
    'name': "Print Gift Card",
    'version': '10.0.2018.08.29.1',
    'summary': """Print Gift Card""",
    'description': """Print Gift Card""",
    'author': "Inceptus.io",
    'website': "http://www.inceptus.io",
    'category': 'Tools',
    "depends": [
        'gift_card_design',
        'card_design_printer',
    ],
    'data': [
        'wizard/wiz_card_coupon_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
}
