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
from openerp import netsvc
from tools.translate import _
from lxml import etree

class sale_order(osv.Model):
    _inherit = 'sale.order'

    def default_get(self, cr, uid, fields_list=None, context=None):
        res = super(sale_order, self).default_get(cr, uid, fields_list, context)
        if context:
            _shop_ids = self.pool.get('sale.shop').search(cr, uid, [('shop_production', '=', context.get('shop_production', False))], limit=1, order='id')
            if len(_shop_ids) > 0:
                res['shop_id'] = _shop_ids[0]
            else:
                res['shop_id'] = False
        return res

    def copy_data(self, cr, uid, id, default=None, context=None):
        _data = super(sale_order, self).copy_data(cr, uid, id, default, context=context)
        
        _user = self.pool.get('res.users').browse(cr, uid, uid)
        _date_order = self.pool.get('ir.values').get_default(cr, uid, 'sale.order', 'date_order', False, _user.company_id.id, False)
        
        _order_lines = _data.get('order_line')
        _order_lines = [x for x in _order_lines if not x[2]['product_id'] == False]
        
        for _order_line in _order_lines:
            _order_line[2]['product_qty_returned'] = 0
            if _date_order:
                _data.update({'date_order': _date_order})
                _price = self._get_line_price(cr, uid, _data['partner_id'], _data['pricelist_id'], _data['date_order'],
                                                       _order_line[2]['product_id'], _order_line[2]['product_uom'],
                                                       _order_line[2]['product_uom_qty'])
                _order_line[2]['price_unit'] = _price
        
        _data.update({'order_line': _order_lines})
        
        return _data
    
    _columns = {
        'state': fields.selection([
            ('draft', 'Draft Quotation'),
            ('prepared', 'Prepared for Confirm'),
            ('sent', 'Quotation Sent'),
            ('cancel', 'Cancelled'),
            ('waiting_date', 'Waiting Schedule'),
            ('progress', 'Sales Order'),
            ('manual', 'Sale to Invoice'),
            ('shipping_except', 'Shipping Exception'),
            ('invoice_except', 'Invoice Exception'),
            ('done', 'Done'),
            ], 'Status', readonly=True,help="Gives the status of the quotation or sales order.\
              \nThe exception status is automatically set when a cancel operation occurs \
              in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
               but waiting for the scheduler to run on the order date.", select=True),
    }

    def date_order_change(self, cr, uid, ids, order_lines=False, date_order=False, pricelist=False, partner=False, fiscal_position=False, context=None):
        if context is None:
            context = {}
            
        res = {}
        
        if date_order:
            self.pool.get('ir.values').set_default(cr, uid, 'sale.order', 'date_order', date_order, False, True, False)

        _partner_id = False
        if partner:
            _partner_id = self.pool.get('res.partner').browse(cr, uid, partner, context)

        _dp = self.pool.get('decimal.precision').precision_get(cr, uid, 'Product Price')
        if not ids:
            for _line in order_lines:
                _product_id = self.pool.get('product.product').browse(cr, uid, _line[2]['product_id'], context)
                if _product_id and _product_id.sale_enabled \
                   and _partner_id and _partner_id.sale_prices:
                    _price = _product_id.sale_price
                    _line[2]['price_unit'] = round(_price, _dp)
                elif pricelist:
                    _price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                                 _line[2]['product_id'], _line[2]['product_uom_qty'] or 1.0, partner, {
                                 'uom': _line[2]['product_uom'] or result.get('product_uom'),
                                 'date': date_order,
                                 })[pricelist] or 0.0
                    _line[2]['price_unit'] = round(_price, _dp)
            return {'value':{'order_line':order_lines}}
        else:
            _lines_obj = self.pool.get('sale.order.line')
            lines = []
            for _order in self.browse(cr, uid, ids, context):
                for _line in _order.order_line:
                    if _line.product_id.sale_enabled and _partner_id.sale_prices:
                        _price = _line.product_id.sale_price
                        res = {'price_unit': round(_price, _dp),
                               'price_subtotal': False}
                        lines.append((1, _line.id, res))
                    elif pricelist:
                        _price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                                     _line.product_id.id, _line.product_uom_qty or 1.0, partner, {
                                     'uom': _line.product_uom.id or result.get('product_uom'),
                                     'date': date_order,
                                     })[pricelist] or 0.0
                        res = {'price_unit': round(_price, _dp),
                               'price_subtotal': False}
                        lines.append((1, _line.id, res))
            return {'value':{'order_line':lines}}

    def action_button_confirm_surplus(self, cr, uid, ids, context=None):
        return self.action_button_confirm(cr, uid, ids, context)
    
    def action_prepare(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        _no_price = []
        _no_quantity = []
        _no_tax = []
        
        for _order in self.browse(cr, uid, ids, context):
            for _line in _order.order_line:
                if not _line.price_unit or _line.price_unit == 0.0:
                    _no_price.append(_line.name)
                if _line.product_uom_qty == 0.0 and _line.product_qty_returned == 0.0:
                    _no_quantity.append(_line.name)
                if not _line.tax_id:
                    _no_tax.append(_line.name)

        if len(_no_price) > 0 or len(_no_quantity) > 0 or len(_no_tax) > 0:
            _text = ''
            if len(_no_price) > 0:
                _text += _('Price not set for next products:\n')
                for _line in _no_price:
                    _text += _line + '\n'
            if len(_no_quantity) > 0:
                _text += _('Quantity not set for next products:\n')
                for _line in _no_quantity:
                    _text += _line + '\n'
            if len(_no_tax) > 0:
                _text += _('Tax not set for next products:\n')
                for _line in _no_tax:
                    _text += _line + '\n'
            raise osv.except_osv(_('Error!'), (_text))
            return False
        else:
            for _order in self.browse(cr, uid, ids, context):
                for _line in _order.order_line:
                    if _line.product_uom_qty == 0.0 \
                       and _line.product_qty_returned != 0.0:
                        _line.write({'product_id': False})
            return self.write(cr, uid, ids, {'state': 'prepared'}, context)

    def action_draft(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        _order_line_ids = self.pool.get('sale.order.line').search(cr, uid, [('order_id','=',ids[0]),
                                                                            ('product_id','=',False),
                                                                            ('product_uom_qty','=',0.0),
                                                                            ('product_qty_returned','<>',0.0)])
        if len(_order_line_ids) > 0:
            for _line in self.pool.get('sale.order.line').browse(cr, uid, _order_line_ids, context):
                _pos = _line.name.find('] ')
                if _pos != -1:
                    _default_code = _line.name[1:_pos]
                    _product_id = self.pool.get('product.product').search(cr, uid, [('default_code','=',_default_code)])
                    if len(_product_id) > 0:
                        _line.write({'product_id': _product_id[0]})
        
        self.write(cr, uid, ids, {'state':'draft'})
        wf_service = netsvc.LocalService("workflow")
        for _order_id in ids:
            wf_service.trg_delete(uid, 'sale.order', _order_id, cr)
            wf_service.trg_create(uid, 'sale.order', _order_id, cr)
        return True

    def _get_line_price(self, cr, uid, partner, pricelist, date_order, product, uom, uom_quantity):
        _dp = self.pool.get('decimal.precision').precision_get(cr, uid, 'Product Price')

        _partner_id = False
        _product_id = False
        if partner and product:
            _partner_id = self.pool.get('res.partner').browse(cr, uid, partner, None)
            _product_id = self.pool.get('product.product').browse(cr, uid, product, None)

        if _product_id and _product_id.sale_enabled \
           and _partner_id and _partner_id.sale_prices:
            _price = _product_id.sale_price
        else:
            _price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist], product, uom_quantity or 1.0, partner,
                                                                  {'uom': uom or result.get('uom'),
                                                                   'date': date_order}
                                                                  )[pricelist] or 0.0
        return _price

sale_order()
