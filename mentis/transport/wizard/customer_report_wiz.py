# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from osv import osv, fields
from tools.translate import _


class po_customer(osv.osv_memory):
    _name = 'purchase.customer.wizard'
    _description = 'Purchase customer wizard report'


    def print_report(self, cr, uid, ids, context=None):
        
        if context is None:
            context = {}
            
        active_ids = context.get('active_ids', [])
        list_lines = []
        
        orders_line_ids = self.pool.get('purchase.order.line').search(cr, uid, [('order_id', 'in', active_ids)]) #dobimo vse ID-linije za izbrane purchase orderje
        orders = self.pool.get('purchase.order.line').browse(cr, uid, orders_line_ids, context=None) #dobimo vse linije z izbranim PO-jem
        for lines in orders:
            dict_lines = {'customer_id': lines.customer_id.id, 'transport_id': lines.order_id.transport_id.id, 'ids':active_ids} #zelimo dobiti DISTINCT stranke za izbrani PO
            if not dict_lines in list_lines:
                list_lines.append(dict_lines)
        
        datas = {}
        datas['ids'] = context.get('active_ids', [])
        
#        list= [
#               {'customer_id': 3, 'transport_id': 6}, 
#               {'customer_id': 6, 'transport_id': 6}
#              ]
        
        
        datas['form'] = list_lines
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'customer.order',
            'datas': datas,
       }
po_customer()

