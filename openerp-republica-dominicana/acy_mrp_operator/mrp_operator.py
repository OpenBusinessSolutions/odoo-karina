# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Acysos S.L. (http://acysos.com) All Rights Reserved.
#                       Ignacio Ibeas <ignacio@acysos.com>
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
import decimal_precision as dp
import time
from datetime import datetime, timedelta, date
from dateutil import parser
from dateutil import rrule

class mrp_operator_registry(osv.osv):
	_description = 'MRP Operator Registry'
	_name = 'mrp.operator.registry'

	
	def onchange_employee(self, cr, uid, ids, operator_id, context=None):
		"""
			Checks if chosen employee has an associated product...
		"""
		if operator_id:
			chosen_employee = self.pool.get('hr.employee').browse(cr, uid, operator_id)
			if not chosen_employee.product_id:
				raise osv.except_osv(_('Warning!'), _('There is no product defined for this employee. Please, define one before continuing...'))
			
		return operator_id
        
	def _get_user(self, cr, uid, context=None):
		
		res={}
		return self.pool.get('res.users').browse(cr, uid, uid).name
	
	
	_columns = {
		'name': fields.char('Reference', size=64, required=True, states={'draft':[('readonly',False)]}, readonly=True),
		'username': fields.char('Username', size=64, required=True, readonly=True),
		'date': fields.date('Date', required=True, select=True, states={'draft':[('readonly',False)]}, readonly=True),
		'operator_id': fields.many2one('hr.employee', 'Operator', required=True, states={'draft':[('readonly',False)]}, readonly=True),
		'workcenter_lines': fields.one2many('mrp.workcenter.registry', 'operator_registry_id', 'MRP Workcenter Registry', states={'draft':[('readonly',False)]}, readonly=True),
		'state': fields.selection([('draft','Draft'),('confirmed','Confirmed'),('cancel','Cancelled')],'State', readonly=True),
		#'hour_turn': fields.float('Horas Turno', required=True),		
	}
	
	_defaults = {
		'name': lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'operator_registry'),
		'date': lambda *a: time.strftime('%Y-%m-%d'),
		'state': lambda *a: 'draft',
		'username': lambda self, cr, uid, context: self._get_user(cr, uid, context),
		#'hour_turn': lambda *a: ''
	}
	
	def action_explode(self, cr, uid, moves, context=None):
		return order_registry
	
	def action_confirm(self, cr, uid, ids, context=None):
		"""
		res = {}
		registry = self.browse(cr,uid,ids,context)[0]
		for workcenter_line in registry.workcenter_lines:
			if workcenter_line.production_id.id:
				sql = "SELECT MAX(sequence) FROM mrp_production_workcenter_line WHERE production_id = %s" % (workcenter_line.production_id.id)
				cr.execute(sql)
				sequence = cr.fetchone()[0]
				prod_obj = self.pool.get('mrp.production')
				stock_obj = self.pool.get('stock.move')
				#prod_obj.action_in_production(cr,uid,workcenter_line.production_id.id)
				if sequence == workcenter_line.workcenter_line_id.sequence:
					if workcenter_line.go_product_qty > workcenter_line.qty: 
						qty = workcenter_line.qty
						res['warning'] = {'title': _('Warning'), 'message': _('La Orden de Produccion ha sido procesada por un total de %s, pero realmente se ha producido un total de %s') % (workcenter_line.qty, workcenter_line.go_product_qty)}
					
						prod_obj.action_produce(cr, uid,workcenter_line.production_id.id,workcenter_line.go_product_qty,'consume_produce',context)
							
				for workcenter_line2 in registry.workcenter_lines:
					if workcenter_line.production_id.id == workcenter_line2.production_id.id:
						if workcenter_line2.workcenter_line_id.sequence <= workcenter_line.workcenter_line_id.sequence:
							if workcenter_line.de_product_qty > workcenter_line.qty:
								res['warning'] = {'title': _('Warning'), 'message': _('La Orden de Produccion ha sido procesada por un total de %s, pero realmente se ha producido un total de %s') % (workcenter_line.qty, workcenter_line.go_product_qty)}
								#mrp_routing_ids = self.pool.get('mrp.routing.workcenter').search(cr,uid,[('routing_id','=',workcenter_line2.production_id.routing_id.id)], order='sequence', context=context)
								#for mrp_routing_id in mrp_routing_ids:
									#product_line_id = self.pool.get('mrp.production.product.line').search(cr, uid, [('production_id','=',workcenter_line2.production_id.id),('consumed_on','=',mrp_routing_id)], context=context)
									#print product_line_id
									#if len(product_line_id) == 1:
										#break
								mrp_routing_id = self.pool.get('mrp.routing.workcenter').search(cr,uid,[('routing_id','=',workcenter_line2.production_id.routing_id.id),('workcenter_id','=',workcenter_line2.workcenter_id.id)], context=context)
								
								product_line_id = self.pool.get('mrp.production.product.line').search(cr, uid, [('production_id','=',workcenter_line2.production_id.id),('consumed_on','=',mrp_routing_id[0])], context=context)
								
								if len(product_line_id) > 0:
									product_line = self.pool.get('mrp.production.product.line').browse(cr, uid, product_line_id, context)[0]
									
									move_name = 'PROD:'+workcenter_line2.production_id.name
									
									stock_move_id = stock_obj.search(cr,uid,[('product_id','=',product_line.product_id.id),('state','=','assigned'),('name','=',move_name)],context=context)
		
									bom_id = self.pool.get('mrp.bom').search(cr, uid, [('bom_id','=',workcenter_line2.production_id.bom_id.id),('product_id','=',product_line.product_id.id),('consumed_on','=',mrp_routing_id[0])], context=context)
									bom = self.pool.get('mrp.bom').browse(cr, uid, bom_id, context)[0]
									defective_qty = bom.product_qty*bom.product_efficiency*workcenter_line.de_product_qty
									context = {'operator_registry':1,'location_src':workcenter_line2.production_id.location_src_id.id}
									stock_obj.action_scrap(cr, uid,stock_move_id,defective_qty,4,context)
		"""	
		self.write(cr, uid, ids, {'state': 'confirmed'})
		"""
		todo = []
		for order in self.browse(cr, uid, ids, context=context):
			for o in order.workcenter_lines:
				if o.state =='draft':
					todo.append(o.id)
		
		todo = self.action_explode(cr, uid, todo, context)	
		if len(todo):
			self.pool.get('mrp.workcenter.registry').action_confirm(cr, uid, todo, context=context)
		"""		
		return True
		#return result
	
	def action_cancel(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'cancel'})
		return True
	
	def action_cancel_draft(self, cr, uid, ids, context=None):
		self.write(cr, uid, ids, {'state': 'draft'})
		return True
		
