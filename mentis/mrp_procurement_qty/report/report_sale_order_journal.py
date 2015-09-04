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

import time
from report import report_sxw
from osv import osv
import pooler

class report_sale_order_journal(report_sxw.rml_parse):
    _name = 'report.sale.order.journal'
    def __init__(self, cr, uid, name, context):
        super(report_sale_order_journal, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
                        'time': time,
#                        'get_lines': self._get_lines,
                        })
    
#    def _get_lines(self, data):
#        
#        customer_id = data['customer_id']
#        transport_id = data['transport_id']
#        order_ids = data['ids']
#        
#        pool = pooler.get_pool(self.cr.dbname)
#        line_ids = self.pool.get('purchase.order.line').search(self.cr, self.uid, 
#                                                                [('customer_id', '=', customer_id),
#                                                                 ('order_id.transport_id', '=', transport_id),
#                                                                 ('order_id', 'in', order_ids)
#                                                                ])
#        line_obj = self.pool.get('purchase.order.line').browse(self.cr, self.uid, line_ids)
#        
#        return line_obj
    
report_sxw.report_sxw('report.report.sale.order.journal','sale.order','addons/mrp_procurement_qty/report/report_sale_order_journal.rml',parser=report_sale_order_journal)
