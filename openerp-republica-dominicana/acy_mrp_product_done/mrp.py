# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Acysos S.L. (http://acysos.com) All Rights Reserved.
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

from datetime import datetime
from openerp.osv import osv, fields
from openerp.tools.translate import _
import netsvc
import time
import tools

class mrp_production(osv.osv):
    _inherit = 'mrp.production'
    
    def _get_percent(self, cr, uid, ids, field_name, arg, context=None):
			if context is None:
				context = {}
			res = {}
			for mrp_production in self.browse(cr, uid, ids):
				res[mrp_production.id] = ((mrp_production.products_done / mrp_production.product_qty) * 100)
			return res
    
    def _products_done_get(self, cr, uid, ids, name, arg, context={}):
        res = {}
        for mrp_production in self.browse(cr, uid, ids, context):
            done = 0.0
            for move in mrp_production.move_created_ids2:
		if not move.scrapped:
                   done += move.product_qty
            res[mrp_production.id] = done 
        return res
    
    _columns = {
        'products_done': fields.function(_products_done_get, method=True, type='float', string='Productos Completados', readonly=True), 
        'percent_done': fields.function(_get_percent, method=True, string='Porcentaje',	store=False, type='float', readonly=True),
	'products_done_store':fields.function(_products_done_get, method=True, type='float', visible=False, store=False, readonly=True),   
 }
    
mrp_production()
