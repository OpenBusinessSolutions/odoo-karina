# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Mentis d.o.o.
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
from openerp.tools.safe_eval import safe_eval

class transport(osv.osv):
    _name = "transport"
    _description = "Manage transport"
    _columns = {
        'name': fields.char('Transport name', size=64, required=True),
        'description': fields.text('Description'),
        'transporter_id': fields.many2one('res.partner', 'Transporter'),
        'price': fields.float('Transport Price', digits_compute= dp.get_precision('Sale Price')),
    }
    
transport()

class sales_order(osv.osv):
    _inherit = "sale.order"
        
    def insert_default_supplier(self, cr, uid, line, context=None):
        if not line.product_id.product_tmpl_id.seller_ids:
            
            ir_config_parameter = self.pool.get('ir.config_parameter')
            partner_id = safe_eval(ir_config_parameter.get_param(cr, uid, 'sale.default_supplier_id', 'False'))
            
            #partner_id = self.get_default_supplier(cr, uid, context)
            
            if partner_id:
                supplierinfo_obj = self.pool.get('product.supplierinfo')
                supplierinfo_obj.create(cr, uid, {  'name':partner_id,
                                                'delay':1,
                                                'min_qty':0,
                                                'product_id':line.product_id.id,
                                              })
        
    def _prepare_order_line_procurement(self, cr, uid, order, line, move_id, date_planned, context=None):
        res = super(sales_order,self)._prepare_order_line_procurement( cr, uid, order, line, move_id, date_planned, context)
        res['customer_id'] = order.partner_id.id
        res['customer_delivery_id'] = order.partner_shipping_id.id
        
        res['sale_price'] = line.price_unit
        
        self.insert_default_supplier(cr, uid, line, context)
        return res
    
sales_order()

class sales_order_line(osv.osv):
    _inherit = "sale.order.line"
    _columns = {
        'product_notes': fields.char('Notes', size=256),
    }
    
sales_order_line()

class procurement_order(osv.osv):
    _inherit = 'procurement.order'
    _columns = {
        'customer_id': fields.many2one('res.partner', 'Customer'),
        'sale_price': fields.float('Sale Price', digits_compute= dp.get_precision('Sale Price')),
        'customer_delivery_id': fields.many2one('res.partner', 'Delivery Address'),
    }
    
    def create_procurement_purchase_order(self, cr, uid, procurement, po_vals, line_vals, context=None):
        line_vals['customer_id'] = procurement.customer_id.id
        line_vals['customer_delivery_id'] = procurement.customer_delivery_id.id
        line_vals['sale_price'] = procurement.sale_price
        line_vals['name'] = procurement.name
        
        po_vals['customer'] = procurement.customer_id.name
        po_vals['customer_delivery'] = procurement.customer_delivery_id.name
        po_vals['product_description'] = procurement.name
        return super(procurement_order,self).create_procurement_purchase_order(cr, uid, procurement, po_vals, line_vals, context)
        

procurement_order()

