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
from datetime import datetime
import time
import openerp.addons.decimal_precision as dp


class account_product_cost_recalculation(osv.TransientModel):
    _name = "account.product.cost.recalculation"
    _description = "Recalculate Product Costs"

    _columns = {
        'period_id': fields.many2one('account.period', "Period", required=True,
                                     help="Period for which recalculation will be done."),
        'product_id': fields.many2one('product.product', "Product", domain=[('active', '=', True),
                                                                            ('cost_method', '=', 'average'),
                                                                            ('type', '=', 'product')],
                                      required=False,
                                      help="Product for which recalculation will be done. If not set recalculation will be done for all products with cost method set 'Average Price'"),
    }
    _defaults = {
        'period_id': False,
        'product_id': False,
    }

    def _do_recalculation(self, cr, uid, ids, context=None):
        _recalculation_id = self.browse(cr, uid, ids[0], context)
        _dates = {}
        _digits = {}

        # najdem ustrezna obdobja
        if _recalculation_id.period_id:
            _period = _recalculation_id.period_id
        else:
            raise osv.except_osv(_('Error!'), _('Cannot find suitable dates for recalculation.'))

        _year_start = _period.fiscalyear_id.date_start
        _date_from = _period.date_start
        _date_to = _period.date_stop

        # najdem ustrezne izdelke
        _product_ids = []

        if _recalculation_id.product_id:
            _product_ids.append(_recalculation_id.product_id.id)
        else:
            _product_ids = self.pool.get('product.product').search(cr, uid, [('active', '=', True),
                                                                             ('cost_method', '=', 'average'),
                                                                             ('type', '=', 'product')])

        _digits_obj = self.pool.get('decimal.precision')
        _digits_id = _digits_obj.search(cr, uid, [('name', '=', 'Product Price')])
        if len(_digits_id) > 0:
            _digits['price'] = _digits_obj.browse(cr, uid, _digits_id[0])['digits']
        else:
            _digits['price'] = 2

        _digits_id = _digits_obj.search(cr, uid, [('name', '=', 'Product Unit of Measure')])
        if len(_digits_id) > 0:
            _digits['quantity'] = _digits_obj.browse(cr, uid, _digits_id[0])['digits']
        else:
            _digits['quantity'] = 2

        _digits_id = _digits_obj.search(cr, uid, [('name', '=', 'Account')])
        if len(_digits_id) > 0:
            _digits['account'] = _digits_obj.browse(cr, uid, _digits_id[0])['digits']
        else:
            _digits['account'] = 2

        # preračunam posamezen izdelek
        _products = self.pool.get('product.product').browse(cr, uid, _product_ids, context)
        for _product in _products:

            # izračunam začetno zalogo in ceno
            _dates['date_from'] = _year_start + ' 00:00:00'
            _dates['date_to'] = _date_from + ' 00:00:00'
            _start_stock, _start_cost, _start_period = _product._get_start_stock_and_cost(_dates, _digits)

            # če ni prometa v obdobju pogledam še inventuro
            if not _start_period:
                _dates['date_from'] = _date_from + ' 00:00:00'
                _start_stock, _start_cost = _product._get_inventory_stock_and_cost(_dates, _digits)
            elif _start_period.id != _period.id:
                #if _start_period and _start_period.id != _period.id:
                _new_period = self.pool.get('account.period').next(cr, uid, _start_period, 1, context)
                _new_period = self.pool.get('account.period').browse(cr, uid, _new_period, context)
                _dates['date_from'] = _new_period.date_start + ' 00:00:00'
            else:
                _dates['date_from'] = _date_from + ' 00:00:00'

            if _start_stock <= 0.0 or _start_cost <= 0.0:
                _start_stock = 0.0
                _start_cost = 0.0

            # izračunam povprečno ceno za obdobje
            _dates['date_to'] = _date_to + ' 23:59:59'
            _period_stock, _period_cost = _product._get_purchase_amount_and_cost(_dates, _digits)

            # izračunam skupno vrednost zaloge konec obdobja
            _end_period_stock = round(_start_stock + _period_stock, _digits['quantity'])
            _end_period_cost = round(_start_cost + _period_cost, _digits['price'])

            # izračunam povprečno ceno za obdobje
            _average_cost = False
            if _end_period_stock and _end_period_stock != 0:
                _average_cost = abs(round(_end_period_cost / _end_period_stock, _digits['price']))
            elif _period_stock and _period_stock != 0:
                _average_cost = abs(round(_period_cost / _period_stock, _digits['price']))

            # zapišem povprečno ceno v tabelo
            if _average_cost and _average_cost != 0:
                _product_cost_id = self.pool.get('product.period.cost').search(cr, uid,
                                                                               [('product_id', '=', _product.id),
                                                                                ('period_id', '=', _period.id)])
                if len(_product_cost_id) != 0:
                    self.pool.get('product.period.cost').write(cr, uid, _product_cost_id, {'price_unit': _average_cost})
                else:
                    self.pool.get('product.period.cost').create(cr, uid, {'product_id': _product.id,
                                                                          'period_id': _period.id,
                                                                          'price_unit': _average_cost})
        return True

    def execute(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if self._do_recalculation(cr, uid, ids, context):
            return {'type': 'ir.actions.act_window_close'}
        else:
            return False