mrp_operator_registry()

class mrp_production_workcenter_line(osv.osv):
		_inherit = 'mrp.production.workcenter.line'
		
		def _number_get(self,cr,uid,ids,name,arg,context={}):
			res={}
			for line in self.browse(cr,uid,ids,context):
				res[line.id] = line.production_id.name +'-'+ str(line.sequence)
			return res
		
		_columns = {
			'number': fields.function(_number_get, method=True, store=True, type='char', size=64, string='Number', readonly=True),
		}
		
		_rec_name = "number"
		
		
mrp_production_workcenter_line()

class mrp_workcenter_registry_key(osv.osv):
		_name = 'mrp.workcenter.registry.key'
		_description = 'MRP Workcenter Registry Key'
		_columns = {
			'name': fields.char('Name', required=True, size=46, translate=True),
		}
		
mrp_workcenter_registry_key()

class mrp_workcenter_registry(osv.osv):
		_description = 'MRP Workcenter Registry'
		_name = 'mrp.workcenter.registry'
		
		'''
		def onchange_operator_dates(self, cr, uid, ids, date_start, date_stop, context=None):
			"""
				Returns duration and/or end date based on values passed
			"""
			if context is None:
				context = {}
			value = {}
			
			if not date_start:
				return value

			start = datetime.strptime(date_start, "%Y-%m-%d %H:%M:%S")
			end = datetime.strptime(date_stop, "%Y-%m-%d %H:%M:%S")
			
			if start > end:
				raise osv.except_osv(_('Warning!'), _('La fecha de inicio no puede ser mayor que la fecha final. Por favor corrija esto antes de continuar...'))
			
			diff = end - start
			duration = float(diff.days)* 24 + (float(diff.seconds) / 3600)
			value['operator_duration'] = round(duration, 2)

			return {'value': value}
		'''
		def _get_operation_duration(self, cr, uid, ids, field_name, arg, context=None):
		  if context is None:
		    context = {}
		  value = {}
		  
		  for workcenter_registry in self.browse(cr, uid, ids):
			start = datetime.strptime(workcenter_registry.date_start, "%Y-%m-%d %H:%M:%S")
			end = datetime.strptime(workcenter_registry.date_stop, "%Y-%m-%d %H:%M:%S")
			if start > end:
			  raise osv.except_osv(_('Warning!'), _('La fecha de inicio no puede ser mayor que la fecha final. Por favor corrija esto antes de continuar...'))
			diff = end - start
			duration = float(diff.days)* 24 + (float(diff.seconds) / 3600)
			if duration > 12:
			  raise osv.except_osv(_('Warning!'), _('La duracion no puede exceder las 12 horas. Por favor corrija esto antes de continuar...'))
			if duration == 0:
			  raise osv.except_osv(_('Warning!'), _('La duracion no puede ser igual a 0 horas. Por favor corrija esto antes de continuar...'))
			value[workcenter_registry.id] = round(duration, 2)
			return value
		
		def _get_expected_net_weight(self, cr, uid, ids, field_name, arg, context=None):
			if context is None:
				context = {}
			res = {}
			for workcenter_registry in self.browse(cr, uid, ids):
				if workcenter_registry.go_product_qty == 0:
					raise osv.except_osv(_('Invalid action !'), _('El valor del campo "Producto Bueno" no puede ser igual o menor de 0 (cero).'))
				
				res[workcenter_registry.id] = (workcenter_registry.go_product_qty * workcenter_registry.product_id.weight_net)
				
			return res
		"""
		def _get_percent(self, cr, uid, ids, field_name, arg, context=None):
			if context is None:
				context = {}
			res = {}
			for workcenter_registry in self.browse(cr, uid, ids):
				res[workcenter_registry.id] = 100-((workcenter_registry.real_net_weight / workcenter_registry.exp_net_weight) * 100)
				
			return res
		"""
		def _get_products_done(self, cr, uid, ids, name,  arg, context={}):
			res = {}		
			for item in self.browse(cr, uid, ids):
				res[item.id] = item.production_id.products_done_store		
			return res		
		
		def _production_state(self, cr, uid, ids, name, arg, context={}):
					
			res = {}
			for line in self.browse(cr, uid, ids):
				res[line.id] = line.production_id.state
			return res
		
		_columns = {
			'key': fields.many2one('mrp.workcenter.registry.key','Key'),
			'workcenter_line_id': fields.many2one('mrp.production.workcenter.line', 'Workcenter'),
			'product_id': fields.many2one('product.product', 'Product'),
			'name': fields.char('Operation Code', size=64, required=True),
			'workcenter_id': fields.many2one('mrp.workcenter', 'Resource'),
			'de_product_qty': fields.float('Defective Product Qty'),
			'go_product_qty': fields.float('Good Product Qty'),
			#'real_net_weight': fields.float('Real Net Weight'),
			#'exp_net_weight': fields.function(_get_expected_net_weight,
			#		method=True,
			#		string='Exp. Net Weight',
			#		store=True,
			#		type='float',
			#		readonly=False,
			#		help="TODO"),
			#'dif_percent': fields.function(_get_percent,
			#		method=True,
			#		string='Diferencia',
			#		store=False,
			#		type='float',
			#		readonly=False,
			#		help="TODO"),
			#'date_start': fields.datetime('Date and Time start'),
			#'time_start': fields.datetime('Time start'),
			#'date_stop': fields.datetime('Date and Time stop'),
			#'operator_duration': fields.float('Duration', digits_compute=dp.get_precision('Account')),
			#'operator_duration': fields.function(_get_operation_duration,
			#		method=True,
			#		string='Duration',
			#		store=True,
			#		type='float',
			#		readonly=False,
			#		help="TODO"),
			#'time_stop': fields.time('Time stop'),
			'note': fields.text('Notes'),
			'operator_registry_id': fields.many2one('mrp.operator.registry', 'Operator registry', ondelete='cascade'),
			'production_id': fields.many2one('mrp.production', 'Manufacturing Order', ondelete='set null'),
			'products_done': fields.function(_get_products_done, method=True, type='float', string='Producto realizado' ), 
			'mrp_order_state': fields.function(_production_state, method=True, type='char', string='Estado OP', readonly=True), 
			'operator_id': fields.related('operator_registry_id', 'operator_id', type='many2one', relation='hr.employee', string='Operator'),
			#'machines': fields.selection((('1','1'),
			#							 ('2','2'),
			#							 ('3','3'),
			#							 ('4','4'),
			#							 ('5','5'),
			#							 ('6','6')), 'Maquinas', required=True),
			'qty': fields.float('Order Qty'),
			'move_done': fields.boolean("Move Done"),
			'state': fields.selection([
				('draft', 'New'),
				('confirmed', 'Confirmed'),
				('cancel', 'Cancelled'),
				], 'State', readonly=True, select=True)
		}

	  
		_defaults = {
			'name':'/',
			#'date_start': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
			#'date_stop': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
			#'machines': lambda *a: 1,
			'move_done': lambda *a: False,
			'state':  lambda *a: 'draft',
		}
		
		def workcenter_line_change(self, cr, uid, ids,workcenter_line_id,context={}):
			if (workcenter_line_id):
				workcenter_line = self.pool.get('mrp.production.workcenter.line').browse(cr, uid, [workcenter_line_id], context)[0]
				return {'value': {'workcenter_line_id': workcenter_line.id,
				'product_id':workcenter_line.production_id.product_id.id,
				'name':workcenter_line.name,
				'workcenter_id':workcenter_line.workcenter_id.id,
				'production_id':workcenter_line.production_id.id,
				'qty': workcenter_line.qty}}

		def action_confirm_line(self, cr, uid, ids, context=None):
			res = {}
			registry = self.browse(cr,uid,ids,context)[0]
			registry2 = self.browse(cr,uid,ids,context)[0]
			
			if registry.move_done == True:
				self.write(cr, uid, ids, {'state': 'confirmed'})
							
				return True
			
			if registry.production_id.id:
				sql = "SELECT MAX(sequence) FROM mrp_production_workcenter_line WHERE production_id = %s" % (registry.production_id.id)
				cr.execute(sql)
				sequence = cr.fetchone()[0]

				prod_obj = self.pool.get('mrp.production')
				stock_obj = self.pool.get('stock.move')
				#prod_obj.action_in_production(cr,uid,workcenter_line.production_id.id)
				if sequence == registry.workcenter_line_id.sequence:
					if registry.go_product_qty > 0: 
						qty = registry.qty
						res['warning'] = {'title': _('Warning'), 'message': _('La Orden de Produccion ha sido procesada por un total de %s, pero realmente se ha producido un total de %s') % (registry.qty, registry.go_product_qty)}
					
						prod_obj.action_produce(cr, uid,registry.production_id.id,registry.go_product_qty,'consume_produce',context)
							
				
					if registry.production_id.id == registry2.production_id.id:
						if registry2.workcenter_line_id.sequence <= registry.workcenter_line_id.sequence:
							if registry.de_product_qty > registry.qty:
								res['warning'] = {'title': _('Warning'), 'message': _('La Orden de Produccion ha sido procesada por un total de %s, pero realmente se ha producido un total de %s') % (registry.qty, registry.go_product_qty)}
								#mrp_routing_ids = self.pool.get('mrp.routing.workcenter').search(cr,uid,[('routing_id','=',workcenter_line2.production_id.routing_id.id)], order='sequence', context=context)
								#for mrp_routing_id in mrp_routing_ids:
									#product_line_id = self.pool.get('mrp.production.product.line').search(cr, uid, [('production_id','=',workcenter_line2.production_id.id),('consumed_on','=',mrp_routing_id)], context=context)
									#print product_line_id
									#if len(product_line_id) == 1:
										#break
								mrp_routing_id = self.pool.get('mrp.routing.workcenter').search(cr,uid,[('routing_id','=',registry2.production_id.routing_id.id),('workcenter_id','=',registry2.workcenter_id.id)], context=context)
								
								product_line_id = self.pool.get('mrp.production.product.line').search(cr, uid, [('production_id','=',registry2.production_id.id),('consumed_on','=',mrp_routing_id[0])], context=context)
								
								if len(product_line_id) > 0:
									product_line = self.pool.get('mrp.production.product.line').browse(cr, uid, product_line_id, context)[0]
									
									move_name = 'PROD:'+registry2.production_id.name
									
									stock_move_id = stock_obj.search(cr,uid,[('product_id','=',product_line.product_id.id),('state','=','assigned'),('name','=',move_name)],context=context)
		
									bom_id = self.pool.get('mrp.bom').search(cr, uid, [('bom_id','=',registry2.production_id.bom_id.id),('product_id','=',product_line.product_id.id),('consumed_on','=',mrp_routing_id[0])], context=context)
									bom = self.pool.get('mrp.bom').browse(cr, uid, bom_id, context)[0]
									defective_qty = bom.product_qty*bom.product_efficiency*registry.de_product_qty
									context = {'operator_registry':1,'location_src':registry2.production_id.location_src_id.id}
									stock_obj.action_scrap(cr, uid,stock_move_id,defective_qty,4,context)
				
			self.write(cr, uid, ids, {'state': 'confirmed',
										'move_done': True})
							
			return True

		def action_cancel_draft(self, cr, uid, ids, context=None):
			self.write(cr, uid, ids, {'state': 'draft'})
			return True

