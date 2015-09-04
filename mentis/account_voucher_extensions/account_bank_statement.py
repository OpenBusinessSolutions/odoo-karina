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

class account_bank_statement(osv.osv):
    _inherit = "account.bank.statement"
    
    def _calc_sum(self, cr, uid, ids, field_name, arg=None, context=None):

        res = {}  
        for statement in self.browse(cr, uid, ids):
            res_sub = {}
            sum_debit = sum_credit = 0
            line_ids = self.pool.get('account.bank.statement.line').search(cr, uid, [('statement_id','in',ids)])
            for line in self.pool.get('account.bank.statement.line').browse(cr, uid, line_ids):
                if line.amount < 0:
                    sum_debit = sum_debit + line.amount
                else:
                    sum_credit = sum_credit + line.amount
                    
            res_sub['sum_lines_credit'] = sum_credit
            res_sub['sum_lines_debit'] = sum_debit
            res[statement.id] = res_sub
        return res
        
    _columns = {
        'sum_lines_credit': fields.function(_calc_sum, type='float', string='Sum Credit', multi='sum'),
		'sum_lines_debit': fields.function(_calc_sum, type='float', string='Sum Debit', multi='sum'),
    }
    
#    def button_dummy(self, cr, uid, ids, context=None):
#        
#        sum_customer = sum_supplier = sum_general = 0
#        line_ids = self.pool.get('account.bank.statement.line').search(cr, uid, [('statement_id','=',ids)])
#        for line in self.pool.get('account.bank.statement.line').browse(cr, uid, line_ids):
#            if line.type == 'customer':
#                sum_customer = sum_customer + line.amount
#            elif line.type == 'supplier':
#                sum_supplier = sum_supplier + line.amount
#            elif line.type == 'general':
#                sum_general = sum_general + line.amount
#        return self.write(cr, uid, ids, {'sum_customer_lines':sum_customer,
#                                         'sum_supplier_lines':sum_supplier,
#                                         'sum_general_lines':sum_general,
#                                         }, context=context)
    
account_bank_statement()
