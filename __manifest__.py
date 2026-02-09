# -*- coding: utf-8 -*-
{
    'name': 'Model Browser',
    'version': '1.0.0',
    'category': 'Technical',
    'summary': 'Browse all Odoo models - like "All Functions" in 1C',
    'description': """
        Quick access to all models in your Odoo database.
        - Search bar with instant filtering
        - List all models with their technical names
        - One-click navigation to model list view
        - Keyboard shortcut: Alt+M
    """,
    'author': 'Custom',
    'depends': ['web'],
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'model_browser/static/src/js/model_browser.js',
            'model_browser/static/src/xml/model_browser.xml',
            'model_browser/static/src/scss/model_browser.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

