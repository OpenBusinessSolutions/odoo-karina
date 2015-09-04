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

#####
# Wizard trigers a report, that shows a list of sales order for selected date
#####


from osv import fields, osv
from tools.translate import _
import time

class sale_order_journal_wizard(osv.osv_memory):
    _name = "sale.order.journal.wizard"
    _description = "Sale Order Report"
    _columns = {
        'date': fields.date('Sale Order Date'),
        'sort': fields.selection([('name','Product'), ('qty','Quantity')], 'Sort', required=True)
    }
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        'sort': 'name'
    }
        
    def execute(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        order_date = self.browse(cr,uid,ids)[0].date
        order_sort = self.browse(cr,uid,ids)[0].sort
        
        sale_order_obj = self.pool.get('sale.order.line')
        if order_sort == 'name':
            sale_order_ids = sale_order_obj.search(cr, uid, [('order_id.date_order', '=', order_date),
                                                             ('order_id.shop_id', '=', 1)
                                                             ], order='name')
        else:
            sale_order_ids = sale_order_obj.search(cr, uid, [('order_id.date_order', '=', order_date),
                                                             ('order_id.shop_id', '=', 1)
                                                             ], order='product_uom_qty')
            
            
        group = {}
        for line in sale_order_obj.browse(cr, uid, sale_order_ids):
            if line.product_id.id in group:
                tmp = group[line.product_id.id]
                tmp['qty'] = tmp['qty'] + line.product_uom_qty
                group[line.product_id.id] = tmp
                
            else:
                group[line.product_id.id] = {'name':line.name, 'qty':line.product_uom_qty}
        
#        group_sorted = {}
#        num = 1        
#        for s in sorted(group.iteritems(), key=lambda (x, y): y[order_sort]):
#            group_sorted[num] = s[1]
#            num = num + 1

        #LIST
        sorted_list = sorted(group.iteritems(), key=lambda (x, y): y[order_sort])
        
        data = {'form':sorted_list, 'date':order_date}
        
        return {'type': 'ir.actions.report.xml', 'report_name': 'report.sale.order.journal', 'datas': data}
    
sale_order_journal_wizard()

