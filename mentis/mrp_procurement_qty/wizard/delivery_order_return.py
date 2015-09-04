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

#####
# Wizard trigers a report, that shows a list of delivery orders and returns from original delivery order
#####


from osv import fields, osv
from tools.translate import _
import time

class delivery_orders_return_wizard(osv.osv_memory):
    _name = "delivery.order.return.wizard"
    _description = "Delivery Order return wizard"
    _columns = {
        'copy_num': fields.integer('Število kopij'),
        'customer_copy_num': fields.boolean('Uporabi število kopij določenih na postavki kupca'), 
    }
    _defaults = {
        'copy_num': lambda *a: 1,
        'customer_copy_num': lambda *a: 1,
    }
        
    def execute(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        #copy_num = self.browse(cr,uid,ids)[0].copy_num
        customer_copy_num = self.browse(cr,uid,ids)[0].customer_copy_num
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        trans_obj = self.pool.get('ir.translation')
        active_ids = context.get('active_ids',[])
        list_data = []
        
        for pick in picking_obj.browse(cr, uid, active_ids): #za vsak delovni nalog
            if customer_copy_num:
                copy_num = pick.partner_id.delivery_copies
            else:
                copy_num = self.browse(cr,uid,ids)[0].copy_num
            for repeat in range(0, copy_num):
                dict_moves = {}
                
                sum_price_total = 0
                move_ids = move_obj.search(cr, uid, [('picking_id','=',pick.id)], order='product_id')
                for line in move_obj.browse(cr, uid, move_ids):
                    dict_temp = {}
                    
                    dict_temp['ean'] = line.product_id.ean13                     
                    naziv = '['+line.product_id.default_code+'] '+line.product_id.name_template
                    if line.product_id.variants:
                        naziv = naziv +' - '+line.product_id.variants
                    dict_temp['desc'] = naziv
                    
                    trans_source =  trans_obj._get_source(cr, uid, None, 'model', context['lang'], line.product_uom.name)
                    dict_temp['em'] = trans_source
                    
                    dict_temp['qty_ordered'] = line.sale_line_id.product_uos_qty
                    dict_temp['qty'] = line.basket_deliverd
                    dict_temp['qty_returned'] = line.product_qty_returned
                    dict_temp['qty_for_invoice'] = line.basket_deliverd - line.product_qty_returned
                    
                    
                    #Dodamo ceno
                    if line.picking_id.partner_id.delivery_prices:
                        _price = line.sale_line_id.price_unit * (1 - (line.sale_line_id.discount or 0.0) / 100.0)
                        #_price_tax = self.pool.get('account.tax').compute_all(cr, uid, line.sale_line_id.tax_id, _price, 1, line.sale_line_id.product_id, line.sale_line_id.order_id.partner_id)['total']
                        dict_temp['price'] = _price
                        value = self.pool.get('account.tax').compute_all(cr, uid, line.sale_line_id.tax_id, _price, (line.basket_deliverd-line.product_qty_returned), line.sale_line_id.product_id, line.sale_line_id.order_id.partner_id)['total']
                        
                        dict_temp['price_total'] = value
                        sum_price_total = sum_price_total + value
                    else:
                        dict_temp['price'] = ''
                        dict_temp['price_total'] = ''
                    
                    if line.product_id.id in dict_moves.keys():
                        newid = line.product_id.id + 1000000 #tudi ce pride po podvojitve produkta ga ne sestevamo ampak 2x izpisemo, vracilo samo na prvega
                        dict_moves[newid] = dict_temp
                    else:
                        dict_moves[line.product_id.id] = dict_temp
                    #dict_moves[line.sale_line_id.name] = dict_temp
                
                #Ker je lahko na sale.orderju produkt brez product_id ga na nepotrjeni dobavnici se ni
                #V tem primeru ga moramo dobiti iz sale.orderja
                if pick.state != 'done':
                    sale_line_ids = self.pool.get('sale.order.line').search(cr, uid, [('order_id', '=', pick.sale_id.id),
                                                                                      ('product_id', '=', False),
                                                                                      ])
                    for sale_line in self.pool.get('sale.order.line').browse(cr, uid, sale_line_ids):
                        original_code = sale_line.name[sale_line.name.find("[")+1:sale_line.name.find("]")]
                        new_product_id = self.pool.get('product.product').search(cr, uid, [('default_code', '=', original_code)])
                        new_product = self.pool.get('product.product').browse(cr, uid, new_product_id)[0]
                    
                        dict_temp = {}
                        naziv = '['+new_product.default_code+'] '+new_product.name_template
                        if new_product.variants:
                            naziv = naziv +' - '+new_product.variants
                        dict_temp['desc'] = naziv
                        
                        trans_source =  trans_obj._get_source(cr, uid, None, 'model', context['lang'], sale_line.product_uom.name)
                        dict_temp['em'] = trans_source
                        
                        dict_temp['qty_ordered'] = ''
                        dict_temp['qty'] = ''
                        dict_temp['qty_returned'] = sale_line.product_qty_returned
                        dict_temp['qty_for_invoice'] = 0 - sale_line.product_qty_returned
                        
                        #Dodamo ceno
                        if sale_line.order_id.partner_id.delivery_prices:
                            _price = sale_line.price_unit * (1 - (sale_line.discount or 0.0) / 100.0)
                            dict_temp['price'] = _price
                            
                            value = self.pool.get('account.tax').compute_all(cr, uid, sale_line.tax_id, _price, (0 - sale_line.product_qty_returned), new_product_id[0], sale_line.order_id.partner_id)['total']
                            dict_temp['price_total'] = value
                            #sum_price = sum_price + _price_tax
                            sum_price_total = sum_price_total + value #ker je value vedno negativen
                        else:
                            dict_temp['price'] = ''
                            dict_temp['price_total'] = ''
                
                        if new_product_id[0] in dict_moves.keys():
                            newid = new_product_id[0] + 2000000 #tudi ce pride po podvojitve produkta ga ne sestevamo ampak 2x izpisemo, vracilo samo na prvega
                            dict_moves[newid] = dict_temp
                        else:
                            dict_moves[new_product_id[0]] = dict_temp
                #preverimo ali ima delovni nalog preko prodajnega vezavo na originalni delovni nalog
#                if pick.sale_id.delivery_order_ref_ids:
#                    for pick_orig in picking_obj.browse(cr, uid, [pick.sale_id.delivery_order_ref_ids.id]): #original stock.picking
#                        for move_orig in pick_orig.move_lines: #original stock.move
#                            if move_orig.product_id.id in dict_moves: #ce je product na novem pickingu samo zapisem vrnjene kolicine
#                                dict_moves[move_orig.product_id.id]['qty_returned'] = move_orig.product_qty_returned
#                            else: # v primeru da izdelka ni na trenutnem nalogu, bil pa je na originalnem
#                                dict_temp = {}
#                                dict_temp['desc'] = move_orig.sale_line_id.name
#                                dict_temp['em'] = _(move_orig.product_uom.name)
#                                dict_temp['qty_ordered'] = 0 #move_orig.sale_line_id.product_uos_qty
#                                dict_temp['qty'] = 0
#                                dict_temp['qty_returned'] = move_orig.product_qty_returned

                
                
                sorted_list = sorted(dict_moves.iteritems(), key=lambda (x, y): y['desc'])
                
                dict_data = {}
                dict_data['moves'] = sorted_list
                dict_data['name'] = pick.name
                dict_data['address_title'] = pick.partner_id.title.name
                dict_data['address_name'] = pick.partner_id.name
                dict_data['address_street'] = pick.partner_id.street
                dict_data['address_zip'] = pick.partner_id.zip
                dict_data['address_city'] = pick.partner_id.city
                trans_country =  trans_obj._get_source(cr, uid, None, 'model', context['lang'], pick.partner_id.country_id.name)
                dict_data['address_country'] = trans_country
                dict_data['date'] = pick.date
                dict_data['origin'] = pick.origin
                dict_data['note'] = pick.note
                dict_data['lang'] = pick.partner_id.lang
                dict_data['basket_number'] = pick.basket_number
                if sum_price_total == 0:
                    dict_data['sum_price_total'] = ''
                else:
                    dict_data['sum_price_total'] = sum_price_total
                    
                list_data.append(dict_data)
        
        data = {'form':list_data}
        return {'type': 'ir.actions.report.xml', 'report_name': 'delivery.order.return.report', 'datas': data}
    
delivery_orders_return_wizard()

