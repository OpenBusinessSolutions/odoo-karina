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

from osv import fields, osv, orm
from openerp import netsvc
from openerp import tools

class stock_move(osv.Model):
    _inherit = "stock.move"
    
    def _create_account_move_line(self, cr, uid, move, src_account_id, dest_account_id, reference_amount, reference_currency_id, context=None):
        _move_lines = super(stock_move, self)._create_account_move_line(cr, uid, move, src_account_id, dest_account_id, reference_amount, reference_currency_id, context=context)
        _debit_lines = _move_lines[0][2]
        _credit_lines = _move_lines[1][2]
        _debit_lines['stock_move_id'] = move.id
        _credit_lines['stock_move_id'] = move.id
        return [(0, 0, _debit_lines), (0, 0, _credit_lines)]

    def _move_update_values(self, cr, uid, ids, context, date_delivered, quantity, price_unit):
        _costs_installed = self.pool.get('stock.move').fields_get(cr, uid, ['landing_costs_line_ids'], context) != {}
        _moves = self.pool.get('stock.move').browse(cr, uid, ids, context)
        for _move in _moves:
            if not date_delivered:
                date_delivered = _move.date
            if not quantity:
                quantity = _move.product_qty
            if _costs_installed:
                if not price_unit:
                    price_unit = _move.price_unit_without_costs
                self.pool.get('stock.move').write(cr, uid, [_move.id], {'date': date_delivered,
                                                                        'product_qty': quantity,
                                                                        'price_unit': price_unit,
                                                                        'price_unit_without_costs': False})
            else:
                if not price_unit:
                    price_unit = _move.price_unit
                self.pool.get('stock.move').write(cr, uid, [_move.id], {'date': date_delivered,
                                                                        'product_qty': quantity,
                                                                        'price_unit': price_unit})
                
        return True

    def _move_update_costs(self, cr, uid, ids, context):
        _moves = self.pool.get('stock.move').browse(cr, uid, ids, context)
        for _move in _moves:
            if _move.landing_costs_line_ids or _move.picking_id.landing_costs_line_ids:
                _price_unit_without_costs = _move.price_unit
                _price_unit = _move.price_unit_with_costs
            else:
                _price_unit_without_costs = False
                _price_unit = _move.price_unit
            self.pool.get('stock.move').write(cr, uid, [_move.id], {'price_unit': _price_unit,
                                                                    'price_unit_without_costs': _price_unit_without_costs})
        return True

    def _move_update_valuation(self, cr, uid, ids, context):
        _moves = self.pool.get('stock.move').browse(cr, uid, ids, context)
        for _move in _moves:
            _acc_move_ids = self.pool.get('account.move.line').search(cr, uid, [('stock_move_id','=',_move.id)])

            _type = False
            if _move.location_id.usage == 'supplier' and _move.location_dest_id.usage == 'internal':    # prejem od dobavitelja
                _type = 'in'
            elif _move.location_id.usage == 'internal' and _move.location_dest_id.usage == 'supplier':  # vračilo dobavitelju
                _type = 'out_return'
            elif _move.location_id.usage == 'internal' and _move.location_dest_id.usage == 'customer':  # dobava kupcu
                _type = 'out'
            elif _move.location_id.usage == 'customer' and _move.location_dest_id.usage == 'internal':  # vračilo kupca
                _type = 'in_return'
            elif _move.location_id.usage == 'internal' and _move.location_dest_id.usage not in ('supplier', 'customer'):  # interna izdaja iz skladišča
                _type = 'out_internal'
            elif _move.location_id.usage not in ('supplier', 'customer') and _move.location_dest_id.usage == 'internal':  # interni prejem na skladišče
                _type = 'in_internal'
            
            if _acc_move_ids and _type:
                _acc_move_lines = self.pool.get('account.move.line').browse(cr, uid, _acc_move_ids, context)
                _src_company_ctx = dict(context, force_company=_move.location_id.company_id.id)
                _journal_id, _acc_src, _acc_dest, _acc_valuation = self.pool.get('stock.move')._get_accounting_data_for_valuation(cr, uid, _move, _src_company_ctx)
                for _acc_move_line in _acc_move_lines:
                    if _acc_move_line.account_id.id == _acc_valuation:
                        if _type in ('in', 'in_return', 'in_internal'):
                            _debit = _move.product_qty * _move.price_unit
                            _credit = 0.0
                        elif _type in ('out', 'out_return', 'out_internal'):
                            _debit = 0.0
                            _credit = _move.product_qty * _move.price_unit
                        _acc_move_line.write({'date': _move.date,
                                              'quantity': _move.product_qty,
                                              'debit': _debit,
                                              'credit': _credit})
                    elif _acc_move_line.account_id.id == _acc_src:
                        if _type in ('in', 'in_internal'):
                            _debit = 0.0
                            _credit = _move.product_qty * _move.price_unit
                        elif _type == 'out_return':
                            _debit = _move.product_qty * _move.price_unit
                            _credit = 0.0
                        _acc_move_line.write({'date': _move.date,
                                              'quantity': _move.product_qty,
                                              'debit': _debit,
                                              'credit': _credit})
                    elif _acc_move_line.account_id.id == _acc_dest:
                        if _type in ('out', 'out_internal'):
                            _debit = _move.product_qty * _move.price_unit
                            _credit = 0.0
                        elif _type == 'in_return':
                            _debit = 0.0
                            _credit = _move.product_qty * _move.price_unit
                        _acc_move_line.write({'date': _move.date,
                                              'quantity': _move.product_qty,
                                              'debit': _debit,
                                              'credit': _credit})
        return True

    def write(self, cr, uid, ids, vals, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        frozen_fields = set(['product_qty', 'product_uom', 'product_uos_qty', 'product_uos', 'location_id', 'location_dest_id', 'product_id'])
        if frozen_fields.intersection(vals):
            return super(stock_move, self).write(cr, 1, ids, vals, context=context)
        else:
            return super(stock_move, self).write(cr, uid, ids, vals, context=context)
