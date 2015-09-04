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

#import time
#from datetime import datetime

#import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv
#from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP
from openerp.tools import float_compare
#from openerp.tools.translate import _
from openerp import netsvc
#from openerp import tools
import math
from openerp.tools.safe_eval import safe_eval


class mrp_production(osv.osv):
    _inherit = 'mrp.production'
    
    def create(self, cr, user, vals, context=None):
        
        if context is None:
            context = {}
            
        ir_config_parameter = self.pool.get('ir.config_parameter')
        empty_location_active = safe_eval(ir_config_parameter.get_param(cr, user, 'stock.empty_location_active', 'False'))
        if empty_location_active == 1:
            empty_location_id = safe_eval(ir_config_parameter.get_param(cr, user, 'stock.empty_location', 'False'))
            loc_id = int(empty_location_id)
        else:
            loc_id = 12
        
        context['product_id'] = vals['product_id']
        stock_values = self.pool.get('stock.location')._product_value(cr, user, [loc_id], ['stock_real'], arg=None, context=context)
        vals['product_qty_onstock'] = int(stock_values[loc_id]['stock_real'])
        
        #Koliko je bilo v resnici naroceno, ce se naredi delovni za polizdelek zaradi izdelka potem je narocena kolicina 0
        move_ids = self.pool.get('stock.move').search(cr, user, [('product_id','=',vals['product_id']),
                                                      ('basket_status','=',3)])
        prod_ordered = 0
        for move_line in self.pool.get('stock.move').browse(cr, user, move_ids):
            prod_ordered = prod_ordered + move_line.product_qty
        vals['product_qty_ordered'] = prod_ordered
        
        res = super(mrp_production, self).create(cr, user, vals, context=context)
        return res
    
    def _prepare_product_id(self, cr, uid, ids, field_names, arg, context):
        res = {}
        if context is None:
            context = {}
            
        null_result = {}
        null_result['product_with_bom_id'] = 0
        null_result['product_with_bom_factor'] = 0.0
        null_result['product_with_bom_relation'] = False
        #dict((fn, 0.0) for fn in field_names)
        
        mrp_bom_obj = self.pool.get('mrp.bom')
        for line in self.browse(cr, uid, ids):
            res_sub = {}
            #Poiscemo id kosovnice danega proizvoda
            mrp_main_bom_id = mrp_bom_obj.search(cr, uid, [('product_id', '=', line.product_id.id), ('bom_id', '=', False)])
            main_bom_qty = mrp_bom_obj.browse(cr, uid, mrp_main_bom_id)[0].product_qty #faktor na kosovnici iskanega produkta
            
            #Na kosovnici je lahko vec proizvodov
            mrp_sub_bom_ids = mrp_bom_obj.search(cr, uid, [('bom_id', 'in', mrp_main_bom_id)])
            
#            for mrp_sub_id in mrp_bom_obj.browse(cr, uid, mrp_sub_bom_ids):
#                if len(mrp_sub_bom_ids) == 1:
#                    final_id = mrp_sub_id.id
#                else:
#                    #Dobimo id proizvoda, za tega potem pogledamo ali ima BOM
#                    final_id = mrp_bom_obj.search(cr, uid, [('product_id', '=', mrp_sub_id.product_id.id), ('bom_id', '=', False)])
#                
#                if final_id: #nasli smo proizvod s kosovnico (TABELA: PRODUCT.TEMPLATE)
#                    res_sub['product_with_bom_id'] = mrp_sub_id.product_id.id
#                    res_sub['product_with_bom_relation'] = mrp_sub_id.product_id.id
#                    res_sub['product_with_bom_factor'] =  mrp_sub_id.product_qty/main_bom_qty
#                    break
            lst_bom = []
            dict_bom_qty = {}
            for mrp_sub_id in mrp_bom_obj.browse(cr, uid, mrp_sub_bom_ids):
                if len(mrp_sub_bom_ids) == 1:
                    res_sub['product_with_bom_id'] = mrp_sub_id.product_id.id
                    res_sub['product_with_bom_relation'] = mrp_sub_id.product_id.id
                    res_sub['product_with_bom_factor'] =  mrp_sub_id.product_qty/main_bom_qty
                    break
                else:
                    lst_bom.append(mrp_sub_id.product_id.id)
                    dict_bom_qty[mrp_sub_id.product_id.id] = mrp_sub_id.product_qty #si moram shranit, ker ga uporabim kasneje, ker je kasnejsi qty od spodnjega boma
                    
            #Dobimo id proizvodov, za katere potem pogledamo ali ima BOM
            final_ids = mrp_bom_obj.search(cr, uid, [('product_id', 'in', lst_bom), ('bom_id', '=', False)])
            for mrp_sub_final_id in mrp_bom_obj.browse(cr, uid, final_ids):
                bom_qty = dict_bom_qty[mrp_sub_final_id.product_id.id]
                if len(final_ids) == 1:
                    res_sub['product_with_bom_id'] = mrp_sub_final_id.product_id.id
                    res_sub['product_with_bom_relation'] = mrp_sub_final_id.product_id.id
                    res_sub['product_with_bom_factor'] =  bom_qty/main_bom_qty
                    break
                else:
                    if mrp_sub_final_id.product_id.categ_id.id == 7:
                        res_sub['product_with_bom_id'] = mrp_sub_final_id.product_id.id
                        res_sub['product_with_bom_relation'] = mrp_sub_final_id.product_id.id
                        res_sub['product_with_bom_factor'] =  bom_qty/main_bom_qty
                        break

                    
            if res_sub:
                res[line.id] = res_sub
            else:
                res[line.id] = null_result
                
        return res
    
