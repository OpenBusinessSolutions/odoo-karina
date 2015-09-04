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

#####
# Wizard trigers a report, that shows a receivable & payable card of customer
#####


from osv import fields, osv
from tools.translate import _
import time

class receivable_payable_wizard(osv.osv_memory):
    _name = "receivable.payable.wizard"
    _description = "Receivable Payable Wizard"
    
    def _get_fiscalyear(self, cr, uid, context=None):
        """Return default Fiscalyear value"""
        return self.pool.get('account.fiscalyear').find(cr, uid, context=context)
    
    _columns = {
        'account': fields.selection([('payable','Payable'),
                                     ('receivable','Receivable')], 'Account', required=True),
        'account_code': fields.char('Account Code', size=16),
        'reconcile': fields.selection([('open','Open'),
                                       ('partial','Partial'),
                                       ('full','Reconciled')], 'Reconcile'),
        'filter': fields.selection([('filter_date', 'Date'),
                                    ('filter_period', 'Periods')], "Filter date by"),
        'fiscalyear_id': fields.many2one('account.fiscalyear', \
                                    'Fiscal year',  \
                                    help='Keep empty for all open fiscal years'),
        'period_from': fields.many2one('account.period', 'Start period'),
        'period_to': fields.many2one('account.period', 'End period'),
        'date_from': fields.date("Start Date"),
        'date_to': fields.date("End Date"),
        'date_type_filter': fields.selection([('effective_date', 'Effective date'),
                                              ('due_date', 'Due date')], 'Date type', required=True),
        'sort': fields.selection([('name','Name'),
                                  ('date','Date')], 'Sort'),
        'print_overdue': fields.boolean('Print Overdues'),
    }
    _defaults = {
        'account': 'receivable',
        'fiscalyear_id': _get_fiscalyear,
        'filter': 'filter_date',
        'date_type_filter': 'effective_date',
        'sort': 'date',
    }
    
    def onchange_fiscalyear(self, cr, uid, ids, fiscalyear_id=False, context=None):
        res = {}
        if fiscalyear_id:
            start_period = end_period = False
            cr.execute('''
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               ORDER BY p.date_start ASC
                               LIMIT 1) AS period_start
                UNION ALL
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               AND p.date_start < NOW()
                               ORDER BY p.date_stop DESC
                               LIMIT 1) AS period_stop''', (fiscalyear_id, fiscalyear_id))
            periods =  [i[0] for i in cr.fetchall()]
            if periods and len(periods) > 1:
                start_period = periods[0]
                end_period = periods[1]
            res['value'] = {'period_from': start_period, 'period_to': end_period}
        else:
            res['value'] = {'period_from': False, 'period_to': False}
        return res
    
    def onchange_filter(self, cr, uid, ids, filter='filter_no', fiscalyear_id=False, context=None):
        res = {'value': {}}
        if not filter:
            res['value'] = {'period_from': False, 'period_to': False, 'date_from': False ,'date_to': False}
        if filter == 'filter_date':
            res['value'] = {'reconcile': False, 'period_from': False, 'period_to': False, 'date_from': time.strftime('%Y-01-01'), 'date_to': time.strftime('%Y-%m-%d')}
        if filter == 'filter_period' and fiscalyear_id:
            start_period = end_period = False
            cr.execute('''
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               AND p.special = false
                               ORDER BY p.date_start ASC, p.special ASC
                               LIMIT 1) AS period_start
                UNION ALL
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               LEFT JOIN account_fiscalyear f ON (p.fiscalyear_id = f.id)
                               WHERE f.id = %s
                               AND p.date_start < NOW()
                               AND p.special = false
                               ORDER BY p.date_stop DESC
                               LIMIT 1) AS period_stop''', (fiscalyear_id, fiscalyear_id))
            periods =  [i[0] for i in cr.fetchall()]
            if periods and len(periods) > 1:
                start_period = periods[0]
                end_period = periods[1]
            res['value'] = {'reconcile': False, 'period_from': start_period, 'period_to': end_period, 'date_from': False, 'date_to': False}
        return res
    
    def onchange_print_overdue(self, cr, uid, ids, print_overdue, context=None):
        res = {}
        if print_overdue:
            res['value'] = {'date_type_filter': 'due_date'}
        else:
            res['value'] = {'date_type_filter': 'effective_date'}
        return res
        
    def execute(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        active_ids = context.get('active_ids',[])
        data = self.read(cr, uid, ids, [], context=context)[0]
        db_account =  data.get('account', False) and data['account'] or False
        if db_account == 'payable':
            db_debcred = 'credit'
        else:
            db_debcred = 'debit'
            
        db_account_code = data.get('account_code', False) and data['account_code'] or ''
        
        reconcile = data.get('reconcile', False) and data['reconcile'] or False
        if reconcile == 'full':
            db_reconcile = 'AND reconcile_id IS NOT null'
        elif reconcile == 'partial':
            db_reconcile = 'AND reconcile_partial_id IS NOT null'
        elif reconcile == 'open':
            db_reconcile = 'AND reconcile_id IS null'
        else:
            db_reconcile = 'AND AML.id IS NOT null'
            
        period_from = data.get('period_from', False) and data['period_from'][0] or False
        period_from_desc = data.get('period_from', False) and data['period_from'][1] or False
        period_to = data.get('period_to', False) and data['period_to'][0] or False
        period_to_desc = data.get('period_to', False) and data['period_to'][1] or False
        period_ids = self.pool.get('account.period').build_ctx_periods(cr, uid, period_from, period_to)
        
        db_sort = data.get('sort', False) and data['sort'] or False
        if not db_sort:
            db_sort = 'AML.id'
        
        #Date Filter
        db_date_type = data.get('date_type_filter', False) and data['date_type_filter'] or False
        db_filter = data.get('filter', False) and data['filter'] or False
        if not db_filter:
            db_date_period = ''
        elif db_filter == 'filter_date':
            db_date_from = data.get('date_from', False) and data['date_from'] or False
            db_date_to = data.get('date_to', False) and data['date_to'] or False
            #db_date_period = 'AND AML.date >= \'{0}\' AND AML.date <= \'{1}\''.format(db_date_from, db_date_to)
            if db_date_type == 'effective_date':
                db_date_period = 'AND AML.date <= \'{0}\''.format(db_date_to)
            else:
                db_date_period = 'AND AML.date_maturity <= \'{0}\''.format(db_date_to)
        elif db_filter == 'filter_period':
            period_str = ','.join(str(x) for x in period_ids)
            db_date_period = 'AND AML.period_id in ({0})'.format(period_str)
        
        
        partner_obj = self.pool.get('res.partner')
        acc_move_line_obj = self.pool.get('account.move.line')
        list_data = []
        i = 1
        
        for partner in partner_obj.browse(cr, uid, active_ids):
            dict_moves = {}
            
            query_string = """SELECT
                                AML.id,
                                AML.date,
                                CASE
                                    WHEN AM.name ILIKE \'OTV%\'
                                        THEN AML.name
                                        ELSE AM.name
                                end as name
                                FROM account_move_line AML
                                    LEFT JOIN account_move AM on AML.move_id = AM.id
                                    LEFT JOIN account_account AA on AML.account_id = AA.id
                                WHERE
                                    AML.partner_id = {0}
                                    AND AA.type in (\'{1}\')
                                    AND AA.code like \'{2}%\'
                                    AND {3} > 0
                                    {4}
                                    {5}
                                ORDER BY {6}""".format(partner.id, db_account, db_account_code, db_debcred, db_reconcile, db_date_period, db_sort)
            
            cr.execute(query_string)
            res_ids = [(r[0]) for r in cr.fetchall()]

#            acc_move_line_ids = acc_move_line_obj.search(cr, uid, [
#                                                       ('partner_id','=',partner.id),         X
#                                                       ('period_id','in',period_ids),
#                                                       ('account_id.type','in',[account]),    X
#                                                       (db_debcred, '>',0),                   X 
#                                                       (db_reconcile, '!=', None)             X
#                                                       ], order=db_sort)                      X  
            
            sum_debit = 0
            sum_credit = 0
            sum_start_debit = 0
            sum_start_credit = 0
            for move_line in acc_move_line_obj.browse(cr, uid, res_ids): #za vsak strankin racun preverimo placila
                
                if db_filter == 'filter_date' and move_line.date < db_date_from: #izracunamo zacetni saldo
                    if move_line.debit > 0:
                        sum_start_debit = sum_start_debit + move_line.debit
                    else:
                        sum_start_credit = sum_start_credit + move_line.credit
                        
                dict_temp = {}
                if move_line.move_id.name[:3].lower() == "otv":
                    dict_temp['document'] = move_line.name
                    dict_temp['desc'] = move_line.move_id.name
                else:
                    dict_temp['document'] = move_line.move_id.name
                    if db_debcred == 'debit':
                        dict_temp['desc'] = move_line.name
                    else:
                        dict_temp['desc'] = move_line.ref 
                dict_temp['move'] = ''
                dict_temp['date'] = move_line.date
                dict_temp['date_due'] = move_line.date_maturity
                dict_temp['saldo'] = ''
                
                if move_line.debit == 0:
                    dict_temp['debit'] = ''
                else:
                    dict_temp['debit'] = format(move_line.debit, '.2f').replace('.',',')
                
                if move_line.credit == 0:
                    dict_temp['credit'] = ''
                else:
                    dict_temp['credit'] = format(move_line.credit, '.2f').replace('.',',')
                
                if move_line.reconcile_id.id:
                    dict_temp['reconcile'] = move_line.reconcile_id.id
                else:
                    dict_temp['reconcile'] = move_line.reconcile_partial_id.id
                dict_temp['sort'] = i
                
                if (db_filter != 'filter_date') or (db_filter == 'filter_date' and move_line.date >= db_date_from): #dodamo na izpis, ker je visjega datuma
                    sum_debit = sum_debit + move_line.debit
                    sum_credit = sum_credit + move_line.credit
                    dict_moves[i] = dict_temp
                    i = i+1
                
                if not move_line.reconcile_id.id and not move_line.reconcile_partial_id.id:
                    continue
                
                #-----------------------------Poiscemo placila, ki ustrezajo izbranim dokumetom-------------------
                query_lst = [('reconcile_id','=',move_line.reconcile_id.id),
                             ('reconcile_partial_id','=',move_line.reconcile_partial_id.id),
                             ('id','!=',move_line.id)]
                if db_filter == 'filter_date':
                    #query_lst.append(('date','>=',db_date_from))
                    query_lst.append(('date','<=',db_date_to))
                elif db_filter == 'filter_period':
                    query_lst.append(('period_id','in',period_ids))
                if db_account == 'payable':
                    query_lst.append(('debit','>',0))
                else:
                    query_lst.append(('credit','>',0)) #Terjatve
                payment_ids = self.pool.get('account.move.line').search(cr, uid, query_lst, order='date')
                
                j = len(payment_ids)
                sub_sum_credit = 0
                for account_line in self.pool.get('account.move.line').browse(cr, uid, payment_ids):
                    dict_temp = {}
                    dict_temp['document'] = '-->'
                    dict_temp['move'] = account_line.move_id.name
                    dict_temp['desc'] = account_line.name
                    dict_temp['date'] = account_line.date
                    dict_temp['date_due'] = account_line.date
                    dict_temp['debit'] = ''
                    dict_temp['credit'] = ''
                    
                    if db_debcred == 'debit':
                        if account_line.credit > 0:
                            #Ce je bilo eno placilo za vsec racunov je credit vecji
                            if account_line.credit > move_line.debit:
                                dict_temp['debit'] = '('+str(format(account_line.credit, '.2f').replace('.',','))+')' #kolik je bil skupni znesek za zapiranje
                                dict_temp['credit'] = format(move_line.debit, '.2f').replace('.',',') #znesek je kar enak debitu, ker je bil v celoti zaprt, ce bi bil delno ne bi bil vecji
                                if (db_filter != 'filter_date') or (db_filter == 'filter_date' and account_line.date >= db_date_from):
                                    sum_credit = sum_credit + move_line.debit
                                else:
                                    sum_start_credit = sum_start_credit + move_line.debit
                                sub_sum_credit = sub_sum_credit + move_line.debit
                            else:
                                if account_line.credit == 0:
                                    dict_temp['credit'] = ''
                                else:
                                    dict_temp['credit'] = format(account_line.credit, '.2f').replace('.',',')
                                if (db_filter != 'filter_date') or (db_filter == 'filter_date' and account_line.date >= db_date_from):
                                    sum_credit = sum_credit + account_line.credit
                                else:
                                    sum_start_credit = sum_start_credit + account_line.credit
                                sub_sum_credit = sub_sum_credit + account_line.credit
                        else:
                            if account_line.debit == 0:
                                dict_temp['credit'] = ''
                            else:
                                dict_temp['credit'] = format(account_line.debit, '.2f').replace('.',',')
                            if (db_filter != 'filter_date') or (db_filter == 'filter_date' and account_line.date >= db_date_from):
                                sum_credit = sum_credit + account_line.debit
                            else:
                                sum_start_credit = sum_start_credit + account_line.debit
                            sub_sum_credit = sub_sum_credit + account_line.debit
                    else:
                        if account_line.debit > 0:
                            if account_line.debit > move_line.credit:
                                dict_temp['credit'] = '('+str(format(account_line.debit, '.2f').replace('.',','))+')' #kolik je bil skupni znesek za zapiranje
                                dict_temp['debit'] = format(move_line.credit, '.2f').replace('.',',') #znesek je kar enak debitu, ker je bil v celoti zaprt, ce bi bil delno ne bi bil vecji
                                if (db_filter != 'filter_date') or (db_filter == 'filter_date' and account_line.date >= db_date_from):
                                    sum_debit = sum_debit + move_line.credit
                                else:
                                    sum_start_debit = sum_start_debit + move_line.credit
                                sub_sum_credit = sub_sum_credit + move_line.credit
                            else:
                                if account_line.debit == 0:
                                    dict_temp['debit'] = ''
                                else:
                                    dict_temp['debit'] = format(account_line.debit, '.2f').replace('.',',')
                                if (db_filter != 'filter_date') or (db_filter == 'filter_date' and account_line.date >= db_date_from):
                                    sum_debit = sum_debit + account_line.debit
                                else:
                                    sum_start_debit = sum_start_debit + account_line.debit
                                sub_sum_credit = sub_sum_credit + account_line.debit
                        else:
                            if account_line.credit == 0:
                                dict_temp['debit'] = ''
                            else:
                                dict_temp['debit'] = format(account_line.credit, '.2f').replace('.',',')
                            if (db_filter != 'filter_date') or (db_filter == 'filter_date' and account_line.date >= db_date_from):
                                sum_debit = sum_debit + account_line.credit
                            else:
                                sum_start_debit = sum_start_debit + account_line.credit
                            sub_sum_credit = sub_sum_credit + account_line.credit
                            
                        
                    if j == 1:
                        if db_debcred == 'debit':
                            dict_temp['saldo'] = format(abs(move_line.debit - sub_sum_credit), '.2f').replace('.',',')
                        else:
                            dict_temp['saldo'] = format(abs(move_line.credit - sub_sum_credit), '.2f').replace('.',',')
                    else:
                        dict_temp['saldo'] = ''
                    
                    if account_line.reconcile_id.id:
                        dict_temp['reconcile'] = account_line.reconcile_id.id
                    else:
                        dict_temp['reconcile'] = account_line.reconcile_partial_id.id
                    dict_temp['sort'] = i
                    
                    if (db_filter != 'filter_date') or (db_filter == 'filter_date' and account_line.date >= db_date_from):
                        dict_moves[i] = dict_temp
                        #dict_moves[account_line.move_id.id] = dict_temp
                        i = i+1
                    j = j-1
                    
            #-----------------------------Poiscemo placila, ki NISO vezana na kateri dokument-------------------
            open_query_lst = [('reconcile_id','=',None),
                              ('reconcile_partial_id','=',None),
                              ('partner_id','=',partner.id)]
            if db_filter == 'filter_date':
                #query_lst.append(('date','>=',db_date_from))
                open_query_lst.append(('date','<=',db_date_to))
            elif db_filter == 'filter_period':
                open_query_lst.append(('period_id','in',period_ids))
            if db_account == 'payable':
                open_query_lst.append(('debit','>',0))
                open_query_lst.append(('account_id.type','=','payable'))
            else:
                open_query_lst.append(('credit','>',0)) #Terjatve
                open_query_lst.append(('account_id.type','=','receivable'))
                
            open_payment_ids = self.pool.get('account.move.line').search(cr, uid, open_query_lst, order='date')
            if open_payment_ids: #dodamo prazno vrstico da locimo pralcila ki niso vezana
                dict_temp = {}
                dict_temp['document'] = ''
                dict_temp['move'] = 'Nepovezana plačila'
                dict_temp['sort'] = i
                dict_moves[i] = dict_temp
                i = i+1
            for open_account_line in self.pool.get('account.move.line').browse(cr, uid, open_payment_ids):
                dict_temp = {}
                dict_temp['document'] = '-->'
                dict_temp['move'] = open_account_line.move_id.name
                dict_temp['desc'] = open_account_line.name
                dict_temp['date'] = open_account_line.date
                dict_temp['date_due'] = open_account_line.date
                dict_temp['debit'] = ''
                dict_temp['credit'] = ''
                if db_debcred == 'debit':
                    if open_account_line.credit == 0:
                        dict_temp['credit'] = ''
                    else:
                        dict_temp['credit'] = format(open_account_line.credit, '.2f').replace('.',',')
                    if (db_filter != 'filter_date') or (db_filter == 'filter_date' and open_account_line.date >= db_date_from):
                        sum_credit = sum_credit + open_account_line.credit
                    else:
                        sum_start_credit = sum_start_credit + open_account_line.credit
                else:
                    if open_account_line.debit == 0:
                        dict_temp['debit'] = ''
                    else:
                        dict_temp['debit'] = format(open_account_line.debit, '.2f').replace('.',',')
                    if (db_filter != 'filter_date') or (db_filter == 'filter_date' and open_account_line.date >= db_date_from):
                        sum_debit = sum_debit + open_account_line.debit
                    else:
                        sum_start_debit = sum_start_debit + open_account_line.debit
                
                dict_temp['sort'] = i
                if (db_filter != 'filter_date') or (db_filter == 'filter_date' and account_line.date >= db_date_from):
                    dict_moves[i] = dict_temp
                    i = i+1
                        
                
            sorted_list = sorted(dict_moves.iteritems(), key=lambda (x, y): y['sort'])
                    
            dict_data = {}
            dict_data['moves'] = sorted_list
            db_print_overdue = data.get('print_overdue', False) and data['print_overdue'] or False
            if db_print_overdue:
                dict_data['doc_name'] = 'Opomin'
            else:
                dict_data['doc_name'] = 'Kartica partnerja'
            dict_data['address_name'] = partner.name
            dict_data['address_street'] = partner.street
            dict_data['address_zip'] = partner.zip
            dict_data['address_city'] = partner.city
            dict_data['lang'] = partner.lang
            if db_account == 'receivable':
                dict_data['account'] = 'Terjatve'
            else:
                dict_data['account'] = 'Obveznosti'
            dict_data['account_code'] = db_account_code
            if not db_filter:
                dict_data['period'] = 'Celotno'
            elif db_filter == 'filter_date':
                dict_data['period'] = db_date_from + ' - ' + db_date_to
            elif db_filter == 'filter_period':
                dict_data['period'] = period_from_desc + ' - ' + period_to_desc
                
            if reconcile == 'open':
                dict_data['reconcile'] = 'Odprto'
            elif reconcile == 'partial':
                dict_data['reconcile'] = 'Delno usklajeno'
            elif reconcile == 'full':
                dict_data['reconcile'] = 'Usklajeno'
            else:
                dict_data['reconcile'] = 'Vse'
                
            if db_date_type == 'effective_date':
                dict_data['date_type'] = 'Datum dogodka'
            else:
                dict_data['date_type'] = 'Datum valute'
                
            dict_data['sum_start_debit'] = format(sum_start_debit, '.2f').replace('.',',')
            dict_data['sum_start_credit'] = format(sum_start_credit, '.2f').replace('.',',')
            dict_data['sum_start_saldo'] = format(sum_start_debit - sum_start_credit, '.2f').replace('.',',')
            
            dict_data['sum_debit'] = format(sum_debit, '.2f').replace('.',',')
            dict_data['sum_credit'] = format(sum_credit, '.2f').replace('.',',')
            dict_data['sum_saldo'] = format(sum_debit - sum_credit, '.2f').replace('.',',')
            
            dict_data['sum_sum_debit'] = format(sum_start_debit + sum_debit, '.2f').replace('.',',')
            dict_data['sum_sum_credit'] = format(sum_start_credit + sum_credit, '.2f').replace('.',',')
            dict_data['sum_sum_saldo'] = format(sum_start_debit - sum_start_credit + sum_debit - sum_credit, '.2f').replace('.',',')
            
            
            list_data.append(dict_data)
        
        data = {'form':list_data}
        return {'type': 'ir.actions.report.xml', 'report_name': 'receivable.payable.report', 'name':'Kartica_partnerja', 'datas': data}
    
receivable_payable_wizard()

