# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# Part of LICENSE file for copyright and licensing details.

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
    'depends': ['hr', 'web_editor', 'mail', 'web_kanban_gauge'],

    'external_dependencies': {
        'python': ['imgkit'],
    },
    'data': [
        'wizard/card_print_view.xml',
        'views/card_design_template.xml',
        'views/card_template_view.xml',
        'security/ir.model.access.csv',
        'views/editor_field_html.xml',
        'views/themes_templates.xml',
        'views/snippets_themes.xml',
        'views/snippets_themes_options.xml',
    ],
    'application': True,
}
