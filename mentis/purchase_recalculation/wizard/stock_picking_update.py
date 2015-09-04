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
from openerp.osv.orm import setup_modifiers
import decimal_precision as dp
from tools.translate import _
from lxml import etree

class stock_picking_update_line(osv.TransientModel):
    _name = "stock.picking.update.line"
    _rec_name = 'product_id'
    _columns = {
        'product_id': fields.many2one('product.product', string="Product", required=True, ondelete='CASCADE'),
        'quantity': fields.float("Quantity", digits_compute=dp.get_precision('Product Unit of Measure')),
        'quantity_new': fields.float("New Quantity", digits_compute=dp.get_precision('Product Unit of Measure'),
                                     required=True),
        'price_unit': fields.float("Price Unit", digits_compute=dp.get_precision('Product Price')),
        'price_unit_new': fields.float("New Price Unit", digits_compute=dp.get_precision('Product Price'),
                                       required=True),
        'move_id': fields.many2one('stock.move', "Move", ondelete='CASCADE'),
        'wizard_id': fields.many2one('stock.picking.update', string="Wizard", ondelete='CASCADE'),
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        res = super(stock_picking_update_line, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type,
                                                                     context=context, toolbar=toolbar, submenu=submenu)
        _picking_id = context and context.get('picking_id', False)
        if _picking_id:
            _invisible = '0'
            _picking = self.pool.get('stock.picking').browse(cr, uid, _picking_id, None)
            for _move in _picking.move_lines:
                if _move.location_id.usage != 'supplier' and _move.location_dest_id.usage != 'supplier':
                    _invisible = '1'
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='price_unit']"):
                node.set('invisible', _invisible)
                setup_modifiers(node, res['fields']['price_unit'], None, True)
            for node in doc.xpath("//field[@name='price_unit_new']"):
                node.set('invisible', _invisible)
                setup_modifiers(node, res['fields']['price_unit_new'], None, True)
            res['arch'] = etree.tostring(doc)    
        return res

stock_picking_update_line()

class stock_picking_update(osv.TransientModel):
    _name = "stock.picking.update"
    _rec_name = 'picking_id'
    _description = "Update Picking Values Processing Wizard"
    _columns = {
        'date_delivered': fields.datetime('Date delivered', required=True),
        'move_ids': fields.one2many('stock.picking.update.line', 'wizard_id', 'Product Lines'),
        'picking_id': fields.many2one('stock.picking', 'Picking', required=True, ondelete='CASCADE'),
     }
   
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(stock_picking_update, self).default_get(cr, uid, fields, context=context)
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
            moves = [self._update_values_for(cr, uid, m) for m in picking.move_lines if m.state not in ('cancel')]
            res.update(move_ids=moves)
        if 'date_delivered' in fields:
            picking = self.pool.get('stock.picking').browse(cr, uid, picking_id, context=context)
            res.update(date_delivered=picking.date_done)
        return res
    
    def _update_values_for(self, cr, uid, move):
        context = {}
        _costs_installed = self.pool.get('stock.picking').fields_get(cr, uid, ['landing_costs_line_ids'], context) != {}
        _price_unit = move.price_unit
        if _costs_installed:
            if len(move.landing_costs_line_ids) <> 0 \
               or len(move.picking_id.landing_costs_line_ids) <> 0:
                _price_unit = move.price_unit_without_costs
        
        update_move = {'product_id': move.product_id.id,
                       'quantity': move.product_qty or 0,
                       'quantity_new': move.product_qty or 0,
                       'price_unit': _price_unit or 0,
                       'price_unit_new': _price_unit or 0,
                       'move_id': move.id}
        return update_move
    
    def do_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ctx = {}
        _update_picking = self.browse(cr, uid, ids[0], context=context)
        _picking = self.pool.get('stock.picking').browse(cr, uid, _update_picking.picking_id.id, context=context)
        if _picking.date_done != _update_picking.date_delivered:
            ctx['date_delivered'] = _update_picking.date_delivered
        for _update_line in _update_picking.move_ids:
            ctx['move%s' % _update_line.move_id.id] = {'quantity': _update_line.quantity_new,
                                                       'price_unit': _update_line.price_unit_new}
        if ctx:
            self.pool.get('stock.picking')._picking_update(cr, uid, [_picking.id], ctx)
        return {'type': 'ir.actions.act_window_close'}
    
stock_picking_update()