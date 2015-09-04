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

class sale_order(osv.osv):
    _inherit = "sale.order"

    def print_quotation(self, cr, uid, ids, context=None):
        res = super(sale_order,self).print_quotation(cr, uid, ids, context)
        if res['report_name'] == 'sale.order':
            res['report_name'] = 'sale.order.mentis'
        return res
    
sale_order()

class account_invoice(osv.osv):
    _inherit = "account.invoice"

    def invoice_print(self, cr, uid, ids, context=None):
        res = super(account_invoice,self).invoice_print(cr, uid, ids, context)
        if res['report_name'] == 'account.invoice':
            res['report_name'] = 'account.invoice.mentis'
        return res
    
account_invoice()

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    _columns = {
        'create_uid': fields.many2one('res.users', 'User', readonly=1),
    }
    
stock_picking()
