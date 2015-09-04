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

class mrp_production(osv.osv):
    _inherit = 'mrp.production'

    def action_production_end(self, cr, uid, ids, context=None):
        write_res = super(mrp_production, self).action_production_end(cr, uid, ids, context) 
        if write_res:
            _production_ids = self.pool.get('mrp.production').browse(cr, uid, ids, context=None)
            for _production_id in _production_ids:
                _name = _production_id.name
                _product_id = _production_id.product_id.id
                
                product_obj=self.pool.get('product.product')
                accounts = product_obj.get_product_accounts(cr, uid, _product_id, context)
                
                if _production_id.product_id.cost_method == 'average' and accounts['stock_account_input'] and accounts['property_stock_valuation_account_id']:
                    _debit= 0.00
                    _credit = 0.00
                    _move_line_ids = self.pool.get('account.move.line').search(cr, uid, [('name','=',_name),
                                                                                         ('product_id','!=',_product_id)])
                    _move_lines = self.pool.get('account.move.line').browse(cr, uid, _move_line_ids, context=None)
                    for _move_line in _move_lines:
                        _debit += _move_line.debit
                        _credit += _move_line.credit
                    
                    _move_line_ids = self.pool.get('account.move.line').search(cr, uid, [('name','=',_name),
                                                                                         ('product_id','=',_product_id)], order='id')
                    _move_lines = self.pool.get('account.move.line').browse(cr, uid, _move_line_ids, context=None)
    
                    for _move_line in _move_lines:
                        if _move_line.account_id.id == accounts['stock_account_input']:
                            _move_line.write({'credit': _credit}, context)
                        elif _move_line.account_id.id == accounts['property_stock_valuation_account_id']:
                            _move_line.write({'debit': _debit}, context)
                    if _debit and _debit != 0.00:
                        _old_inventory_qty = _production_id.product_id.qty_available or 0.00
                        _old_inventory_value = _old_inventory_qty * _production_id.product_id.standard_price
                        _new_inventory_value = _production_id.product_qty * _debit
                        _new_inventory_qty = _old_inventory_qty + _production_id.product_qty
                        if _new_inventory_qty and _new_inventory_qty != 0.00:
                            _new_standard_price = (_old_inventory_value + _new_inventory_value) / _new_inventory_qty
                        elif _production_id.product_qty and _product_id.product_qty != 0.00:
                            _new_standard_price = _debit / _production_id.product_qty
                        else:
                            _new_standard_price = _debit                        
                        product_obj.write(cr, uid, [_product_id], {'standard_price': _new_standard_price}, context)
        return write_res

mrp_production()