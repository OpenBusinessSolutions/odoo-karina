# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Mentis d.o.o.
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

import time

from openerp.report import report_sxw
from account.report.common_report_header import common_report_header

class account_balance(report_sxw.rml_parse, common_report_header):
    _name = 'report.account.account.balance.mentis'

    def __init__(self, cr, uid, name, context=None):
        super(account_balance, self).__init__(cr, uid, name, context=context)
        self.sum_debit = 0.00
        self.sum_credit = 0.00
        self.sum_BS = 0.00
        self.sum_BU = 0.00
        self.date_lst = []
        self.date_lst_string = ''
        self.result_acc = []
        self.localcontext.update({
            'time': time,
            'lines': self.lines,
            'sum_debit': self._sum_debit,
            'sum_credit': self._sum_credit,
            'get_fiscalyear':self._get_fiscalyear,
            'get_filter': self._get_filter,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period ,
            'get_account': self._get_account,
            'get_journal': self._get_journal,
            'get_start_date':self._get_start_date,
            'get_end_date':self._get_end_date,
            'get_target_move': self._get_target_move,
            'lines_by_classes': self.lines_by_classes,
            'get_BS_value': self.get_BS_value,
            'get_BU_value': self.get_BU_value,
        })
        self.context = context

    def _get_filter(self, data):
        res = ''
        if data.get('form', False) and data['form'].get('filter', False):
            if data['form']['filter'] == 'filter_date':
                res = self._translate('Date')
            elif data['form']['filter'] == 'filter_period':
                res = self._translate('Periods')
        else:
            res = self._translate('No Filters')
        return res
    
    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        if (data['model'] == 'ir.ui.menu'):
            new_ids = 'chart_account_id' in data['form'] and [data['form']['chart_account_id']] or []
            objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
        return super(account_balance, self).set_context(objects, data, new_ids, report_type=report_type)

    def _get_account(self, data):
        if data['model']=='account.account':
            return self.pool.get('account.account').browse(self.cr, self.uid, data['form']['id']).company_id.name
        return super(account_balance ,self)._get_account(data)

    def lines(self, form, ids=None, done=None):
        def _process_child(accounts, disp_acc, parent):
                account_rec = [acct for acct in accounts if acct['id']==parent][0]
                currency_obj = self.pool.get('res.currency')
                acc_id = self.pool.get('account.account').browse(self.cr, self.uid, account_rec['id'])
                currency = acc_id.currency_id and acc_id.currency_id or acc_id.company_id.currency_id
                
                if (account_rec['debit_open'] - account_rec['credit_open']) >= 0:
                    debit_open = account_rec['debit_open'] - account_rec['credit_open']
                    credit_open = 0.00
                else:
                    credit_open = account_rec['credit_open'] - account_rec['debit_open']
                    debit_open = 0.00
                    
                debit_close = account_rec['debit'] + account_rec['debit_open']
                credit_close = account_rec['credit'] + account_rec['credit_open']
                
                if (debit_close - credit_close) >= 0:
                    debit_close = debit_close - credit_close
                    credit_close = 0.00
                else:
                    credit_close = credit_close - debit_close
                    debit_close = 0.00
                
                
                res = {
                    'id': account_rec['id'],
                    'type': account_rec['type'],
                    'code': account_rec['code'],
                    'name': account_rec['name'],
                    'level': account_rec['level'],
                    'debit': account_rec['debit'],
                    'credit': account_rec['credit'],
                    'balance': account_rec['balance'],
                    'debit_open': debit_open,
                    'credit_open': credit_open,
                    'debit_close': debit_close,
                    'credit_close': credit_close,
                    'parent_id': account_rec['parent_id'],
                    'bal_type': '',
                }
                
                
                if disp_acc == 'movement':
                    if not currency_obj.is_zero(self.cr, self.uid, currency, res['credit']) \
                    or not currency_obj.is_zero(self.cr, self.uid, currency, res['debit']) \
                    or not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']) \
                    or not currency_obj.is_zero(self.cr, self.uid, currency, res['debit_open']) \
                    or not currency_obj.is_zero(self.cr, self.uid, currency, res['credit_open']):
                        self.result_acc.append(res)
                        if account_rec['code'] in ('0','1','2','3','6','8','9'):
                            self.sum_BS += account_rec['debit_open'] - account_rec['credit_open'] + account_rec['debit'] - account_rec['credit']
                        elif account_rec['code'] in ('4','7'):
                            self.sum_BU += account_rec['debit_open'] - account_rec['credit_open'] + account_rec['debit'] - account_rec['credit']
                
                elif disp_acc == 'not_zero':
                    if not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
                        self.result_acc.append(res)
                        if account_rec['code'] in ('0','1','2','3','6','8','9'):
                            self.sum_BS += account_rec['debit_open'] - account_rec['credit_open'] + account_rec['debit'] - account_rec['credit']
                        elif account_rec['code'] in ('4','7'):
                            self.sum_BU += account_rec['debit_open'] - account_rec['credit_open'] + account_rec['debit'] - account_rec['credit']
                        
                else:
                    self.result_acc.append(res)
                    if account_rec['code'] in ('0','1','2','3','6','8','9'):
                        self.sum_BS += account_rec['debit_open'] - account_rec['credit_open'] + account_rec['debit'] - account_rec['credit']
                    elif account_rec['code'] in ('4','7'):
                        self.sum_BU += account_rec['debit_open'] - account_rec['credit_open'] + account_rec['debit'] - account_rec['credit']
                
                if account_rec['child_id']:
                    sorted_list = sorted(account_rec['child_id'])
                    for child in sorted_list:
                        _process_child(accounts,disp_acc,child)

        obj_account = self.pool.get('account.account')
        if not ids:
            ids = self.ids
        if not ids:
            return []
        if not done:
            done={}
            
        #Izbira konta
        if form.has_key('account_id'):
            if form['account_id']:
                ids = form['account_id']

        ctx = self.context.copy()

        ctx['fiscalyear'] = form['fiscalyear_id']
        if form['filter'] == 'filter_period':
            ctx['period_from'] = form['period_from']
            ctx['period_to'] = form['period_to']
            ctx['if_date_calc_initial_bal'] = False
        elif form['filter'] == 'filter_date':
            ctx['date_from'] = form['date_from']
            ctx['date_to'] =  form['date_to']
            ctx['if_date_calc_initial_bal'] = True
        ctx['state'] = form['target_move']
        parents = ids
        child_ids = obj_account._get_children_and_consol(self.cr, self.uid, ids, ctx)
        
        if child_ids:
            ids = child_ids
        
        accounts = obj_account.read(self.cr, self.uid, ids, ['type','code','name','debit','credit','balance','credit_open','debit_open','parent_id','level','child_id'], ctx)

        for parent in parents:
                if parent in done:
                    continue
                done[parent] = 1
                _process_child(accounts,form['display_account'],parent)
        return self.result_acc
    
    def lines_by_classes(self, form, ids=None, done=None):
        result_class = []
        for obj_line in self.result_acc:
            if obj_line['level'] == 1:
                result_class.append(obj_line)
                
        return result_class
            
    def get_BS_value(self):
        return self.sum_BS
    
    def get_BU_value(self):
        return self.sum_BU
        
        
        

report_sxw.report_sxw('report.account.account.balance.mentis', 'account.account', 'addons/accounting_reports/report/account_balance1.rml', parser=account_balance, header="internal")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
