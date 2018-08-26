# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# Part of LICENSE file for copyright and licensing details.

{
    'name': "Gift Card Template Designer",
    'summary': """
        Gift Card Template Designer""",
    'description': """
       Gift Card Template Designer
    """,
    'author': "Inceptus.io",
    'website': "http://www.inceptus.io",
    'category': 'Tools',
    'version': '10.0.2018.08.14.1',
    'depends': [
        'card_design',
        'ies_giftcards'
    ],
    'data': [
        'data/sequence.xml',
        'views/coupon_view.xml',
        'wizard/wiz_card_coupon_view.xml',
    ],
    'qweb': [
    ],
    'application': True,
}
