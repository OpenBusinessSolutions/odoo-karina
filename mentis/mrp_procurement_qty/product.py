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

class product_product(osv.osv):
	_inherit = "product.product"
	
	def _check_unique_insesitive(self, cr, uid, ids, context=None):
		sr_ids = self.search(cr, 1 ,[], context=context)
		lst = [x.default_code.lower() for x in self.browse(cr, uid, sr_ids, context=context) if x.default_code and x.id not in ids]
		
		for self_obj in self.browse(cr, uid, ids, context=context):
			if self_obj.default_code and self_obj.default_code.lower() in  lst:
				return False
			return True
	
	_columns = {
        'qty_delivery_available': fields.integer('Product quantity available'),
    }
	_defaults = {
        'qty_delivery_available': lambda *a: 0,
    }
	_constraints = [(_check_unique_insesitive, 'Interni sklic mora biti edinstven!', ['default_code'])]

	def copy(self, cr, uid, id, default=None, context=None):
		if not default:
			default = {}
		
		default_code_copy = self.browse(cr, uid, id).default_code + '_copy'
		default.update({
			'default_code': default_code_copy
		})
		return super(product_product, self).copy(cr, uid, id, default, context=context)
	
	def qty_available_location(self, cr, uid, ids, locations=False, context=None):
		if not locations:
			return 0.0
		
		if context == None:
			context = {}
		
		for _product in self.browse(cr, uid, ids, context):
			_stock_move_ids = self.pool.get('stock.move').search(cr, uid, [('product_id','=',_product.id),
																			'|',
																			('location_id','in',locations),
			                                                                ('location_dest_id','in',locations),
			                                                               	('state','=','done')],
			                                                                order='date')
			
			_qty_available = 0.0
			for _stock_move in self.pool.get('stock.move').browse(cr, uid, _stock_move_ids, context):
				if (_stock_move.location_dest_id.id in locations):
					_qty_available = _qty_available + _stock_move.product_qty
					
				if (_stock_move.location_id.id in locations):
					_qty_available = _qty_available - _stock_move.product_qty
					
#				if locations.get(_stock_move.location_dest_id, False):
#					_qty_available = _qty_available + _stock_move.product_qty
#				if locations.get(_stock_move.location_id, False):
#					_qty_available = _qty_available - _stock_move.product_qty

			return _qty_available
	
product_product()

def true_rounding(f, r):
	if not r:
		return f
	
	_index = r
	_count = 0
	
	while _index % 1 > 0:
		_index = _index * 10
		_count += 1 

	_result = round(f / r) * r
	_result = round(_result, _count)
	
	return _result

class product_uom(osv.osv):
	_inherit = 'product.uom'
	
#	def _compute_qty(self, cr, uid, from_uom_id, qty, to_uom_id=False):
#		res = super(product_uom, self)._compute_qty(cr, uid, from_uom_id=from_uom_id, qty=qty, to_uom_id=to_uom_id)
#		res_rounded = round(res, 2)
#		
#		temp={}
#		temp[0] = res
#		temp[1] = res_rounded
#		
#		return res_rounded
	def _compute_qty_obj(self, cr, uid, from_unit, qty, to_unit, context=None):
		res = super(product_uom, self)._compute_qty_obj(cr, uid, from_unit=from_unit, qty=qty, to_unit=to_unit, context=context)
		
		if to_unit:
			res = true_rounding(res * to_unit.factor, to_unit.rounding)
		return res

product_uom()

class stock_change_product_qty(osv.osv_memory):
	_inherit = "stock.change.product.qty"
	
	def change_product_qty(self, cr, uid, ids, context=None):
		res = super(stock_change_product_qty,self).change_product_qty(cr, uid, ids, context=context)
		
		stock_move_obj = self.pool.get('stock.move')
		product_obj = self.pool.get('product.product')
		product_id = context and context.get('active_id', False)
		
		#1. Najdemo ID inventory lokacije tega produkta
		for prod_line in product_obj.browse(cr, uid, [product_id]):
			inventory_id = prod_line.product_tmpl_id.property_stock_inventory.id
		
		#2. Najdem stock.move, ki so bili kreirani s spremembo zaloge in jim status postavimo na 2
		stock_ids = stock_move_obj.search(cr, uid, [
												('product_id', '=', product_id),
												'|',
												('location_id', '=', inventory_id),
												('location_dest_id', '=', inventory_id),
												('basket_status', '!=', 2),
												])
		stock_move_obj.write(cr, uid, stock_ids, {'basket_status':2})
		
		#3. Klicemo funkcijo za preracun zaloge
		stock_move_obj.get_qty_delivery_available(cr, uid, False, False, product_id, context=context)
		
		return res
	
stock_change_product_qty()

