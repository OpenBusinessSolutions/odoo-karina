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
from tools.translate import _
from tools.safe_eval import safe_eval

class account_invoice(osv.Model):
    _inherit = "account.invoice"

    def action_number(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        res = super(account_invoice, self).action_number(cr, uid, ids, context)
        if res:
            _invoice_ids = self.search(cr, uid, [('id','in',ids)], context)
            if len(_invoice_ids) > 0:
                ctx = {}
                _costs_installed = self.pool.get('stock.picking.in').fields_get(cr, uid, ['landing_costs_line_ids'], context) != {}
                _picking_ids = []
                for _invoice in self.browse(cr, uid, _invoice_ids, context):
                    _src_usage = False
                    _dst_usage = False
                    
                    if _invoice.type == 'in_invoice':
                        _src_usage = 'supplier'
                        _dst_usage = 'internal'
                    elif _invoice.type == 'in_refund':
                        _src_usage = 'internal'
                        _dst_usage = 'supplier'
                    elif _invoice.type == 'out_invoice':
                        _src_usage = 'internal'
                        _dst_usage = 'customer'
                    elif _invoice.type == 'out_refund':
                        _src_usage = 'customer'
                        _dst_usage = 'internal'

                    if not _src_usage and not _dst_usage:
                        continue

                    for _line in _invoice.invoice_line:
                        _quantity = 0.0
                        _uom_id = False
                        
                        _order_line_ids = []
                        _stock_move_ids = []
                        if _src_usage == 'supplier' or _dst_usage == 'supplier':
                            _order_line_ids = self.pool.get('purchase.order.line').search(cr, uid, [('invoice_lines','=',_line.id)])                        
                            _stock_move_ids = self.pool.get('stock.move').search(cr, uid, [('purchase_line_id','in',_order_line_ids),
                                                                                           ('state','=','done'),
                                                                                           ('location_id.usage','=',_src_usage),
                                                                                           ('location_dest_id.usage','=',_dst_usage)])
                        else:
                            _order_line_ids = self.pool.get('sale.order.line').search(cr, uid, [('invoice_lines','=',_line.id)])                        
                            _stock_move_ids = self.pool.get('stock.move').search(cr, uid, [('sale_line_id','in',_order_line_ids),
                                                                                           ('state','=','done'),
                                                                                           ('location_id.usage','=',_src_usage),
                                                                                           ('location_dest_id.usage','=',_dst_usage)])

                        if len(_stock_move_ids) > 0:
                            _stock_moves = self.pool.get('stock.move').browse(cr, uid, _stock_move_ids, context)
                            if safe_eval(self.pool.get('ir.config_parameter').get_param(cr, uid, 'account.check_quantity_on_invoices', 'False')):
                                for _stock_move in _stock_moves:
                                    _quantity = _quantity + _stock_move.product_qty
                                    _uom_id = _stock_move.product_uom.id

                                if _line.uos_id.id == _uom_id and _quantity != _line.quantity:
                                    _text = _line.invoice_id.origin + ' - ' + _line.name
                                    raise osv.except_osv(_('Error!'), _('Invoiced quantity is different than received quantity.\n' + _text))
                            
                            if _line.uos_id.id == _uom_id and (_src_usage == 'supplier' or _dst_usage == 'supplier'):
                                for _stock_move in _stock_moves:
                                    _updated = False
                                    if _costs_installed:
                                        _has_costs = len(_stock_move.landing_costs_line_ids) <> 0 or len(_stock_move.picking_id.landing_costs_line_ids) <> 0
                                        if (_has_costs and _stock_move.price_unit_without_costs != _line.price_unit) \
                                            or (not _has_costs and _stock_move.price_unit != _line.price_unit):
                                            ctx['move%s' % (_stock_move.id)] = {'price_unit': _line.price_unit,
                                                                                'price_unit_without_costs': False,
                                                                                'quantity': False}
                                            _updated = True
                                    else:
                                        if _stock_move.price_unit != _line.price_unit:
                                            ctx['move%s' % (_stock_move.id)] = {'price_unit': _line.price_unit,
                                                                                'quantity': False}
                                            _updated = True
                                    if _updated:
                                        _picking_ids.append(_stock_move.picking_id.id)
                    if _picking_ids:
                        self.pool.get('stock.picking')._picking_update(cr, uid, _picking_ids, ctx)
        return res
                
account_invoice()