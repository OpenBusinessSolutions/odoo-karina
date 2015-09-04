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

import time
from lxml import etree
from osv import fields, osv
from tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
import decimal_precision as dp
from tools.translate import _

class stock_partial_return_line(osv.TransientModel):
    _name = "stock.partial.return.line"
    _rec_name = 'product_id'
    _columns = {
        'default_code'      : fields.char('Internal Reference', size=64),
        'product_id'        : fields.many2one('product.product', string="Product", required=True, ondelete='CASCADE'),
        'quantity'          : fields.float("Calculated Quantity", digits_compute=dp.get_precision('Product Unit of Measure'), required=True),
        'quantity_delivered': fields.float("Delivered Quantity", digits_compute=dp.get_precision('Product Unit of Measure'), required=True),
        'quantity_returned' : fields.float("Returned Quantity", digits_compute=dp.get_precision('Product Unit of Measure'), required=True),
        'move_id'           : fields.many2one('stock.move', "Move", ondelete='CASCADE'),
        'wizard_id'         : fields.many2one('stock.partial.return', string="Wizard", ondelete='CASCADE'),
    }

stock_partial_return_line()


class stock_partial_return(osv.osv_memory):
    _name = "stock.partial.return"
    _rec_name = 'picking_id'
    _description = "Partial Return Processing Wizard"
    _columns = {
        'date'      : fields.datetime('Date', required=True),
        'move_ids'  : fields.one2many('stock.partial.return.line', 'wizard_id', 'Product Returns'),
        'picking_id': fields.many2one('stock.picking', 'Picking', required=True, ondelete='CASCADE'),
     }
    
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(stock_partial_return, self).default_get(cr, uid, fields, context=context)
        picking_ids = context.get('active_ids', [])
        active_model = context.get('active_model')

        if not picking_ids or len(picking_ids) != 1:
            # Partial Picking Processing may only be done for one picking at a time
            return res
        assert active_model in ('stock.picking', 'stock.picking.in', 'stock.picking.out'), 'Bad context propagation'
        picking_id, = picking_ids
        if 'picking_id' in fields:
            res.update(picking_id=picking_id)
        if 'move_ids' in fields:
            picking = self.pool.get('stock.picking').browse(cr, uid, picking_id, context=context)
            moves = [self._partial_move_for(cr, uid, m) for m in picking.move_lines if m.state not in ('draft','cancel')]
            res.update(move_ids=moves)
        if 'date' in fields:
            res.update(date=time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
        return res
    
    def _partial_move_for(self, cr, uid, move):
        partial_move = {
            'default_code'      : move.product_id.default_code,
            'product_id'        : move.product_id.id,
            'quantity'          : move.state in ('assigned','done','confirmed') and move.product_qty or 0,
            'quantity_delivered': move.state in ('assigned','done','confirmed') and (move.product_qty + move.product_qty_returned) or 0,
            'quantity_returned' : move.state in ('assigned','done','confirmed') and move.product_qty_returned or 0,
            'move_id'           : move.id,
        }
        return partial_move
    
    def do_confirm(self, cr, uid, ids, context=None):
        _partial_return = self.browse(cr, uid, ids[0], context=context)
        for _return_line in _partial_return.move_ids:
            _product_qty = _return_line.quantity_delivered - _return_line.quantity_returned
            _product_uos_qty = _product_qty * _return_line.move_id.product_id.uos_coeff
            _product_qty_returned = _return_line.quantity_returned

            if _return_line.move_id.product_qty != _product_qty \
               or _return_line.move_id.product_qty_returned != _product_qty_returned:

                move_obj = self.pool.get('stock.move')
                move_obj.write(cr, uid, [_return_line.move_id.id], {'product_qty': _product_qty,
                                                                    'product_uos_qty': _product_uos_qty,
                                                                    'product_qty_returned': _product_qty_returned})
                move_obj._move_return_valuation(cr, uid, [_return_line.move_id.id], context)
                
                move_obj.create_return_move(cr, uid, [_return_line.move_id.id], context)
                
        return True
    
stock_partial_return()