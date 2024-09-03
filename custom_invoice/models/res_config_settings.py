from odoo import models, api, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    retention_money = fields.Boolean(string='Retention Money', related='company_id.retention_money', readonly=False)
    retention_account_id = fields.Many2one('account.account', string='Retention Account', related='company_id.retention_account_id', readonly=False)

class ResCompany(models.Model):
    _inherit = 'res.company'

    retention_account_id = fields.Many2one('account.account', string='Retention Account')
    retention_money = fields.Boolean(string='Retention Money')