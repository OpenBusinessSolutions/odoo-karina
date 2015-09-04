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

class overdue_financial_report(osv.osv):
    _name = 'overdue.financial.report'
    _description = 'Overdue payment and financial report'
    _auto = False
    _columns = {
        'date': fields.date('Date'),
        'date_maturity': fields.date('Date Maturity'),
	    'name': fields.char('Name', size=64),
	    'reference': fields.char('Ref', size=64),
		'partner': fields.char('Partner name', size=128),
	    'journal_entry': fields.char('Journal', size=64),
        'debit': fields.float('Debit', digits=(16,2)),
        'credit': fields.float('Credit', digits=(16,2)),
        'saldo': fields.float('Saldo', digits=(16,2)),
        'period': fields.char('Period', size=64),
        'reconcile': fields.integer('Reconcile'),
	    'partner_type': fields.char('Partner type', size=64),
        'account_type': fields.char('Account type', size=64),
        'account_code': fields.char('Account code', size=64),
	}
    
    def init(self, cr):
        drop_view_if_exists(cr, 'overdue_financial_report')
        cr.execute("""
            create or replace view overdue_financial_report as (
                SELECT
                    AML.id as id,
                    AML.date as date,
                    AML.date_maturity as date_maturity,
                    AML.name as name,
                    AML.ref as reference,
                    P.name as partner,
                    AM.name as journal_entry,
                    AML.debit as debit,
                    AML.credit as credit,
                    AML.debit-AML.credit as saldo,
                    AP.name as period,
                    AML.reconcile_id as reconcile,
                    CASE
                        WHEN P.business_partner_type = '1' THEN 'D.D.'
                        WHEN P.business_partner_type = '2' THEN 'D.O.O.'
                        WHEN P.business_partner_type = '3' THEN 'S.P.'
                        WHEN P.business_partner_type = '4' THEN 'Bolnice'
                        WHEN P.business_partner_type = '5' THEN 'Šole'
                        WHEN P.business_partner_type = '6' THEN 'Sindikati'
                        WHEN P.business_partner_type = '7' THEN 'Društva'
                        WHEN P.business_partner_type = '8' THEN 'Zavarovalnice'
                        WHEN P.business_partner_type = '9' THEN 'Vrtec'
                        WHEN P.business_partner_type = '10' THEN 'Občine'
                        ELSE 'Neopredeljeni'
                    END as partner_type,
                    AA.type as account_type,
                    AA.code as account_code
                FROM account_move_line AML
                    LEFT JOIN account_account AA ON AML.account_id = AA.id
                    LEFT JOIN res_partner P ON AML.partner_id = P.id
                    LEFT JOIN account_move AM ON AML.move_id = AM.id
                    LEFT JOIN account_period AP ON AML.period_id = AP.id
                WHERE
                    AA.reconcile = true
            )""")
overdue_financial_report()
    