class purchase_order(osv.osv):
    _name = "purchase.order"
    _inherit = "purchase.order"
    _columns = {
        'transport_id': fields.many2one('transport', 'Transport', help="Manage transport for this Purchase Order"),
        'customer': fields.char('Customer', size=128),
        'customer_delivery': fields.char('Delivery Address', size=128),
        'product_description': fields.char('Product desc.', size=128),
    }
    
  
    
    def get_next_number(self, cr, uid, list_move, list_order, number):       
        while ((number not in list_order) or (number in list_move)):
            number += 1
        return number
        
    
    def get_move_list(self, cr, uid, dict_move):
        #dict: [{'id': 101, 'move_dest_id': False}, {'id': 102, 'move_dest_id': False}]
        list_move = []
        for dict_tmp in dict_move:
            if dict_tmp['move_dest_id']:
                ajdi = dict_tmp['move_dest_id'][0]
                list_move.append(ajdi)
        return list_move
    
    def do_merge(self, cr, uid, ids, context=None):
        
        #najprej pogledam, ce imajo linije move_id, ce ne jim sam vpisem cifro, ki jo kasneje zbrisem
        dict_move_dest = {}
        order_lines_obj = self.pool.get('purchase.order.line')
        order_line_ids = order_lines_obj.search(cr, uid, [('order_id', 'in', ids)], context=context)
        
        dict_move = order_lines_obj.read(cr, uid, order_line_ids, ['move_dest_id'])
        list_move = self.get_move_list(cr, uid, dict_move) #katere stevilke so ze mogoce vpisane, ce se je preneslo iz sale
        list_order = self.search(cr, uid, [('id','<',200)]) #katere stevilke lahko uporabim, stock.move
        
        move_dest_num = self.get_next_number(cr, uid, list_move, list_order, 1)
        
        
        for lines in order_lines_obj.browse(cr, uid, order_line_ids, context=context):
            move_id = lines.move_dest_id.id
            if move_id:
                dict_move_dest[lines.id] = {'changed':0,'value':move_id}
            else:
                dict_move_dest[lines.id] = {'changed':1,'value':move_dest_num}
                order_lines_obj.write(cr, uid, [lines.id], {'move_dest_id':move_dest_num})
                
                move_dest_num += 1
                move_dest_num = self.get_next_number(cr, uid, list_move, list_order, move_dest_num)
                
        
        
        allorders = super(purchase_order,self).do_merge(cr, uid, ids, context)
        
        customer_name = ''
        delivery_name = ''
        desc_name = ''
        
        list_cust = []
        list_del = []
        
        
        for new_order in allorders: #iz lista dobimo nov purchase order ID
            #glede na nov ID v dictionary dobimo ids zdruzenih starih order_listov
            order_line_ids = order_lines_obj.search(cr, uid, [('order_id', 'in', allorders[new_order])], context=context) 
            for lines in order_lines_obj.browse(cr, uid, order_line_ids, context=context):
                move_id = lines.move_dest_id.id
                sale_price = lines.sale_price
                customer_id = lines.customer_id.id
                delivery_id = lines.customer_delivery_id.id
                country_orig_id = lines.country_origin_id.id
                extra_dim = lines.extra_dimensions
                
                #----------CUSTOMER----------
                if customer_id and (not customer_id in list_cust):
                    list_cust.append(customer_id)
                    
                    if customer_name == '':
                        customer_name = (lines.customer_id.name or '')
                    else:
                        customer_name = customer_name + ", " + lines.customer_id.name
                        
                #----------DELIVERY----------
                if delivery_id and (not delivery_id in list_del):
                    list_del.append(delivery_id)
                    
                    if delivery_name == '':
                        delivery_name = (lines.customer_delivery_id.name or '')
                    else:
                        delivery_name = delivery_name + ", " + lines.customer_delivery_id.name
                        
                #-----PRODUCT-DESCRIPTION-----                    
                if desc_name == '':
                    desc_name = lines.name
                else:
                    desc_name = 'more products'
                
                
                new_line_id = order_lines_obj.search(cr, uid , [('order_id','=', new_order), ('move_dest_id', '=', move_id)])
                
                
                if dict_move_dest[lines.id]["changed"]:
                    tmp_move = None
                else:
                    tmp_move = move_id
                
                #zapisemo custom vrednosti v nove linije
                order_lines_obj.write(cr, uid, new_line_id, {   'sale_price': sale_price,
                                                                'customer_id': customer_id,
                                                                'customer_delivery_id': delivery_id,
                                                                'country_origin_id': country_orig_id,
                                                                'extra_dimensions': extra_dim,
                                                                'move_dest_id': tmp_move })
            #__________konec iskanja, zapisov po vrstici_______
            #sedaj se sprehodimo po izbranih orderjih in skupaj potegnemo se origin in transport
            origin_name = ''
            list_origin = []
            transport_id = 0
            for old_order in self.browse(cr, uid, ids):
                #----------ORIGIN----------
                if old_order.origin not in list_origin:
                    list_origin.append(old_order.origin)
                    
                    if origin_name == '':
                        origin_name = (old_order.origin or '')
                    else:
                        origin_name = origin_name + ", " + old_order.origin
                transport_id = old_order.transport_id.id
                
            
            #zapisemo zdruzenega customerja v nov PO
            self.write(cr, uid, new_order, {    'customer': customer_name,
                                                'customer_delivery': delivery_name,
                                                'product_description': desc_name,
                                                'origin': origin_name,
                                                'transport_id': transport_id,
                                            })
            
#            #v nov PO moram zapisat tudi id prevoza - lahko ga vzamem kar iz prvega PO, ker morajo biti vsi enaki
#            transport_id_old = self.pool.get('purchase.order').read(cr, uid, ids[0], ['transport_id'])
#            
#            #dobim dict: {'transport_id': (3, u'Prevoz 2012.11.07'), 'id': 15}
#            #transport_id_old['transport_id'][0] - po dict se z transport_id_old postavim na tuple, z ineksom na vrednost
#            if transport_id_old['transport_id']:
#                self.write(cr, uid, new_order, {'transport_id': transport_id_old['transport_id'][0]})
                
            #ce smo move_dest spremenili, potem ga popravim nazaj
            for dict_key in dict_move_dest:
                if dict_move_dest[dict_key]['changed']:
                    old_id = dict_key
                    order_lines_obj.write(cr, uid, [old_id], {'move_dest_id':None})
                    
                    
        return allorders
                 
purchase_order()

class purchase_order_line(osv.osv):
    _inherit = "purchase.order.line"
    _columns = {
        'customer_id': fields.many2one('res.partner', 'Customer'),
        'customer_delivery_id': fields.many2one('res.partner', 'Delivery address'),
        'sale_price': fields.float('Sale Price', digits_compute= dp.get_precision('Sale Price')),
        'extra_dimensions': fields.char('Extra dimensions', size=128),
    }
    
purchase_order_line()

class purchase_order_group(osv.osv_memory):
    _inherit = "purchase.order.group"
    
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = super(purchase_order_group, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar,submenu=False)
        
        if context is None:
            context={}
            
        #Iz ids bom prebral transport in preveril ali je za vse izrane enak
        purchase_order_obj = self.pool.get('purchase.order')
        
        transport_obj = purchase_order_obj.read(cr, uid, context['active_ids'], ['transport_id'])
        #dobim listo dictionaries
        #jo razbijem po linijah, dobim posamezni dictionary
        #po ključu transport_id dobim tuple, tem primeru {id, naziv_prevoza}
        tmp_transport_id = -1
        value = 0
        
        for line in transport_obj:
            #if not line['transport_id']:
                #raise osv.except_osv(_('Warning'), _('Please select all transports.'))
            
            if not line['transport_id']:
                value = 0
            else:
                value = line['transport_id'][0]
            
                
            if tmp_transport_id == -1:
                tmp_transport_id = value
            else:
                if (tmp_transport_id == 0 and value > 0) or (tmp_transport_id > 0 and value == 0):
                    raise osv.except_osv(_(' Warning!'), _('Cannot merge Purchase Orders while some of them have no transport defined.'))
                if tmp_transport_id != value:
                    raise osv.except_osv(_(' Warning!'), _('Cannot merge Purchase Orders with different transports.'))
            
        return res

purchase_order_group()
