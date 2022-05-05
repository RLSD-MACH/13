# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import datetime, timedelta, date
from odoo.exceptions import AccessError, UserError, ValidationError

class AccountMoveInherit(models.Model):
    
    _inherit = 'account.move'

    partner_last_vies_message_valid = fields.Boolean(related='partner_id.last_vies_message_valid', readonly=True)
    partner_last_vies_message_id = fields.Many2one("vies.message", related='partner_id.last_vies_message_id', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        
        res = super(AccountMoveInherit, self).create(vals_list)
        
        if res:
            res._test_vies_message()

        return res

    
    def write(self, data):

        res = super(AccountMoveInherit, self).write(data)
        
        self._test_vies_message()

        return res
    
    
    def _test_vies_message(self):
        
        for record in self:
            
            if record.type in ['out_invoice','out_refund']: #move_type in Odoo V > 13

                if record.partner_id.id:
                    
                    partner = record.partner_id
                    company = record.company_id
                    auto = company.vies_run_auto_sales_invoice
                    days = company.vies_days_between_validations
        
                    if auto:
                        
                        if partner.vat != False:

                            if partner.last_vies_message_id.id:

                                deadline = partner.last_vies_message_date + timedelta(days=days)

                                if date.today() > deadline.date() or partner.last_vies_message_valid == False:

                                    partner.control_vat_on_vies(silent=True)

                            else:

                                partner.control_vat_on_vies(silent=True)