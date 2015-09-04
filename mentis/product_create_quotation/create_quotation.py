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
from datetime import datetime
from tools.translate import _

class create_quotation_from_products(osv.osv_memory):
    _name = "product.create.quotation"
    _description = "Create quotation from selected products"
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Customer', required=True),
        'product_qty': fields.integer('Product quantity', required=True),
                }
    _defaults = {
        'product_qty': lambda *a: 1,
                 }
    
    def create_quotation(self, cr, uid, ids, context=None):
        
        if context is None:
            context={}
            
        product_obj = self.pool.get('product.product')
        sale_obj = self.pool.get('sale.order')
        
        active_ids = context.get('active_ids',[])
        product_qty = self.browse(cr,uid,ids)[0]['product_qty'] #podatki iz trenutne wizard vrstice
        partner_id = self.browse(cr,uid,ids)[0]['partner_id'] #podatki iz trenutne wizard vrstice
        
        order_lines = []
        #Se sprehodimo po izbranih produktih in izdelujemo dictionary
        for prod in product_obj.browse(cr, uid, active_ids, context=context):
            vals_lines = {}
            vals_lines['product_uos_qty'] = product_qty
            vals_lines['product_id'] = prod.id
            vals_lines['product_uom'] = prod.uom_id.id
            vals_lines['discount'] = 0
            vals_lines['price_unit'] = prod.list_price
            vals_lines['product_uom_qty'] = product_qty
            vals_lines['delay'] = prod.produce_delay
            vals_lines['product_uos'] = prod.uos_id.id
            vals_lines['th_weight'] = 0
            vals_lines['product_packaging'] = False
            vals_lines['tax_id'] = False
            vals_lines['type'] = prod.procure_method
            
            product_name = ''
            if prod.variants:
                product_name = '[' + prod.code + ']' + ' ' + prod.name + ' - ' + prod.variants
            else:
                product_name = '[' + prod.code + ']' + ' ' + prod.name
            vals_lines['name'] = product_name
            
            tmp_list = [0, False, vals_lines]
            order_lines.append(tmp_list)
        
        
        vals= {}
        vals['origin'] = False
        vals['message_follower_ids'] = False
        
        vals['order_line'] = order_lines
        
        vals['picking_policy'] = 'direct'
        vals['order_policy'] = 'picking'
        vals['invoice_quantity'] = 'procurement'
        vals['client_order_ref'] = False
        vals['date_order'] = datetime.now().strftime("%Y-%m-%d")
        vals['partner_id'] = partner_id.id
        vals['message_ids'] = False
        vals['fiscal_position'] = 1
        vals['user_id'] = 1
        vals['payment_term'] = 2
        vals['note'] = False
        vals['clause_ids'] = [[6, False, []]]
        vals['pricelist_id'] = 1
        vals['project_id'] = False
        vals['incoterm'] = False
        vals['partner_invoice_id'] = partner_id.id
        vals['invoice_type_id'] = 2
        vals['partner_shipping_id'] = partner_id.id
        vals['shop_id'] = 1
        
        
        sale_obj.create(cr, uid, vals, context=context)
        
        
        
        
        return {
                'type': 'ir.actions.act_window_close',
        }
    
create_quotation_from_products()
