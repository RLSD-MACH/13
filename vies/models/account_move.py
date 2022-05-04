# -*- coding: utf-8 -*-

from ast import Raise
from odoo import api, fields, models
from datetime import datetime, timedelta, date
from odoo.exceptions import AccessError, UserError, ValidationError

class AccountMoveInherit(models.Model):
    
    _inherit = 'account.move'

    partner_last_vies_message_valid = fields.Boolean(related='partner_id.last_vies_message_valid', readonly=True)
    partner_last_vies_message_id = fields.Many2one("vies.message", related='partner_id.last_vies_message_id', readonly=True)

    @api.multi
    def create(self, vals):

        res = super(AccountMoveInherit, self).create(vals)
        
        for record in res:

            if record.move_type in ['out_invoice','out_refund']:

                if record.partner_id.id:

                    auto = self.env.company.vies_run_auto_sales_invoice
                    days = self.env.company.vies_days_between_validations
        
                    if auto:
                        
                        if record.partner_id.vat != False:

                            if record.partner_id.last_vies_message_id.id:

                                deadline = record.partner_id.last_vies_message_date + timedelta(days=days)

                                if date.today() > deadline.date() or record.partner_id.last_vies_message_valid == False:

                                    record.partner_id.control_vat_on_vies(silent=True)

                            else:

                                record.partner_id.control_vat_on_vies(silent=True)

        return res

    
    def write(self, data):

        res = super(AccountMoveInherit, self).write(data)
  
        if self.move_type in ['out_invoice','out_refund']:

            if 'partner_id' in data:

                auto = self.env.company.vies_run_auto_sales_invoice
                days = self.env.company.vies_days_between_validations
    
                if auto:
                    
                    partner = self.env['res.partner'].browse(data['partner_id'])
                    
                    if partner:
                        
                        if partner.vat != False:

                            if partner.last_vies_message_id.id:

                                deadline = partner.last_vies_message_date + timedelta(days=days)
                                
                                if date.today() > deadline.date() or partner.last_vies_message_valid == False:

                                    partner.control_vat_on_vies(silent=True)

                            else:
                                
                                partner.control_vat_on_vies(silent=True)

        return res