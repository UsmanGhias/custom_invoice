from odoo import models, api, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    retention_money = fields.Boolean(string='Retention Money')
    retention_percentage_id = fields.Many2one('retention.percentage', string='Retention Percentage')
    show_retention_options = fields.Boolean(compute='check_retenion_options', store=True)
    english_name = fields.Char('Name in English')

    @api.depends('company_id')
    def check_retenion_options(self):
        for rec in self:
            rec.show_retention_options = self.env.company.retention_money

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    iban = fields.Char('IBAN')