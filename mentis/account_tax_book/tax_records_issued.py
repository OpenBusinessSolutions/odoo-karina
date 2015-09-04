# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Mentis d.o.o. (<http://www.mentis.si>)
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

from openerp.osv import fields, osv
from tools.sql import drop_view_if_exists

class tax_records_issued(osv.osv):
    _name = 'tax.records.issued'
    _description = 'Tax records of issued documents'
    _auto = False
    _columns = {
        'period_id': fields.many2one('account.period', string='Period'),
        #'period_name': fields.related('period_id', 'name', relation='account.period', type='char', string='Period'),
        'date': fields.date('Date'),
	    'document_name': fields.char('Document name', size=64),
        'partner_name': fields.char('Partner name', size=128),
        'vat': fields.char('Vat', size=16),
        'col_7': fields.float('C_7', digits=(16,2)),
        'col_8': fields.float('C_8', digits=(16,2)),
        'col_9': fields.float('C_9', digits=(16,2)),
        'col_10a': fields.float('C_10a', digits=(16,2)),
        'col_10a1': fields.float('C_10a1', digits=(16,2)),
        'col_10b': fields.float('C_10b', digits=(16,2)),
        'col_11': fields.float('C_11', digits=(16,2)),
        'col_12': fields.float('C_12', digits=(16,2)),
        'col_13': fields.float('C_13', digits=(16,2)),
        'col_14': fields.float('C_14', digits=(16,2)),
        'col_15': fields.float('C_15', digits=(16,2)),
        'col_16': fields.float('C_16', digits=(16,2)),
        'col_17': fields.float('C_17', digits=(16,2)),
        'col_18': fields.float('C_18', digits=(16,2)),
        'col_19': fields.float('C_19', digits=(16,2)),
        'col_20': fields.float('C_20', digits=(16,2)),
        'col_21': fields.float('C_21', digits=(16,2)),
        'col_22': fields.float('C_22', digits=(16,2)),
        'col_23': fields.float('C_23', digits=(16,2)),
	}
    
    def init(self, cr):
        drop_view_if_exists(cr, 'tax_records_issued')
        cr.execute("""
            create or replace view tax_records_issued as (
                SELECT
                    min(AML.id) as id,
                    AM.tax_period_id as period_id,
                    AM.date as date,
                    AM.name as document_name,
                    P.name as partner_name,
                    P.vat as vat,
                    sum(
                    case
                    when ATB.position = '7' 
                            then credit-debit
                            else 0
                    end) as col_7,
                    sum(
                    case
                    when ATB.position = '8' 
                            then credit-debit
                            else 0
                    end) as col_8,
                    sum(
                    case
                    when ATB.position = '9' 
                            then credit-debit
                            else 0
                    end) as col_9,
                    sum(
                    case
                    when ATB.position = '10.a' 
                            then credit-debit
                            else 0
                    end) as col_10a,
                    sum(
                    case
                    when ATB.position = '10.a1' 
                            then credit-debit
                            else 0
                    end) as col_10a1,
                    sum(
                    case
                    when ATB.position = '10b' 
                            then credit-debit
                            else 0
                    end) as col_10b,
                    sum(
                    case
                    when ATB.position = '11' 
                            then credit-debit
                            else 0
                    end) as col_11,
                    sum(
                    case
                    when ATB.position = '12'
                            then credit-debit
                            else 0
                    end) as col_12,
                    sum(
                    case
                    when ATB.position = '13' 
                            then credit-debit
                            else 0
                    end) as col_13,
                    sum(
                    case
                    when ATB.position = '14' 
                            then credit-debit
                            else 0
                    end) as col_14,
                    sum(
                    case
                    when ATB.position = '15'
                            then credit-debit
                            else 0
                    end) as col_15,
                    sum(
                    case
                    when ATB.position = '16'
                            then credit-debit
                            else 0
                    end) as col_16,
                    sum(
                    case
                    when ATB.position = '17'
                            then credit-debit
                            else 0
                    end) as col_17,
                    sum(
                    case
                    when ATB.position = '18'
                            then credit-debit
                            else 0
                    end) as col_18,
                    sum(
                    case
                    when ATB.position = '19'
                            then credit-debit
                            else 0
                    end) as col_19,
                    sum(
                    case
                    when ATB.position = '20'
                            then credit-debit
                            else 0
                    end) as col_20,
                    sum(
                    case
                    when ATB.position = '21'
                            then credit-debit
                            else 0
                    end) as col_21,
                    sum(
                    case
                    when ATB.position = '22'
                            then credit-debit
                            else 0
                    end) as col_22,
                    sum(
                    case
                    when ATB.position = '23'
                            then credit-debit
                            else 0
                    end) as col_23
                FROM 
                        account_move_line AML,
                        account_move AM,
                        account_tax_book_fields_issued_tax_code_rel REL,
                        account_tax_book_fields ATB,
                    res_partner P
                WHERE 
                        AML.tax_code_id = REL.tax_code_id and 
                        REL.tax_book_fields_id = ATB.id and 
                        AML.tax_code_id != 0 and
                    AML.partner_id = P.id and
                    AML.move_id = AM.id
                
                GROUP BY AM.name, AM.date, AM.tax_period_id, P.name, P.vat
                ORDER BY AM.name
            )""")
tax_records_issued()
    

