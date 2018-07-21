# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# Part of LICENSE file for copyright and licensing details.

{
    'name': "Gift Card Designer",
    'summary': """
        Gift Card Desiner Module for Odoo""",
    'description': """
       Gift Card Desiner Module for Odoo
    """,
    'author': "Inceptus.io",
    'website': "http://www.inceptus.io",
    'category': 'Tools',
    'version': '10.0.2018.07.14.1',
    'depends': ['card_design', 'ies_giftcards'],
    'data': [
        'views/coupon_view.xml',
        'wizard/wiz_card_coupon_view.xml',
    ],
    'qweb': [
    ],
    'application': True,
}
