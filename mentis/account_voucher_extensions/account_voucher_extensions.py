# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Mentis d.o.o.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv

class account_bank_statement_line(osv.osv):
    _inherit = "account.bank.statement.line"
    _columns = {
        'auto_voucher_allocation': fields.boolean('Auto Alloc.')
    }
    
account_bank_statement_line()

class account_voucher(osv.osv):
    _inherit = "account.voucher"
    
    def recompute_voucher_lines(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=None):
        res = super(account_voucher, self).recompute_voucher_lines(cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, context=context)
        leave_values = context.get('auto_alloc', True) #Ce kljuc ne obstaja potem ohranimo vrednosti
        if context and not leave_values:
            for line in res['value']['line_cr_ids']:
                line['reconcile'] = False
                line['amount'] = 0
            for line in res['value']['line_dr_ids']:
                line['reconcile'] = False
                line['amount'] = 0
        return res
    
    def onchange_amount(self, cr, uid, ids, amount, rate, partner_id, journal_id, currency_id, ttype, date, payment_rate_currency_id, company_id, context=None):
        refresh_grid = context.get('auto_alloc', True) #Ce kljuc ne obstaja potem osvezimo
        if refresh_grid:
            res = super(account_voucher, self).onchange_amount(cr, uid, ids, amount, rate, partner_id, journal_id, currency_id, ttype, date, payment_rate_currency_id, company_id, context=context)
            return res
        return False
    
    def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context=None):
        refresh_grid = context.get('auto_alloc', True) #Ce kljuc ne obstaja potem osvezimo
        if context and refresh_grid:
            res = super(account_voucher, self).onchange_journal(cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, context=context)
            return res
        return False
    
account_voucher()
