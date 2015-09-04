# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from product_stock_card import JasperDataParser
from jasper_reports import jasper_report
import pooler
import time, datetime
import base64
import os


class jasper_user_analysis(JasperDataParser.JasperDataParser):
    def __init__(self, cr, uid, ids, data, context):
        super(jasper_user_analysis, self).__init__(cr, uid, ids, data, context)
 
    def generate_data_source(self, cr, uid, ids, data, context):
        return False
 
    def generate_parameters(self, cr, uid, ids, data, context):
        return data['parameters']
 
    def generate_properties(self, cr, uid, ids, data, context):
        return {}

#     def generate_records(self, cr, uid, ids, data, context):
#         pool = pooler.get_pool(cr.dbname)
#         results = []
#         product_id = context.get('active_ids', False)
#         if 'form' in data:
#             domain = data['form']
#         else:
#             domain = [('product_id', 'in', product_id)]
# #        wiz_obj = pool.get('user.analysis').browse(cr, uid,[1])
# #        print dir(wiz_obj)
# ##        user_ids = wiz_obj.user_ids
# #        from_date = wiz_obj.from_date
# #        to_date = wiz_obj.to_date
#        
#         
#         products_data = pool.get('product.product').browse(cr, uid, product_id, context)
#         for product_data in products_data:
#             result = {
#                     'id': product_data.id,
#                     'company_name': product_data.company_id.name,
#                     'company_id': {
#                                     'name': product_data.company_id.name,
#                                     'partner_id': {
#                                                    'street': product_data.company_id.partner_id.street,
#                                                    'street2': product_data.company_id.partner_id.street,
#                                                    'city': product_data.company_id.partner_id.city,
#                                                    'state_id': {'name': product_data.company_id.partner_id.state_id.name},
#                                                    'country_id': {'name': product_data.company_id.partner_id.country_id.name},
#                                                    'zip': product_data.company_id.partner_id.zip,
#                                                    'vat': product_data.company_id.partner_id.vat,
#                                                    'branch': product_data.company_id.partner_id.branch,
#                                                     },
#                                    },
#                       'stock_card_ids': [],
#                     }
#             product_stock_ids = pool.get('product.stock.card').search(cr, uid, domain)
#             product_stock_lines = pool.get('product.stock.card').browse(cr, uid, product_stock_ids, context)
#             for line in product_stock_lines:
#                 stock_card_data = {
#                         'id': line.id,
#                         'name': line.name,
#                         'date': line.date,
#                         'in_qty': line.in_qty,
#                         'out_qty': line.out_qty,
#                         'balance': line.balance,
#                         'default_uom': {'name': line.default_uom.name},
#                         'location_id': {'name': line.location_id.name},
#                         'location_dest_id': {'name': line.location_dest_id.name}
#                           }
#                 result['stock_card_ids'].append(stock_card_data)
#             results.append(result)
#         return results

jasper_report.report_jasper('report.report.product.stock.card', 'product.product', parser=jasper_user_analysis, )
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
