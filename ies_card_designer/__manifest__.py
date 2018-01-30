# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# See LICENSE file for copyright and licensing details.
{
    'name': "Card Designer",

    'summary': """
        Card Desiner Module for Odoo""",

    'description': """
        Card Desiner Module for Odoo
    """,

    'author': "Inceptus.io",
    'website': "http://www.inceptus.io",

    'category': 'Tools',
    'version': '0.1',

    'depends': ['hr', 'web_editor', 'website', 'mass_mailing'],

    'external_dependencies': {
        'python': ['imgkit'],
    },

    'data': [
        # 'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/card_options.xml',
        'views/card_designer_template.xml',
        'views/card_template_view.xml',
        'wizard/card_print_view.xml',
        'views/snippets.xml',
        'views/snippets_themes_options.xml',
        'views/templates.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
}

# 323.52 x 204 px card size
