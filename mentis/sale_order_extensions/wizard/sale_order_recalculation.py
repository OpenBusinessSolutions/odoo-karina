# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP s.a. (<http://www.openerp.com>)
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
import openerp.addons.decimal_precision as dp

class sale_order_recalculation(osv.TransientModel):
    _name="sale.order.recalculation"
    _description="Recalculate Sale Prices"

    def _do_recalculation(self, cr, uid, ids, context=None):
        if ids and len(ids) > 0:
            _dp_digits = self.pool.get('decimal.precision').precision_get(cr, uid, 'Product Price')
            _sale_orders = self.pool.get('sale.order').browse(cr, uid, ids, context)
            for _sale_order in _sale_orders:
                for _sale_order_line in _sale_order.order_line:
                    _price = 0.0
                    if _sale_order_line.product_id and _sale_order_line.product_id.sale_enabled \
                       and _sale_order.partner_id and _sale_order.partner_id.sale_prices:
                        _price = _sale_order_line.product_id.sale_price
                    elif _sale_order_line.product_id:
                        _price = self.pool.get('product.pricelist').price_get(cr, uid, [_sale_order.pricelist_id.id],
                                                                              _sale_order_line.product_id.id,
                                                                              _sale_order_line.product_uom_qty or 1.0,
                                                                              _sale_order.partner_id.id,
                                                                              {'uom': _sale_order_line.product_uom.id or result.get('uom'),
                                                                               'date': _sale_order.date_order}
                                                                              )[_sale_order.pricelist_id.id] or 0.0
                    else:
                        _price = False

                    if _price and _price != 0.0 and round(_price, _dp_digits) != round(_sale_order_line.price_unit, _dp_digits):
                        _sale_order_line.write({'price_unit': round(_price, _dp_digits),
                                                'price_subtotal': False})

        return True
    
    def execute(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        _active_ids = context.get('active_ids', False)
        if _active_ids:
            self._do_recalculation(cr, uid, _active_ids, context)
        
        return {'type': 'ir.actions.act_window_close'}
