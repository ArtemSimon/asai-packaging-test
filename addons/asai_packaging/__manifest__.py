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
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/packaging_order_views.xml',
        'views/packaging_cancel_views.xml',
        'views/packaging_menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto-install': False,
}