# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Ecosoft Co., Ltd. (http://ecosoft.co.th).
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

from openerp.osv import fields, osv
from openerp.tools.translate import _
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta


class product_stock_card_location(osv.osv_memory):
    _name = "product_stock.card.location"
    _columns = {
        'product_id': fields.many2one('product.product', 'Product', domain=[('type', '!=', 'service')]),
        'location_id': fields.many2one('stock.location', 'Location', required=False, domain=[('usage', '=', 'internal')]),
        'from_date': fields.datetime('From Date'),
        'to_date': fields.datetime('To Date'),
        }

    def open_stock_card(self, cr, uid, ids, context=None):
#         view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'product_stock_card', 'view_product_stock_card_tree')
#         view_id = view_ref and view_ref[1] or False,

        stock_card_location = self.read(cr, uid, ids, ['product_id', 'location_id', 'from_date', 'to_date'], context=context)
        domain = []
        if stock_card_location:
            if stock_card_location[0]['product_id']:
                product = stock_card_location[0]['product_id']
                ctx = {'search_default_product_id': product, 'default_product_id': product, }
            else:
                product = context.get('active_id', False)
                ctx = {'search_default_product_id': product, 'default_product_id': product, }

            if stock_card_location[0]['location_id']:
                ctx.update({'location': stock_card_location[0]['location_id'][0]})
                domain += ['|', ('location_id', '=', stock_card_location[0]['location_id'][0]), ('location_dest_id', '=', stock_card_location[0]['location_id'][0])]
            else:
                domain += [('type', 'not in', ('move', False))]

            if stock_card_location[0]['from_date']:
                start = datetime.strptime(stock_card_location[0]['from_date'], "%Y-%m-%d %H:%M:%S")
                domain += [('date', '>=', start.strftime('%Y-%m-%d'))]
            if stock_card_location[0]['to_date']:
                stop = datetime.strptime(stock_card_location[0]['to_date'], "%Y-%m-%d %H:%M:%S")
                stop = stop + relativedelta(days=1)
                domain += [('date', '<=', stop.strftime('%Y-%m-%d'))]
        return {
                'name': _('Stock Card By Location'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'product.stock.card',
                'type': 'ir.actions.act_window',
                'context': ctx,
                'domain': domain,
                }

    def print_stock_card(self, cr, uid, ids, context=None):
        stock_card_location = self.read(cr, uid, ids, ['product_id', 'location_id', 'from_date', 'to_date'], context=context)
        domain = []
        ctx = context.copy()
        start = None
        stop = None
        parameters = {}
        if stock_card_location:
            if stock_card_location[0]['product_id']:
                product = stock_card_location[0]['product_id'][0]
                ctx = {'search_default_product_id': product, 'default_product_id': product, 'active_id': product}
            else:
                product = context.get('active_id', False)
                ctx = {'search_default_product_id': product, 'default_product_id': product, }

            if stock_card_location[0]['location_id']:
                location_id = stock_card_location[0]['location_id'][0]
                parameters.update({'location_id': location_id})
                ctx.update({'location': location_id})
                domain += ['|', ('location_id', '=', location_id), ('location_dest_id', '=', location_id)]
            else:
                domain += [('type', 'not in', ('move', False))]

            if stock_card_location[0]['from_date']:
                start = datetime.strptime(stock_card_location[0]['from_date'], "%Y-%m-%d %H:%M:%S")
                domain += [('date', '>=', start.strftime('%Y-%m-%d'))]
                parameters.update({'from_date': start.strftime('%Y-%m-%d')})

            if stock_card_location[0]['to_date']:
                stop = datetime.strptime(stock_card_location[0]['to_date'], "%Y-%m-%d %H:%M:%S")
                stop = stop + relativedelta(days=1)
                domain += [('date', '<=', stop.strftime('%Y-%m-%d'))]
                parameters.update({'to_date': stop.strftime('%Y-%m-%d')})

        data = self.read(cr, uid, ids, )[-1]
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'report.product.stock.card',
                'report_type': 'pdf',
                'context': ctx,
                'domain': domain,
                'datas': {
                          'model': 'product.product',
                          'id': product or False,
                          'ids': [product] or [],
                          'form': data,
                          'parameters': parameters,
            },
        }
product_stock_card_location()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
