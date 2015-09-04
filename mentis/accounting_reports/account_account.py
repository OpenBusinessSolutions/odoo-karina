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

from osv import fields, osv
from tools.translate import _
import openerp.addons.decimal_precision as dp

class account_account(osv.osv):
    _inherit = "account.account"

    def __compute1(self, cr, uid, ids, field_names, arg=None, context=None,
                  query='', query_params=()):
        """ compute the balance, debit and/or credit for the provided
        account ids
        Arguments:
        `ids`: account ids
        `field_names`: the fields to compute (a list of any of
                       'balance', 'debit' and 'credit')
        `arg`: unused fields.function stuff
        `query`: additional query filter (as a string)
        `query_params`: parameters for the provided query string
                        (__compute will handle their escaping) as a
                        tuple
        """
        mapping = {
            'balance': "COALESCE(SUM(l.debit),0) - COALESCE(SUM(l.credit), 0) as balance",
            'debit_open': "COALESCE(SUM(l.debit), 0) as debit_open",
            'credit_open': "COALESCE(SUM(l.credit), 0) as credit_open",
            # by convention, foreign_balance is 0 when the account has no secondary currency, because the amounts may be in different currencies
            'foreign_balance': "(SELECT CASE WHEN currency_id IS NULL THEN 0 ELSE COALESCE(SUM(l.amount_currency), 0) END FROM account_account WHERE id IN (l.account_id)) as foreign_balance",
        }
        #get all the necessary accounts
        children_and_consolidated = self._get_children_and_consol(cr, uid, ids, context=context)
        #compute for each account the balance/debit/credit from the move lines
        accounts = {}
        res = {}
        null_result = dict((fn, 0.0) for fn in field_names)
        if children_and_consolidated:
            context['if_date_calc_initial_bal'] = False
            aml_query = self.pool.get('account.move.line')._query_get(cr, uid, context=context)
            
            if context.has_key('date_from'):
                last_pos = aml_query.rfind('AND l.')
                tmp_query = aml_query[:last_pos] #odstranimo (SELECT id FROM account_move WHERE date < \'%s\')'
                aml_query = tmp_query + """AND l.move_id IN (
                                                SELECT AM.id FROM account_move AM LEFT JOIN account_period AP ON AM.period_id = AP.id
                                                WHERE (AM.date < \'{0}\' AND AP.special = False) or AP.special = True)""".format(context['date_from'])

            wheres = [""]
            if query.strip():
                wheres.append(query.strip())
            if aml_query.strip():
                wheres.append(aml_query.strip())
            filters = " AND ".join(wheres)
            # IN might not work ideally in case there are too many
            # children_and_consolidated, in that case join on a
            # values() e.g.:
            # SELECT l.account_id as id FROM account_move_line l
            # INNER JOIN (VALUES (id1), (id2), (id3), ...) AS tmp (id)
            # ON l.account_id = tmp.id
            # or make _get_children_and_consol return a query and join on that
            request = ("SELECT l.account_id as id, " +\
                       ', '.join(mapping.values()) +
                       " FROM account_move_line l" \
                       " WHERE l.account_id IN %s " \
                            + filters +
                       " GROUP BY l.account_id")
            params = (tuple(children_and_consolidated),) + query_params
            
            #______Ce obdobje ni doloceno, potem zacetnega stanmja ne preracunavamo
            #______in nastavim account_id<0 da ne najde nic
            if not context.has_key('period_from') and not context.has_key('date_from'):
                request = ("SELECT l.account_id as id, " +\
                       ', '.join(mapping.values()) +
                       " FROM account_move_line l" \
                       " WHERE l.account_id < 0" \
                       " GROUP BY l.account_id")
            #______
            
            cr.execute(request, params)

            for row in cr.dictfetchall():
                accounts[row['id']] = row

            # consolidate accounts with direct children
            children_and_consolidated.reverse()
            brs = list(self.browse(cr, uid, children_and_consolidated, context=context))
            sums = {}
            currency_obj = self.pool.get('res.currency')
            while brs:
                current = brs.pop(0)
