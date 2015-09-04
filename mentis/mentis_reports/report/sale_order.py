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
from openerp.report import report_sxw

class order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context=None):
        super(order, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_total_discount': self._get_total_discount,
            'get_total_net': self._get_total_net,
        })
    
    def _get_total_discount(self, order):
        disc_total = 0
        for line in order.order_line:
            if line.product_uos:
                disc_tmp = line.product_uos_qty * line.price_unit * line.discount / 100
            else:
                disc_tmp = line.product_uom_qty * line.price_unit * line.discount / 100
            disc_total += disc_tmp

        return disc_total
    
    def _get_total_net(self, order):
        value_total = 0
        for line in order.order_line:
            if line.product_uos:
                value_tmp = line.product_uos_qty * line.price_unit
            else:
                value_tmp = line.product_uom_qty * line.price_unit
            value_total += value_tmp
            
        return value_total

report_sxw.report_sxw('report.sale.order.mentis', 'sale.order', 'mentis_reports/report/sale_order.rml', parser=order, header="external")