#		def action_confirm(self, cr, uid, ids, context=None):
#			order_registry = self.browse(cr, uid, ids, context=context)
#			self.write(cr, uid, ids, {'state':'confirmed'})
#			return []

mrp_workcenter_registry()

class mrp_production(osv.osv):
	
	def onchange_prod_dates(self, cr, uid, ids, begin_production_date_1, end_production_date_1, production_duration_1, context=None):
		"""
			Returns duration and/or end date based on values passed
		"""
		if context is None:
			context = {}
		value = {}
		if not begin_production_date_1:
			return value
		if not end_production_date_1 and not production_duration_1:
			duration = 1.00
			value[production_duration_1] = duration

		start = datetime.strptime(begin_production_date_1, "%Y-%m-%d %H:%M:%S")
		if end_production_date_1 and not production_duration_1:
			end = datetime.strptime(end_production_date_1, "%Y-%m-%d %H:%M:%S")
			diff = end - start
			duration = float(diff.days)* 24 + (float(diff.seconds) / 3600)
			value[production_duration_1] = round(duration, 2)
		elif not end_production_date_1:
			end = start + timedelta(hours=production_duration_1)
			value[end_production_date_1] = end.strftime("%Y-%m-%d %H:%M:%S")
		elif end_production_date_1 and production_duration_1:
			# we have both, keep them synchronized:
			# set duration based on end_date (arbitrary decision: this avoid
			# getting dates like 06:31:48 instead of 06:32:00)
			end = datetime.strptime(end_production_date_1, "%Y-%m-%d %H:%M:%S")
			diff = end - start
			duration = float(diff.days)* 24 + (float(diff.seconds) / 3600)
			value['production_duration_1'] = round(duration, 2)

		return {'value': value}

	_inherit = 'mrp.production'
	_columns = {
		'begin_production_date_1': fields.datetime('Begin production date', required=True),
		'end_production_date_1': fields.datetime('End production date', required=True),
		'production_duration_1': fields.float('Duration', digits_compute=dp.get_precision('Account')),
		'operator_ids': fields.one2many('mrp.workcenter.registry', 'production_id', 'Operator Registry'),
		#'production_manpower': fields.one2many('mrp.production.manpower', 'production_id', 'Production manpower', required=True),
		'products_total_cost_1': fields.float('Material total cost', digits_compute=dp.get_precision('Account'), readonly=True),
		#'unit_product_cost': fields.float('Material unit cost', digits_compute=dp.get_precision('Account'), readonly=True),
		'manpower_cost_1': fields.float('Manpower total cost', digits_compute=dp.get_precision('Account'), readonly=True),
		#'manpower_unit_cost': fields.float('Manpower unit cost', digits_compute=dp.get_precision('Account'), readonly=True),
		'total_production_cost_1': fields.float('Total production cost', digits_compute=dp.get_precision('Account'), readonly=True),
		#'unit_production_cost': fields.float('Unit production cost', digits_compute=dp.get_precision('Account'), readonly=True),
		'total_fixed_cost_1': fields.float('Total fixed cost', digits_compute=dp.get_precision('Account'), readonly=True),
		#'unit_fixed_cost': fields.float('Unit fixed cost', digits_compute=dp.get_precision('Account'), readonly=True),
		#'new_standard_price': fields.float('New standard product price', digits_compute=dp.get_precision('Account'), readonly=True, help="New product price (only if its cost method is set to average)"),
		'unit_costs_1': fields.one2many ('mrp.production.unit.costs', 'production_id', 'Unit costs by product')
	}
	_defaults = {
		'begin_production_date_1': lambda *a: time.strftime('%Y-%m-%d 08:00:00'),
		'end_production_date_1': lambda *a: time.strftime('%Y-%m-%d 13:00:00'),
		'production_duration_1': 5.0
	}

mrp_production()

class mrp_routing_workcenter(osv.osv):
		_inherit = 'mrp.routing.workcenter'
		
		_sql_constraints = [
			('sequence_routing_uniq', 'unique (sequence,routing_id)', 'The sequence must be unique per routing !')
		]
		
mrp_routing_workcenter()