#    def _get_prod_qty_available(self, cr, uid, ids, field_name, arg=None, context=None):
#        res = {}
#        for order in self.browse(cr, uid, ids):
#            qty_available = order.product_id.qty_available
#            qty_produced = 0
#            qty_reserved = 0.00
#            
#            #Se sprehodimo po odprtih delovnih nalogih in sestejemo narejeno kolicino tega produkta
#            ready_prod_ids = self.search(cr, uid, [('state', 'in', ['ready', 'confirmed']),
#                                              ('product_id', '=', order.product_id.id)])
#            for order_ready in self.browse(cr, uid, ready_prod_ids, context=context):
#                qty_produced += order_ready.produced - order_ready.scrap - order_ready.produced_stock
#                
#            #Po delovnih nalogih kjer je produkt product_with_bom_id produkt
#            bom_prod_ids = self.search(cr, uid, [('state', 'in', ['ready', 'confirmed']),
#                                              ('product_with_bom_id', '=', order.product_id.id)])
#            for order_bom in self.browse(cr, uid, bom_prod_ids, context=context):
#                qty_reserved += (order_bom.produced/order_bom.product_with_bom_factor)
#                
#            res[order.id] = qty_available + qty_produced - qty_reserved
#        return res
    
    def _get_prod_on_bom_qty_available(self, cr, uid, ids, field_name, arg=None, context=None):
        
        if context is None:
            context = {}
        res = {}
        for order in self.browse(cr, uid, ids):
            qty_available = 0.0
            qty_produced = 0.0
            qty_reserved = 0.0
            qty_from_stock = 0.0 #kar je dano iz hladilnice
            faktor = 0.0
            #qty_available_sandi = product_obj.qty_available_location(cr, uid, [order.product_with_bom_relation.id], [12], context=context)
            #Se sprehodimo po odprtih delovnih nalogih in sestejemo narejeno kolicino tega produkta
            ready_prod_ids = self.search(cr, uid, [('state', 'in', ['ready', 'confirmed']),
                                              ('product_id', '=', order.product_with_bom_relation.id)])
            for order_ready in self.browse(cr, uid, ready_prod_ids, context=context):
                qty_produced += order_ready.produced - order_ready.scrap - order_ready.produced_stock
                qty_produced += order_ready.product_on_bom_qty_ready #nalozeni izdelki direktno za ta produkt
                
            
            #Po delovnih nalogih kjer je produkt product_with_bom_id produkt
            bom_prod_ids = self.search(cr, uid, [('state', 'in', ['ready', 'confirmed']),
                                              ('product_with_bom_id', '=', order.product_with_bom_relation.id)])
            for order_bom in self.browse(cr, uid, bom_prod_ids, context=context):
                if (order.id == order_bom.id):
                    faktor = order_bom.product_with_bom_factor
                if order_bom.produced != 0 and order_bom.product_with_bom_factor:
                    qty_reserved += (order_bom.produced*order_bom.product_with_bom_factor)
                    #qty_from_stock += (order_bom.product_on_bom_qty_ready/order_bom.product_with_bom_factor) #kar je dano iz hladilnice
                qty_from_stock += order_bom.product_on_bom_qty_O_ready #Nalozena zaloga polizdelka na ta P_izdelek
                    
            
            res_tmp = {}
            if (faktor != 0):
                tmp_sum = (qty_produced - qty_reserved + qty_from_stock)/faktor
            else:
                tmp_sum = (qty_produced - qty_reserved + qty_from_stock)
            tmp_sum = int(tmp_sum)
            
            res_tmp['product_on_bom_qty_available'] = tmp_sum
            
            #-------------------------------------------------------------------------------------
            #Pogledamo se ali je polizdelek in se kupuje ali pa je izdelek - potem zracunamo zalogo
            if order.product_with_bom_relation:
                if (order.product_with_bom_relation.product_tmpl_id.categ_id.parent_id.id == 34 and order.product_with_bom_relation.product_tmpl_id.supply_method == 'buy') or order.product_with_bom_relation.product_tmpl_id.categ_id.parent_id.id == 38:
                    context['product_id'] = order.product_with_bom_relation.id
                    
                    stock_values = self.pool.get('stock.location')._product_value(cr, uid, [12], ['stock_real'], arg=None, context=context)
                    #stock_sandi = self.pool.get('product.product').qty_available_location(cr, uid, [order.product_with_bom_relation.id], [12], context=context)
                    res_tmp['product_on_bom_qty_stock'] = int(stock_values[12]['stock_real'])
                else:
                    res_tmp['product_on_bom_qty_stock'] = 0
            else:
                res_tmp['product_on_bom_qty_stock'] = 0
                
            if order.product_id.product_tmpl_id.categ_id.parent_id.id == 38:
                if order.product_with_bom_relation:
                    #_____________________________________
                    
                    product_obj = self.pool.get('product.product')
                    pro_name = product_obj.name_get(cr, uid, [order.product_with_bom_relation.id], context)
                    
