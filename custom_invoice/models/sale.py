from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    retention_percentage_id = fields.Many2one("retention.percentage", string='Retention Percentage')
    edit_retention_percentage = fields.Boolean(compute='check_edit_retention_percentage', store=True)
    # invoices_number = fields.Integer('Number of Invoices')
    project_description = fields.Char(string='Project Description')

    @api.depends('partner_id')
    def check_edit_retention_percentage(self):
        for rec in self:
            if not rec.partner_id:
                rec.edit_retention_percentage = True
                rec.retention_percentage_id = False
            else:
                if rec.partner_id.retention_money:
                    rec.edit_retention_percentage = False
                    rec.retention_percentage_id = rec.partner_id.retention_percentage_id
                else:
                    rec.edit_retention_percentage = True
                    rec.retention_percentage_id = False

    def _create_invoices(self, grouped=False, final=False, date=None):
        moves = super()._create_invoices(grouped, fields, date)
        moves.update({'project_description': self.project_description})
        if self.retention_percentage_id:
            moves.update({'retention_percentage': self.retention_percentage_id.percentage})
            for move in moves:
                debit = 0

                receivable_line = move.line_ids.filtered(lambda line: line.account_id.account_type == 'asset_receivable' and line.name != 'Retention')
                debit = receivable_line.debit * move.retention_percentage / 100
                    
                date_maturity = receivable_line.date_maturity
                
                
                retention_line = self.env['account.move.line'].create([{
                            'name': 'Retention',
                            'account_id': self.env.company.retention_account_id.id,
                            'tax_ids': False,
                            'display_type': 'payment_term',
                            'move_id': move.id,
                            'debit': 0,
                            'credit': 0,
                            'date_maturity': date_maturity,
                            'is_retention_line': True,
                        }])
                receivable_line_debit = receivable_line.debit - debit

                

                query = """
                UPDATE account_move_line set debit = %(debit)s, balance=%(debit)s where id = %(id)s;
                """

                self.env.cr.execute(query, {'debit': receivable_line_debit, 'id': receivable_line.id})

                
                self.env.cr.execute(query, {'debit': debit, 'id': retention_line.id})

                retention_amount_currency = 0
                
                retention_amount_currency = retention_line.currency_id.round(debit * retention_line.currency_rate)
                if retention_line.currency_id == retention_line.company_id.currency_id:
                    retention_amount_currency = debit
                
                receivable_line_amount_currency = 0
                receivable_line_amount_currency = receivable_line.currency_id.round(receivable_line_debit * receivable_line.currency_rate)
                if receivable_line.currency_id == receivable_line.company_id.currency_id:
                    receivable_line_amount_currency = receivable_line_debit
                
                query = """
                UPDATE account_move_line set amount_currency = %(amount_currency)s where id = %(id)s;
                """
                self.env.cr.execute(query, {'amount_currency': receivable_line_amount_currency, 'id': receivable_line.id})
                self.env.cr.execute(query, {'amount_currency': retention_amount_currency, 'id': retention_line.id})
                lines = retention_line | receivable_line
                retention_line._compute_amount_currency()
        return moves
    


