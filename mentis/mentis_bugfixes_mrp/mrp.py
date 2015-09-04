# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Mentis d.o.o. All rights reserved.
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

import string
from osv import fields, osv
from tools.translate import _
from openerp import tools

"""
	- fix function _bom_explode by deviding factor by "newbom_pool.product_qty"
"""

def rounding(f, r):
	import math
	if not r:
		return f
	return math.ceil(f / r) * r

class mrp_bom(osv.osv):
	_inherit = "mrp.bom"
	
	def _bom_explode(self, cr, uid, bom, factor, properties=None, addthis=False, level=0, routing_id=False):
		""" Finds Products and Work Centers for related BoM for manufacturing order.
		@param bom: BoM of particular product.
		@param factor: Factor of product UoM.
		@param properties: A List of properties Ids.
		@param addthis: If BoM found then True else False.
		@param level: Depth level to find BoM lines starts from 10.
		@return: result: List of dictionaries containing product details.
				 result2: List of dictionaries containing Work Center details.
		"""
		routing_obj = self.pool.get('mrp.routing')
		factor = factor / (bom.product_efficiency or 1.0)
		factor = rounding(factor, bom.product_rounding)
		if factor < bom.product_rounding:
			factor = bom.product_rounding
		result = []
		result2 = []
		phantom = False
		if bom.type == 'phantom' and not bom.bom_lines:
			newbom = self._bom_find(cr, uid, bom.product_id.id, bom.product_uom.id, properties)

			if newbom:
				#res = self._bom_explode(cr, uid, self.browse(cr, uid, [newbom])[0], factor*bom.product_qty, properties, addthis=True, level=level+10)
				
				newbom_pool=self.browse(cr,uid,newbom)
				res = self._bom_explode(cr, uid, self.browse(cr, uid, [newbom])[0], factor*bom.product_qty/newbom_pool.product_qty, properties, addthis=True, level=level+10)
				
				result = result + res[0]
				result2 = result2 + res[1]
				phantom = True
			else:
				phantom = False
		if not phantom:
			if addthis and not bom.bom_lines:
				result.append(
				{
					'name': bom.product_id.name,
					'product_id': bom.product_id.id,
					'product_qty': bom.product_qty * factor,
					'product_uom': bom.product_uom.id,
					'product_uos_qty': bom.product_uos and bom.product_uos_qty * factor or False,
					'product_uos': bom.product_uos and bom.product_uos.id or False,
				})
			routing = (routing_id and routing_obj.browse(cr, uid, routing_id)) or bom.routing_id or False
			if routing:
				for wc_use in routing.workcenter_lines:
					wc = wc_use.workcenter_id
					d, m = divmod(factor, wc_use.workcenter_id.capacity_per_cycle)
					mult = (d + (m and 1.0 or 0.0))
					cycle = mult * wc_use.cycle_nbr
					result2.append({
						'name': tools.ustr(wc_use.name) + ' - '  + tools.ustr(bom.product_id.name),
						'workcenter_id': wc.id,
						'sequence': level+(wc_use.sequence or 0),
						'cycle': cycle,
						'hour': float(wc_use.hour_nbr*mult + ((wc.time_start or 0.0)+(wc.time_stop or 0.0)+cycle*(wc.time_cycle or 0.0)) * (wc.time_efficiency or 1.0)),
					})
			for bom2 in bom.bom_lines:
				res = self._bom_explode(cr, uid, bom2, factor, properties, addthis=True, level=level+10)
				result = result + res[0]
				result2 = result2 + res[1]
		return result, result2
	
mrp_bom()
