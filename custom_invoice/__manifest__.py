{
    'name': 'Custom Invoice Print',
    'version': '1.0',
    'description': '',
    'summary': '',
    'author': 'Nasreldin Omar',
    'website': 'nasrom9@gmail.com',
    'license': 'LGPL-3',
    'category': '',
    'depends': [
        'account_accountant', 'sale', 'account'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_setting_views.xml',
        'views/accounting_views.xml',
        'views/sale_views.xml',
        'views/res_partner_views.xml',
       'report/custom_invoice_report.xml',
       'report/custom_invoice_report_template.xml',
    ],
    'assets': {
        'web.assets_backend': [
            "custom_invoice/static/src/scss/primary_variables.css",
        ],
    },
    'auto_install': False,
    'application': False,
}