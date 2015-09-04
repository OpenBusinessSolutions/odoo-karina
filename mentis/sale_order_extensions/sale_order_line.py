# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP s.a. (<http://www.openerp.com>).
#    Copyright (C) 2013-TODAY Mentis d.o.o. (<http://www.mentis.si/openerp>)
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
import decimal_precision as dp

class sale_order_line(osv.Model):
    _inherit = 'sale.order.line'

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty, uom, qty_uos, uos, name, partner_id,
            lang, update_tax, date_order, packaging, fiscal_position, flag, context)
        if res and product and 'value' in res:
            result = res['value']
            if partner_id and product:
                _partner_id = self.pool.get('res.partner').browse(cr, uid, partner_id, None)
                _product_id = self.pool.get('product.product').browse(cr, uid, product, None)
            if _product_id and _product_id.sale_enabled \
               and _partner_id and _partner_id.sale_prices:
                result['price_unit'] = _product_id.sale_price
            res['value'] = result
        return res

    _columns = {
        'product_qty_returned': fields.float('Quantity Returned', digits_compute=dp.get_precision('Product Unit of Measure'), ),
    }
    _defaults = {
        'product_qty_returned': 0.0,
    }
