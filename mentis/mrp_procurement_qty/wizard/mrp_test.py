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
from tools.translate import _
from datetime import datetime
import time
import openerp.addons.decimal_precision as dp
from openerp.tools.safe_eval import safe_eval

class mrp_test(osv.osv_memory):
    _name = "mrp.test"
    _description = "TEST"
    _columns = {
        #'product_qty': fields.float('Product Qty', digits_compute=dp.get_precision('Product Unit of Measure'), required=True),
        'date_done': fields.date('Datum dobave'),
    }
    
    _defaults = {
        #'product_qty': lambda *a: 0,
        'date_done': time.strftime('%Y-%m-%d'),
    }
    
    
    def execute(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        
        print('start')    
        move_obj = self.pool.get('stock.move')
        move_ids = move_obj.search(cr, uid, [('state', '=', 'confirmed')])
        move_obj.action_cancel(cr, uid, move_ids, context) #preklicemo se stock move
        print('konec')
        
        return {
                'type': 'ir.actions.act_window_close',
        }
        
       
mrp_test()

