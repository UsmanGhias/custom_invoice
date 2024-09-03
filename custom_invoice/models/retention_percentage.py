from odoo import models, api, fields
from odoo.exceptions import UserError


class RetentionPercentage(models.Model):
    _name = 'retention.percentage'

    name = fields.Char(required=True, string='Retention Percentage')
    code = fields.Char(required=True, string='Code')
    percentage = fields.Float(string='Percentage')

    