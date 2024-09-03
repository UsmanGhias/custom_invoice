from odoo import models, api, fields, _
from num2words import num2words
from contextlib import ExitStack, contextmanager
from odoo.tools import (
    format_amount,
)
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    amount_in_words = fields.Char(compute='amount_to_words')
    retention_percentage = fields.Float('Retention Percenatage', readonly=True)
    project_description = fields.Char(string='Project Description')
    print_header = fields.Boolean(string='Print Header and Footer', default=True)
    values_fixed = fields.Boolean()

    @api.depends('amount_total')
    def amount_to_words(self):
        for rec in self:
            retention_amount = 0
            retention_amount = sum(rec.line_ids.filtered(lambda line: line.is_retention_line).mapped('balance'))
            rec.amount_in_words = num2words(rec.amount_total - retention_amount, to = 'currency').replace('euro', 'Rials')
            rec.amount_in_words = rec.amount_in_words.replace('cents', 'Halala')

    def get_current_date(self):
        for rec in self:
            return fields.Date.today()

    

    def fix_values(self):
        total_credit = sum(self.line_ids.mapped('credit'))
        total_credit -= sum(self.line_ids.filtered(lambda line: line.name == 'Down payment').mapped('debit'))
        retention_debit = total_credit * self.retention_percentage / 100
        receivable_debit = total_credit - (total_credit * self.retention_percentage / 100)
        self.line_ids.filtered(lambda line: line.is_retention_line).update({'debit': retention_debit})
        self.line_ids.filtered(lambda line: line.account_id.account_type == 'asset_receivable' and not line.is_retention_line).update({'debit': receivable_debit })
        

    @contextmanager
    def _check_balanced(self, container):
        ''' Assert the move is fully balanced debit = credit.
        An error is raised if it's not the case.
        '''
        with self._disable_recursion(container, 'check_move_validity', default=True, target=False) as disabled:
            yield
            if disabled:
                return

        unbalanced_moves = self._get_unbalanced_moves(container)
        if unbalanced_moves:
            if self.retention_percentage > 0 and not self.values_fixed:
                self.values_fixed = True
                self.fix_values()
            else:
                error_msg = _("An error has occurred.")
                for move_id, sum_debit, sum_credit in unbalanced_moves:
                    move = self.browse(move_id)
                    error_msg += _(
                        "\n\n"
                        "The move (%s) is not balanced.\n"
                        "The total of debits equals %s and the total of credits equals %s.\n"
                        "You might want to specify a default account on journal \"%s\" to automatically balance each move.",
                        move.display_name,
                        format_amount(self.env, sum_debit, move.company_id.currency_id),
                        format_amount(self.env, sum_credit, move.company_id.currency_id),
                        move.journal_id.name)
                if not self.retention_percentage > 0:
                    raise UserError(error_msg)

        
    @api.onchange('invoice_line_ids')
    def on_change_invoice_line_ids(self):
        if self.retention_percentage > 0:
            self.values_fixed = False


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_retention_line = fields.Boolean()