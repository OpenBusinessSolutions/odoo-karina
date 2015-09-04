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

import time
from report import report_sxw
from osv import osv
import pooler

class order_transport(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(order_transport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
                        'time': time,
                        'get_weight': self._get_weight,
                        'get_weight_sum': self._get_weight_sum,
                        })
    
    def _get_weight(self, order):
        
        teza = 0
        for line in order.order_line:
            if line.product_uom.name == 'kg': #ce je mera kg potem sestevamo
                teza += line.product_qty
            else:
                p_uos_name = line.product_id.product_tmpl_id.uos_id.name or ''
                if p_uos_name == 'kg':
                    teza += (line.product_id.product_tmpl_id.uos_coeff * line.product_qty)
        
        return str( round(teza,2) ) + 'kg'
    
    def _get_weight_sum(self, object):
        
        teza = 0
        
        for order in object:
            for line in order.order_line:
                if line.product_uom.name == 'kg': #ce je mera kg potem sestevamo
                    teza += line.product_qty
                else:
                    p_uos_name = line.product_id.product_tmpl_id.uos_id.name or ''
                    if p_uos_name == 'kg':
                        teza += (line.product_id.product_tmpl_id.uos_coeff * line.product_qty)
            
        return str( round(teza,2) ) + 'kg'

report_sxw.report_sxw('report.transport.purchase','purchase.order','transport/report/order_report.rml',parser=order_transport)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

