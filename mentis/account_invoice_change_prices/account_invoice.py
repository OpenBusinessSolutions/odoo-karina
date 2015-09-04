# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP s.a. (<http://www.openerp.com>).
#    Copyright (C) 2013 Mentis d.o.o. (<http://www.mentis.si/openerp>)
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

class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    def action_check_prices(self, cr, uid, ids, context=None):
        _sale_orders = self.pool.get('sale.order').search(cr, uid, [('invoice_ids','=',ids[0])])
        
        if len(_sale_orders) == 0:
            _change = False
            for _invoice in self.browse(cr, uid, ids, context):
                _partner = _invoice.partner_id
                _pricelist = _partner.property_product_pricelist and _partner.property_product_pricelist.id or False
                if _pricelist:
                    for _line in _invoice.invoice_line:
                        _price = self.pool.get('product.pricelist').price_get(cr, uid, [_pricelist],
                                 _line.product_id.id, _line.quantity or 1.0, _partner.id, {
                                     'uom': _line.uos_id.id or result.get('product_uos'),
                                     'date': _invoice.date_invoice,
                                     })[_pricelist]
                        if _price and _price != _line.price_unit:
                            _change = True
                            _line.write({'price_unit': _price,
                                         'price_subtotal': False})
            if _change:
                self.button_reset_taxes(cr, uid, ids, context)
        return True