#                can_compute = True
#                for child in current.child_id:
#                    if child.id not in sums:
#                        can_compute = False
#                        try:
#                            brs.insert(0, brs.pop(brs.index(child)))
#                        except ValueError:
#                            brs.insert(0, child)
#                if can_compute:
                for fn in field_names:
                    sums.setdefault(current.id, {})[fn] = accounts.get(current.id, {}).get(fn, 0.0)
                    for child in current.child_id:
                        if child.company_id.currency_id.id == current.company_id.currency_id.id:
                            sums[current.id][fn] += sums[child.id][fn]
                        else:
                            sums[current.id][fn] += currency_obj.compute(cr, uid, child.company_id.currency_id.id, current.company_id.currency_id.id, sums[child.id][fn], context=context)

                # as we have to relay on values computed before this is calculated separately than previous fields
                if current.currency_id and current.exchange_rate and \
                            ('adjusted_balance' in field_names or 'unrealized_gain_loss' in field_names):
                    # Computing Adjusted Balance and Unrealized Gains and losses
                    # Adjusted Balance = Foreign Balance / Exchange Rate
                    # Unrealized Gains and losses = Adjusted Balance - Balance
                    adj_bal = sums[current.id].get('foreign_balance', 0.0) / current.exchange_rate
                    sums[current.id].update({'adjusted_balance': adj_bal, 'unrealized_gain_loss': adj_bal - sums[current.id].get('balance', 0.0)})

            for id in ids:
                res[id] = sums.get(id, null_result)
        else:
            for id in ids:
                res[id] = null_result
        return res

    def _prepare_compute(self, cr, uid, ids, field_names, arg=None, context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        
        if context.has_key('date_from'):
            ctx['initial_bal'] = True
        elif context.has_key('period_from'):
            account_period_obj = self.pool.get('account.period')
            account_period_start_data = account_period_obj.browse(cr, uid, [ctx['period_from']], context=ctx)[0]
            
            #period_company_id = account_period_obj.browse(cr, uid, ctx['period_from'], context=ctx).company_id.id
            #end_period_id = account_period_obj.browse(cr, uid, [ctx['period_from']], context=ctx)[0]
            
            temp_from = account_period_obj.search(cr, uid, [('company_id', '=', account_period_start_data.company_id.id),
                                                            ('fiscalyear_id','=',account_period_start_data.fiscalyear_id.id)],
                                                            order='id', limit=1)[0]
            
            temp_to = account_period_obj.search(cr, uid, [('date_start','<',account_period_start_data.date_start),
                                                          ('company_id','=',account_period_start_data.company_id.id),
                                                          ('fiscalyear_id','=',account_period_start_data.fiscalyear_id.id)],
                                                          order='date_start DESC', limit=1)[0]
            ctx['period_from'] = temp_from
            ctx['period_to'] = temp_to
            
        
        #raise 'napaka'
        res = self.__compute1(cr, uid, ids, field_names, context=ctx)
        return res

    _columns = {
        'credit_open': fields.function(_prepare_compute, digits_compute=dp.get_precision('Account'), string='Credit', multi='balance_open'),
        'debit_open': fields.function(_prepare_compute, digits_compute=dp.get_precision('Account'), string='Debit', multi='balance_open'),
        
    }
   
account_account()

class account_move_line(osv.osv):
    _inherit = "account.move.line"
    
    def _query_get(self, cr, uid, obj='l', context=None):
        res = super(account_move_line, self)._query_get(cr, uid, obj=obj, context=context)
        
        if context.has_key('if_date_calc_initial_bal') and context['if_date_calc_initial_bal']: #preoblikujemo v primeru datuma in izracuna prometa
            last_pos = res.rfind('AND l.')
            tmp_query = res[:last_pos] #odstranimo (SELECT id FROM account_move WHERE date < \'%s\')'
            res = tmp_query + """AND l.move_id IN 
                                            (SELECT AM.id FROM account_move AM LEFT JOIN account_period AP ON AM.period_id = AP.id
                                                 WHERE (AM.date >= \'{0}\' AND AM.date <= \'{1}\' AND AP.special = False))
                                    """.format(context['date_from'],context['date_to'])
        
        return res
account_move_line()