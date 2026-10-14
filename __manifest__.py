{
    'name': 'Malabar FMCG Distributors',
    'version': '20.0.1.0.0',
    'summary': 'FMCG Wholesale + Counter Sales practice project (Individual plan, Odoo 20)',
    'description': """
Malabar FMCG Distributors - Individual practice project for Odoo 20.
Covers: Purchase, Inventory (3 warehouses, lots/expiry, FEFO),
Wholesale Sales, POS counter sales, Accounting & Reporting.
Initial phases use standard apps; this module is a skeleton for
future customizations (expiry alerts, credit-limit, dashboard,
POS batch validation, purchase approval).
    """,
    'category': 'Inventory/Inventory',
    'author': 'Training',
    'website': '',
    'depends': ['base', 'contacts', 'purchase', 'stock', 'sale', 'point_of_sale', 'account'],
    'data': [
        'security/security.xml',
        'security/ir.access.csv',
        'data/sequence.xml',
        'data/ir_cron.xml',
        'data/mail_template.xml',
        # Phase 2 - master data views
        'views/product_views.xml',
        'views/res_partner_views.xml',
        # Phase 3 - purchase
        'views/purchase_views.xml',
        # Phase 4 - inventory / transfers / expiry
        'views/stock_views.xml',
        'views/expiry_wizard_views.xml',
        # Phase 5 - wholesale
        'views/sale_views.xml',
        # Phase 6 - POS
        'views/pos_views.xml',
        # Phase 7 - accounting
        'views/account_views.xml',
        'views/menus.xml',
        'reports/stock_expiry_report.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
