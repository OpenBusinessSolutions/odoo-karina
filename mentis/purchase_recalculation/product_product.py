# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP s.a. (<http://www.openerp.com>)
#    Copyright (C) 2013-TODAY Mentis d.o.o. (<http://www.mentis.si/openerp>)
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
from datetime import datetime
import time
import openerp.addons.decimal_precision as dp

class product_product(osv.Model):
    _inherit="product.product"
    
    _columns = {
        'period_cost_ids': fields.one2many('product.period.cost', 'product_id', 'Cost Price Per Period'),
    }
    
    def _get_inventory_stock_and_cost(self, cr, uid, ids, dates, digits, context):
        if dates is None:
            dates = {}
        _stock = 0.0
        _cost = 0.0
        _date_from = dates.get('date_from', False)
        _sql_string = '  SELECT sil.id \n' \
                      '    FROM stock_inventory_line AS sil \n' \
                      '         INNER JOIN stock_inventory AS si ON si.id = sil.inventory_id \n' \
                      '                                             AND si.state = \'done\' \n' \
                      '                                             AND si.date_done < \'{date_from}\' \n' \
                      '   WHERE sil.product_id = {product} \n' \
                      'ORDER BY si.date_done DESC \n' \
                      '   LIMIT 1'.format(product=ids[0],
                                          date_from=_date_from).replace(',)', ')')
        cr.execute(_sql_string)
        _inventory_line_tuples = cr.fetchall()
        _inventory_line_ids = []
        for _tup in _inventory_line_tuples:
            _inventory_line_ids.append(_tup[0])

        _inventory_lines = self.pool.get('stock.inventory.line').browse(cr, uid, _inventory_line_ids, context)
        for _inventory_line in _inventory_lines:
            for _move_line in _inventory_line.inventory_id.move_ids:
                if _move_line.product_id == ids[0]:
                    _stock = _stock + _move_line.product_qty
                    _acc_move_line_id = self.pool.get('account.move.line').search(cr, uid,
                                                                                  [('stock_move_id', '=', _move_line.id)],
                                                                                  limit=1)
                    if len(_acc_move_line_id) != 0:
                        _acc_move_line = self.pool.get('account.move.line').browse(cr, uid, _acc_move_line_id[0], context)
                        if _acc_move_line:
                            _cost = _acc_move_line.debit + _acc_move_line.credit
        return [round(_stock, digits['quantity']), round(_cost, digits['price'])]

    def _get_start_stock_and_cost(self, cr, uid, ids, dates, digits, context):
        if dates is None:
            dates = {}
        _stock = 0.0
        _cost = 0.0
        _period = False
        _date_from = dates.get('date_from', False)
        _date_to = dates.get('date_to', False)
        
        # izračunam zalogo na začetku obdobja
        _sql_string = '  SELECT sm.id \n' \
                      '    FROM stock_move AS sm \n' \
                      '   WHERE sm.product_id = {product} \n' \
                      '         AND sm.date < \'{date_to}\' \n' \
                      '         AND sm.state = \'done\' \n' \
                      'ORDER BY sm.date;'.format(product=ids[0],
                                                 date_from=_date_from,
                                                 date_to=_date_to).replace(',)', ')')
        
        
        cr.execute(_sql_string)
        _move_tups = cr.fetchall()
        _move_ids = []
        for _tup in _move_tups:
            _move_ids.append(_tup[0])

        _moves = self.pool.get('stock.move').browse(cr, uid, _move_ids, context)
        for _move in _moves:
            if _move.location_id.usage != 'internal' and _move.location_dest_id.usage == 'internal':
                _stock = _stock + _move.product_qty
            elif _move.location_id.usage == 'internal' and _move.location_dest_id.usage != 'internal':
                _stock = _stock - _move.product_qty
        _stock = round(_stock, digits['quantity'])

        # če je zaloga na zečetku obdobja 0 vrnem same nule
        if _stock == round(0.0, digits['quantity']):
            return [round(_stock, digits['quantity']), round(_cost, digits['price']), _period]
        
        # najdem zadnjo prodajo
        _int_location_ids = self.pool.get('stock.location').search(cr, uid, [('usage','=','internal')])
        _sup_location_ids = self.pool.get('stock.location').search(cr, uid, [('usage','=','supplier')])
        _last_out_move_id = self.pool.get('stock.move').search(cr, uid, [('product_id','=',ids[0]),
                                                                         ('date','<',_date_to),
                                                                         ('location_id','in',_int_location_ids),
                                                                         ('location_dest_id','not in',_sup_location_ids),
                                                                         ('state','=','done')],
                                                               order='date desc',
                                                               limit=1)

        # če obstaja zadnja prodaja vzamem ceno iz stock_move-a
        if len(_last_out_move_id) == 1:
            _last_out_move = self.pool.get('stock.move').browse(cr, uid, _last_out_move_id[0], context)
            _period_id = self.pool.get('account.period').find(cr, uid, _last_out_move.date, context)
            _period = self.pool.get('account.period').browse(cr, uid, _period_id[0], context)
            _cost = round(_last_out_move.price_unit, digits['price']) * _stock
            return [round(_stock, digits['quantity']), round(_cost, digits['price']), _period]
            
        # če ni prodaje najdem zadnjo nabavo
        _last_in_move_id = self.pool.get('stock.move').search(cr, uid, [('product_id','=',ids[0]),
                                                                        ('date','<',_date_to),
                                                                        ('location_id','in',_sup_location_ids),
                                                                        ('location_dest_id','in',_int_location_ids),
                                                                        ('state','=','done')],
                                                              order='date desc',
                                                              limit=1)
        # če obstaja zadnja prodaja vzamem ceno iz stock_move-a
        if len(_last_in_move_id) == 1:
            _last_in_move = self.pool.get('stock.move').browse(cr, uid, _last_in_move_id[0], context)
            _period_id = self.pool.get('account.period').find(cr, uid, _last_in_move.date, context)
            _period = self.pool.get('account.period').browse(cr, uid, _period_id[0], context)
            _cost = round(_last_in_move.price_unit, digits['price']) * _stock
            return [round(_stock, digits['quantity']), round(_cost, digits['price']), _period]

        # če ni niti zadnje prodaje niti zadnje zaloge vrnem 0
        return [round(_stock, digits['quantity']), round(_cost, digits['price']), _period]

    def _get_purchase_amount_and_cost(self, cr, uid, ids, dates, digits, context):
        if dates is None:
            dates = {}

        _stock = 0.0
        _cost = 0.0

        _date_from = dates.get('date_from', False)
        _date_to = dates.get('date_to', False)
        if _date_from and _date_to:
            _location_ids = self.pool.get('stock.location').search(cr, uid, [('usage','=','supplier')])
            _sql_string = 'SELECT id \n' \
                          '  FROM stock_move \n' \
                          ' WHERE product_id = {product} \n' \
                          '       AND date >= \'{date_from}\' \n' \
                          '       AND date <= \'{date_to}\' \n' \
                          '       AND state = \'done\' \n' \
                          '       AND (location_id IN {locations} \n' \
                          '            OR location_dest_id IN {locations})'.format(product = ids[0],
                                                                                   date_from = _date_from,
                                                                                   date_to = _date_to,
                                                                                   locations = tuple(_location_ids)).replace(',)', ')')
            cr.execute(_sql_string)
            _stock_move_tups = cr.fetchall()
            _stock_move_ids = []
            for _tup in _stock_move_tups:
                _stock_move_ids.append(_tup[0])

            _moves = self.pool.get('stock.move').browse(cr, uid, _stock_move_ids, context)
            for _move in _moves:
                if _move.location_id.id in _location_ids:
                    _cost = _cost + (_move.product_qty * _move.price_unit)
                    _stock = _stock + _move.product_qty
                elif _move.location_dest_id.id in _location_ids:
                    _cost = _cost - (_move.product_qty * _move.price_unit)
                    _stock = _stock - _move.product_qty

        return [round(_stock, digits['quantity']), round(_cost, digits['price'])]

    def _set_period_cost(self, cr, uid, ids, dates, digits, average_price, context):
        if dates is None:
            dates = {}
 
        _product_id = self.pool.get('product.product').browse(cr, uid, ids[0], context)
 
        accounts = self.pool.get('product.product').get_product_accounts(cr, uid, _product_id.id, context)
        accounts['stock_account_expense'] = _product_id.property_account_expense and _product_id.property_account_expense.id or False
        if not accounts['stock_account_expense']:
            accounts['stock_account_expense'] = _product_id.categ_id.property_account_expense_categ and _product_id.categ_id.property_account_expense_categ.id or False
 
        if not accounts['stock_journal'] \
           or not accounts['stock_account_input'] \
           or not accounts['stock_account_output'] \
           or not accounts['property_stock_valuation_account_id'] \
           or not accounts['stock_account_expense']:
            raise osv.except_osv(_('Error!'), _('Specify valuation accounts for product: %s.') % (_product_id.name))
 
 
        _date_from = dates.get('date_from', False)
        _date_to = dates.get('date_to', False)
        if _date_from and _date_to:
            # seznam vseh stock move ki jim je treba popravit ceno na povprečno
            _location_ids = self.pool.get('stock.location').search(cr, uid, [('usage','=','supplier')])
            _sql_string = 'SELECT id \n' \
                          '  FROM stock_move \n' \
                          ' WHERE product_id = {product} \n' \
                          '       AND date >= \'{date_from}\' \n' \
                          '       AND date <= \'{date_to}\' \n' \
                          '       AND state = \'done\' \n' \
                          '       AND location_id NOT IN {locations} \n' \
                          '       AND location_dest_id NOT IN {locations} \n' \
                          '       AND NOT EXISTS (SELECT inv.move_id \n' \
                          '                         FROM stock_inventory_move_rel AS inv \n' \
                          '                        WHERE inv.move_id = stock_move.id)'.format(product = ids[0],
                                                                                              date_from = _date_from,
                                                                                              date_to = _date_to,
                                                                                              locations = tuple(_location_ids)).replace(',)', ')')
            #print _sql_string
            cr.execute(_sql_string)
            _stock_move_tups = cr.fetchall()
            _stock_move_ids = []
            for _tup in _stock_move_tups:
                _stock_move_ids.append(_tup[0])
             
            if len(_stock_move_ids) > 0:
                # popravim cene na stock_move
                _sql_string = 'UPDATE stock_move \n' \
                              '   SET price_unit = ROUND({average_price}, {digits}) \n' \
                              ' WHERE id IN {stock_moves}'.format(average_price = average_price,
                                                                  digits = digits['price'],
                                                                  stock_moves = tuple(_stock_move_ids)).replace(',)', ')')
                #print _sql_string
                cr.execute(_sql_string)
 
                # popravim vse ustrezne stock_journale
                _journal_ids = self.pool.get('account.journal').search(cr, uid, [('type','=','stock')])
                _location_ids = self.pool.get('stock.location').search(cr, uid, [('usage','=','internal')])
                _sql_string = 'WITH aml AS (SELECT aml.id,                                                            \n' \
                              '               CASE                                                                    \n' \
                              '                 WHEN (sm.location_id IN {locations}                                   \n' \
                              '                       AND aml.account_id = {account_output})                          \n' \
                              '                      OR (sm.location_dest_id IN {locations}                           \n' \
                              '                          AND aml.account_id = {account_valuation})                    \n' \
                              '                   THEN ROUND({average_price} * aml.quantity, {digits})                \n' \
                              '                 ELSE 0.00                                                             \n' \
                              '               END::NUMERIC AS debit,                                                  \n' \
                              '               CASE                                                                    \n' \
                              '                 WHEN (sm.location_id IN {locations}                                   \n' \
                              '                       AND aml.account_id = {account_valuation})                       \n' \
                              '                      OR (sm.location_dest_id IN {locations}                           \n' \
                              '                          AND aml.account_id = {account_output})                       \n' \
                              '                   THEN ROUND({average_price} * aml.quantity, {digits})                \n' \
                              '                 ELSE 0.00                                                             \n' \
                              '               END::NUMERIC AS credit                                                  \n' \
                              '          FROM stock_move AS sm                                                        \n' \
                              '               INNER JOIN account_move_line AS aml ON aml.stock_move_id = sm.id        \n' \
                              '                                                      AND journal_id = {stock_journal} \n' \
                              '                                                      AND aml.state = \'valid\'        \n' \
                              '         WHERE sm.id IN {stock_moves})                                                 \n' \
                              'UPDATE account_move_line                                                               \n' \
                              '   SET debit = (SELECT aml.debit                                                       \n' \
                              '                  FROM aml                                                             \n' \
                              '                 WHERE aml.id = account_move_line.id),                                 \n' \
                              '      credit = (SELECT aml.credit                                                      \n' \
                              '                  FROM aml                                                             \n' \
                              '                 WHERE aml.id = account_move_line.id)                                  \n' \
                              ' WHERE id IN (SELECT id                                                                \n' \
                              '                FROM aml)'.format(locations = tuple(_location_ids),
                                                                 account_output = accounts['stock_account_output'],
                                                                 account_valuation = accounts['property_stock_valuation_account_id'],
                                                                 average_price = average_price,
                                                                 digits = digits['account'],
                                                                 stock_moves = tuple(_stock_move_ids),
                                                                 stock_journal = accounts['stock_journal']).replace(',)', ')')
                #print _sql_string
                cr.execute(_sql_string)
                 
                # popravim vse knjižbe porabe na izdanih računih in dobropisih
                _journal_ids = self.pool.get('account.journal').search(cr, uid, [('type','in',('sale', 'sale_refund'))])
                _sql_string = 'WITH aml AS (SELECT aml.id,                                                \n' \
                              '               CASE                                                        \n' \
                              '                 WHEN (aj.type = \'sale\'                                  \n' \
                              '                       AND aml.account_id = {account_expense})             \n' \
                              '                      OR (aj.type = \'sale_refund\'                        \n' \
                              '                          AND aml.account_id = {account_output})           \n' \
                              '                   THEN ROUND({average_price}  * aml.quantity, {digits})   \n' \
                              '                 ELSE 0.00                                                 \n' \
                              '               END::NUMERIC AS debit,                                      \n' \
                              '               CASE                                                        \n' \
                              '                 WHEN (aj.type = \'sale\'                                  \n' \
                              '                       AND aml.account_id = {account_output})              \n' \
                              '                      OR (aj.type = \'sale_refund\'                        \n' \
                              '                          AND aml.account_id = {account_expense})          \n' \
                              '                   THEN ROUND({average_price} * aml.quantity, {digits})    \n' \
                              '                 ELSE 0.00                                                 \n' \
                              '               END::NUMERIC AS credit                                      \n' \
                              '          FROM account_move_line AS aml                                    \n' \
                              '               INNER JOIN account_journal AS aj ON aj.id = aml.journal_id  \n' \
                              '         WHERE aml.product_id = {product}                                  \n' \
                              '               AND aml.journal_id IN {journals}                            \n' \
                              '               AND aml.account_id IN ({account_output}, {account_expense}) \n' \
                              '               AND aml.date >= \'{date_from}\'                             \n' \
                              '               AND aml.date <= \'{date_to}\'                               \n' \
                              '               AND aml.state = \'valid\')                                  \n' \
                              'UPDATE account_move_line                                                   \n' \
                              '   SET debit = (SELECT aml.debit                                           \n' \
                              '                  FROM aml                                                 \n' \
                              '                 WHERE aml.id = account_move_line.id),                     \n' \
                              '      credit = (SELECT aml.credit                                          \n' \
                              '                  FROM aml                                                 \n' \
                              '                 WHERE aml.id = account_move_line.id)                      \n' \
                              ' WHERE id IN (SELECT id                                                    \n' \
                              '                FROM aml)'.format(account_expense = accounts['stock_account_expense'],
                                                                 account_output = accounts['stock_account_output'],
                                                                 average_price = average_price,
                                                                 digits = digits['account'],
                                                                 product = ids[0],
                                                                 journals = tuple(_journal_ids),
                                                                 date_from = _date_from,
                                                                 date_to = _date_to).replace(',)', ')')
                #print _sql_string
                cr.execute(_sql_string)
 
        return True
