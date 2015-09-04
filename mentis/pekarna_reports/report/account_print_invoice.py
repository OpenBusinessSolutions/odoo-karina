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

class account_invoice(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_invoice, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_total_discount': self._get_total_discount,
            'get_total_net': self._get_total_net,
        })
        
    def _get_total_discount(self, invoice):
        disc_total = 0
        for line in invoice.invoice_line:
            disc_total += line.quantity * line.price_unit * line.discount / 100
        return disc_total
    
    def _get_total_net(self, invoice):
        value_total = 0
        tax_obj = self.pool.get('account.tax')
        
        for line2 in invoice.invoice_line:
            value_total += tax_obj.compute_all(self.cr, self.uid, line2.invoice_line_tax_id, line2.price_unit, line2.quantity, product=line2.product_id, partner=line2.invoice_id.partner_id)['total']
        
#        for line in invoice.invoice_line:
#            value_total += line.quantity * line.price_unit

        return value_total

report_sxw.report_sxw('report.account.invoice.pekarna', 'account.invoice', 'pekarna_reports/report/account_print_invoice.rml', parser=account_invoice)
