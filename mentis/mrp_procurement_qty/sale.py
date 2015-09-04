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

#class sale_order(osv.osv):
#    _inherit = "sale.order"
#    _columns = {
#        'delivery_order_ref_ids': fields.many2one('stock.picking.out', 'Delivery Order', readonly=True),
#    }
#sale_order()

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    _columns = {
        'default_code': fields.related('product_id', 'default_code', type='char', readonly=True, string='Koda', store=True),
    }
sale_order_line()