#                    tmp_name = '['
#                    if order.product_with_bom_relation.default_code:
#                        tmp_name = tmp_name + order.product_with_bom_relation.default_code
#                        
#                    if order.product_with_bom_relation.name_template:
#                        tmp_name = tmp_name + '] >'+ order.product_with_bom_relation.name_template
#                        
#                    if order.product_with_bom_relation.variants:
#                        tmp_name = tmp_name + ' - ' + order.product_with_bom_relation.variants
                    
                    res_tmp['product_is_product'] = pro_name
                else:
                    res_tmp['product_is_product'] = '[' + order.product_id.default_code + '] <'+ order.product_id.name_template + '[Osnova] - ' + order.product_id.variants
            else:
                res_tmp['product_is_product'] = ''
            
            #res_tmp['product_on_bom_qty_stock'] = int(qty_available_sandi) - qty_from_stock
            
            res[order.id] = res_tmp
        return res
    
    def get_qty_delivery_available(self, cr, uid, production_id=False, stock_id=False, product_id=False, context=None):
        stock_move_obj = self.pool.get('stock.move')
        res = stock_move_obj.get_qty_delivery_available(cr, uid, production_id, stock_id, product_id, context=context)
        return res
    
    _columns = {
        'created_from_op': fields.boolean('Created from orderpoint'),
        'product_qty_onstock': fields.float('Product qty on stock', digits=(6,2)),
        #'product_qty_available': fields.function(_get_prod_qty_available, string='Product quantity available'),
        'product_is_product': fields.function(_get_prod_on_bom_qty_available, string='Product is product', multi='prepare0'),
        'product_on_bom_qty_available': fields.function(_get_prod_on_bom_qty_available, string='Product on BOM quantity available', multi='prepare0'),
        'product_on_bom_qty_stock': fields.function(_get_prod_on_bom_qty_available, string='Product on BOM stock available', multi='prepare0'),
        'product_on_bom_qty_ready': fields.float('Load from stock', digits=(6,2)),
        'product_on_bom_qty_P_ready': fields.float('Load P from stock', digits=(6,2)),
        'product_on_bom_qty_O_ready': fields.float('Load O from stock', digits=(6,2)),
        'product_with_bom_factor': fields.function(_prepare_product_id, digits=(12,4), method=True, store=True,  string='BOM factor', multi='prepare1'),
        'product_with_bom_id': fields.function(_prepare_product_id, type='integer', method=True, store=True,  string='Product with BOM id', multi='prepare1'),
        'product_with_bom_relation': fields.function(_prepare_product_id, type='many2one', obj='product.product', method=True, store=True,  string='Product with BOM name', multi='prepare1'),
        'product_with_bom_name': fields.related('product_with_bom_relation', 'name_template', type='char', string='Product with BOM name'),
        'product_qty_ordered': fields.float('Product ordered', digits=(6,2)),
    }

    def action_produce(self, cr, uid, production_id, production_qty, production_mode, context=None):
        """ To produce final product based on production mode (consume/consume&produce).
        If Production mode is consume, all stock move lines of raw materials will be done/consumed.
        If Production mode is consume & produce, all stock move lines of raw materials will be done/consumed
        and stock move lines of final product will be also done/produced.
        @param production_id: the ID of mrp.production object
        @param production_qty: specify qty to produce
        @param production_mode: specify production mode (consume/consume&produce).
        @return: True
        
        ##Changed line, where comparing mrp.product.line and stock.move
        """
        stock_mov_obj = self.pool.get('stock.move')
        production = self.browse(cr, uid, production_id, context=context)

        produced_qty = 0
        for produced_product in production.move_created_ids2:
            if (produced_product.scrapped) or (produced_product.product_id.id != production.product_id.id):
                continue
            produced_qty += produced_product.product_qty
        if production_mode in ['consume','consume_produce']:
            consumed_data = {}

            # Calculate already consumed qtys
            for consumed in production.move_lines2:
                if consumed.scrapped:
                    continue
                if not consumed_data.get(consumed.product_id.id, False):
                    consumed_data[consumed.product_id.id] = 0
                consumed_data[consumed.product_id.id] += consumed.product_qty

            # Find product qty to be consumed and consume it
            for scheduled in production.product_lines:

                # total qty of consumed product we need after this consumption
                total_consume = ((production_qty + produced_qty) * scheduled.product_qty / production.product_qty)

                # qty available for consume and produce
                qty_avail = scheduled.product_qty - consumed_data.get(scheduled.product_id.id, 0.0)

                if qty_avail <= 0.0:
                    # there will be nothing to consume for this raw material
                    continue

                raw_product = [move for move in production.move_lines if (move.product_id.id==scheduled.product_id.id and move.product_qty==scheduled.product_qty)]
                if raw_product:
                    # qtys we have to consume
                    qty = total_consume - consumed_data.get(scheduled.product_id.id, 0.0)
                    if float_compare(qty, qty_avail, precision_rounding=scheduled.product_id.uom_id.rounding) == 1:
                        # if qtys we have to consume is more than qtys available to consume
                        prod_name = scheduled.product_id.name_get()[0][1]
                        raise osv.except_osv(_('Warning!'), _('You are going to consume total %s quantities of "%s".\nBut you can only consume up to total %s quantities.') % (qty, prod_name, qty_avail))
                    if qty <= 0.0:
                        # we already have more qtys consumed than we need
                        continue

                    raw_product[0].action_consume(qty, raw_product[0].location_id.id, context=context)

        if production_mode == 'consume_produce':
            # To produce remaining qty of final product
            #vals = {'state':'confirmed'}
            #final_product_todo = [x.id for x in production.move_created_ids]
            #stock_mov_obj.write(cr, uid, final_product_todo, vals)
            #stock_mov_obj.action_confirm(cr, uid, final_product_todo, context)
            produced_products = {}
            for produced_product in production.move_created_ids2:
                if produced_product.scrapped:
                    continue
                if not produced_products.get(produced_product.product_id.id, False):
                    produced_products[produced_product.product_id.id] = 0
                produced_products[produced_product.product_id.id] += produced_product.product_qty

            for produce_product in production.move_created_ids:
                produced_qty = produced_products.get(produce_product.product_id.id, 0)
                subproduct_factor = self._get_subproduct_factor(cr, uid, production.id, produce_product.id, context=context)
                rest_qty = (subproduct_factor * production.product_qty) - produced_qty

                if rest_qty < production_qty:
                    prod_name = produce_product.product_id.name_get()[0][1]
                    raise osv.except_osv(_('Warning!'), _('You are going to produce total %s quantities of "%s".\nBut you can only produce up to total %s quantities.') % (production_qty, prod_name, rest_qty))
                if rest_qty > 0 :
                    stock_mov_obj.action_consume(cr, uid, [produce_product.id], (subproduct_factor * production_qty), context=context)

        for raw_product in production.move_lines2:
            new_parent_ids = []
            parent_move_ids = [x.id for x in raw_product.move_history_ids]
            for final_product in production.move_created_ids2:
                if final_product.id not in parent_move_ids:
                    new_parent_ids.append(final_product.id)
            for new_parent_id in new_parent_ids:
                stock_mov_obj.write(cr, uid, [raw_product.id], {'move_history_ids': [(4,new_parent_id)]})

        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'mrp.production', production_id, 'button_produce_done', cr)
        return True

