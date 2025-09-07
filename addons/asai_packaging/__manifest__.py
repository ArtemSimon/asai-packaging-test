{
    'name': 'ASAI Packaging Control',
    'version': '1.0',
    'summary': 'Control and track packaging of furniture orders',
    'description': """
        Module for tracking packaging process:
        - Define packaging orders
        - Mark parts as packed
        - Prevent completion until all parts are packed
        - Operator name
        - Reset and complete actions
    """,
    'category': 'Inventory/Inventory',
    'author': 'Artem',
    'depends': ['base','web'],
    'data': [
        'security/ir.model.access.csv',
        'views/packaging_order_views.xml',
        'views/packaging_menu.xml',
        'views/packer_report_views.xml', 
        'views/cancelled_report_views.xml', 
        'views/packaging_label_template.xml',
        'views/packaging_cancel_views.xml',
    ],
    'assets': {
    'web.assets_backend': [
        'asai_packaging/static/src/js/reload_with_notification.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto-install': False,
}