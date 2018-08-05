# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# Part of LICENSE file for copyright and licensing details.
{
    'name': "Card Designer",
    'summary': """
        Card Designer Module for Odoo""",
    'description': """
        Card Designer Module for Odoo
    """,
    'author': "Inceptus.io",
    'website': "http://www.inceptus.io",
    'category': 'Tools',
    'version': '10.0.2018.08.06.1',
    'depends': [
        'web_editor',
        'mail',
        'web_kanban_gauge',
        'base_setup',
        'report',
    ],
    'external_dependencies': {
        'python': [
            'imgkit', 'weasyprint', 'PyPDF2', 'PIL'
        ],
    },
    'data': [
        'data/svg_data.xml',
        'wizard/card_print_view.xml',
        'views/card_design_template.xml',
        'views/card_template_view.xml',
        'security/ir.model.access.csv',
        'views/editor_field_html.xml',
        'views/themes_templates.xml',
        'views/snippets_themes.xml',
        'views/snippets_themes_options.xml',
        'data/card_design_emai_template.xml',
    ],
    'qweb': [
        '/card_design/static/src/xml/card_design.xml',
        '/card_design/static/src/xml/colorpicker.xml'
    ],
    'application': True,
}
