# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP s.a. (<http://www.openerp.com>).
#    Copyright (C) 2012-TODAY Mentis d.o.o. (<http://www.mentis.si/openerp>)
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
import decimal_precision as dp
from openerp.tools.safe_eval import safe_eval

class stock_move(osv.osv):
    _inherit = "stock.move"

    def _move_return_valuation(self, cr, uid, ids, context):
        _moves = self.pool.get('stock.move').browse(cr, uid, ids, context)
        for _move in _moves:
            _acc_move_ids = self.pool.get('account.move.line').search(cr, uid, [('stock_move_id','=',_move.id)])
            if _acc_move_ids:
                _acc_move_lines = self.pool.get('account.move.line').browse(cr, uid, _acc_move_ids, context)
                _src_company_ctx = dict(context, force_company=_move.location_id.company_id.id)
                _journal_id, _acc_src, _acc_dest, _acc_valuation = self.pool.get('stock.move')._get_accounting_data_for_valuation(cr, uid, _move, _src_company_ctx)
                for _acc_move_line in _acc_move_lines:
                    if _acc_move_line.account_id.id == _acc_dest:
                        _acc_move_line.write({'date': _move.date,
                                              'quantity': _move.product_qty,
                                              'debit': _move.product_qty * _move.price_unit})
                    elif _acc_move_line.account_id.id == _acc_valuation:
                        _acc_move_line.write({'date': _move.date,
                                              'quantity': _move.product_qty,
                                              'credit': _move.product_qty * _move.price_unit})
        return True

    _columns = {
        'product_qty_returned': fields.float('Quantity Returned', digits_compute=dp.get_precision('Product Unit of Measure'), ),
        'return_move_id'      : fields.many2one('stock.move', required=False)
    }
    _defaults = {
        'product_qty_returned': 0.0,
        'return_move_id'      : False
    }

    def create_return_move(self, cr, uid, ids, context=None):
        _ir_config_parameter = self.pool.get('ir.config_parameter')
        _return_location_id = safe_eval(_ir_config_parameter.get_param(cr, uid, 'stock.return_location', 'False'))

        for _move in self.browse(cr, uid, ids, context):
            _product_qty = _move.basket_deliverd - _move.product_qty
            _product_uos_qty = _product_qty * _move.product_id.uos_coeff 

            if not _move.return_move_id and _product_qty != 0.0:
                _vals = {}
                _vals['product_id'] = _move.product_id.id
                _vals['product_qty'] = _product_qty
                _vals['product_uom'] = _move.product_uom.id
                _vals['product_uos_qty'] = _product_uos_qty
                _vals['product_uos'] = _move.product_uos.id
                _vals['price_unit'] = _move.price_unit
                _vals['location_id'] = _move.location_id.id
                _vals['name'] = _move.name
                _vals['origin'] = _move.origin
                _vals['location_dest_id'] = _return_location_id

                _return_move_id = self.pool.get('stock.move').create(cr, uid, _vals, context)
                self.pool.get('stock.move').write(cr, uid, [_return_move_id], _vals)
                self.pool.get('stock.move').action_done(cr, uid, [_return_move_id], context)

                self.pool.get('stock.move').write(cr, uid, [_move.id], {'return_move_id': _return_move_id})

            elif _move.return_move_id and _move.return_move_id.product_qty != _product_qty and _product_qty != 0.0:
                self.pool.get('stock.move').write(cr, uid, [_move.return_move_id.id], {'product_qty': _product_qty,
                                                                                       'product_uos_qty': _product_uos_qty})
            elif _move.return_move_id and _product_qty == 0:
                _move.return_move_id.write({'state': 'draft'})
                _move.return_move_id.unlink()

        return True

stock_move()
