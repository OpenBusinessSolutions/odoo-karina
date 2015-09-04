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
import openerp.addons.decimal_precision as dp

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    _columns = {
        'address_shipping_id': fields.many2one('res.partner', 'Shipping Address', readonly=True, states={'draft':[('readonly',False)]}),
        'decade_date': fields.char('Decade Date', size=24, readonly=True),
        'delivery_order_origin': fields.text('Delivery Orders', readonly=True),
    }

account_invoice()

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    _columns = {
        'product_qty_returned': fields.float('Quantity Returned', digits_compute=dp.get_precision('Purchase Price'), readonly=True),
    }
    _order = 'invoice_id desc, sequence'
    _defaults = {
        'product_qty_returned': 0.0,
        'sequence': 10,
    }

account_invoice_line()
