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

from openerp.osv import fields, osv
from openerp.tools import float_compare
from openerp import netsvc
from openerp.tools.translate import _

class procurement_order(osv.osv):
    _inherit = 'procurement.order'
    
    def _get_short_message(self, cr, uid, ids, field_name, arg=None, context=None):
        res={}
        for order in self.browse(cr, uid, ids, context=context):
            if order.state == 'exception':
                index = order.message.rfind(':')
                if index != -1:
                    res[order.id] = order.message[index+2:]
                else:
                    res[order.id] = order.message
            else:
                res[order.id] = order.message
        
        return res
        
        
    _columns = {
        'message': fields.char('Latest error', help="Exception occurred while computing procurement orders."),
		'supply_method': fields.related('product_id', 'supply_method', type='char', store=True, string='Supply Method'),
        'short_message': fields.function(_get_short_message, type='char', store=True, string='Error Message'),
	}
    
    def check_bom_exists(self, cr, uid, ids, context=None):
        """ Override existing function and write the same message to field: short_message
        """
        res = super(procurement_order, self).check_bom_exists(cr, uid, ids, context=context)
        if res == False:
            for procurement in self.browse(cr, uid, ids, context=context):
                cr.execute('update procurement_order set short_message=%s where id=%s', (_('No BoM defined for this product !'), procurement.id))
        return res
    
    def check_supplier_info(self, cr, uid, ids, context=None):
        """ Override existing function and write message to field: short_message
        """
        res = super(procurement_order, self).check_supplier_info(cr, uid, ids, context=context)
        if res == False:
            for procurement in self.browse(cr, uid, ids, context=context):
                cr.execute('update procurement_order set short_message=message where id=%s', (procurement.id,))
        return res

procurement_order()

class procurement_order_journal(osv.osv):
    _name = 'procurement.order.journal'
    _columns = {
        'date_start': fields.date('Start Date'),
        'date_end': fields.date('Start Date'),
        'state': fields.boolean('Active'),
    }
    
procurement_order_journal()
