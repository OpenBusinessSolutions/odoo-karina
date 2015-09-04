# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Mentis d.o.o.
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
#import openerp.addons.decimal_precision as dp

class delivery_order_confirm(osv.osv_memory):
    _name = "delivery.order.confirm"
    _description = "Confirm Delivery Orders"
    
    def _get_status(self, cr, uid, context):
        return self.pool.get('bakery.process').process_running(cr, uid, '40', context=None)
    
    _columns = {
        'status': fields.char('Status', size=128, readonly=True),
        'override': fields.boolean('Override running process', help='Run the process, even if there is another one running'),
    }
    _defaults = {
        'status': _get_status,
    }
    
    def confirm_delivery_orders(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        
        sale_override = False
        #for self_line in self.browse(cr,uid,ids):
        #    sale_override = self_line.override
        
        #sale_override = self.browse(cr,uid,ids)[0].override
        move_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking')
        
        #Preverimo ali je proces aktiven in bil zacet vceraj
        production_id, production_status = self.pool.get('bakery.production').production_running(cr, uid, '40')
        if production_status: #obstaja, pa ni bil zacet vceraj
            raise osv.except_osv(_('Warning!'),production_status)
        if production_id == []: #se ne obstaja aktiven zapis
            raise osv.except_osv(_('Warning!'),_('Production has not been started yet!'))
        else:
            production_id = production_id[0]

        process_status = self.pool.get('bakery.process').process_running(cr, uid, '40')
        if not sale_override and process_status:
            raise osv.except_osv(_('Warning!'),process_status)
        else:
            process_id = self.pool.get('bakery.process').process_start(cr, uid, '40')
        cr.commit()
        #-------------------------------------------------------------------------------------------------------
        
        
        #5. Popravimo kolicine na STOCK.MOVE
        move_ids = move_obj.search(cr, uid, [('type', '=', 'out'),
                                             ('basket_status', 'in', ['0','1']),
                                             ('location_id', '=', 12)])
        for move in move_obj.browse(cr, uid, move_ids):
            move_obj.write(cr, uid, [move.id], {'product_qty': (move.basket_deliverd - move.product_qty_returned),
                                                'product_uos_qty': (move.basket_deliverd - move.product_qty_returned)})
                

        #7. Na teh nalogih naredimo potem se prevzem
        picking_ids = picking_obj.search(cr, uid, [('type', '=', 'out'),
                                                   ('state', 'in', ['confirmed','assigned']),
                                                   ('sale_id.shop_id', '=', 1)])
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' - Proizvodnja - zakljucevanje dobavnic: ')
        st_naloga = 1
        date_done = time.strftime('%Y-%m-%d')
        for picking in picking_obj.browse(cr, uid, picking_ids):
            #Na pickingu preko sale_orderja najdemo ali je na linijah produkt brez product_id
            sale_line_ids = self.pool.get('sale.order.line').search(cr, uid, [('order_id', '=', picking.sale_id.id),
                                                                          ('product_id', '=', False),
                                                                        ])
            #Iz njega najdemo originalni produkt in ga zapisemo na stock.move
            for sale_line in self.pool.get('sale.order.line').browse(cr, uid, sale_line_ids):
                original_code = sale_line.name[sale_line.name.find("[")+1:sale_line.name.find("]")]
                product_ids = self.pool.get('product.product').search(cr, uid, [('default_code', '=', original_code)])
                
                if product_ids:
                    move_vals = {}
                    move_vals['picking_id'] = picking.id
                    move_vals['product_id'] = product_ids[0]
                    move_vals['partner_id'] = picking.partner_id.id
                    move_vals['product_qty'] = 0 - sale_line.product_qty_returned
                    move_vals['product_uom'] = sale_line.product_uom.id
                    move_vals['product_uos_qty'] = 0 - sale_line.product_qty_returned
                    move_vals['product_uos'] = sale_line.product_uos.id
                    move_vals['price_unit'] = sale_line.price_unit
                    move_vals['location_id'] = sale_line.order_id.shop_id.warehouse_id.lot_input_id.id
                    move_vals['name'] = sale_line.name
                    move_vals['location_dest_id'] = sale_line.order_id.shop_id.warehouse_id.lot_output_id.id
                    move_vals['sale_line_id'] = sale_line.id
                    move_vals['product_qty_returned'] = sale_line.product_qty_returned
                    
                    create_id = move_obj.create(cr, uid, move_vals, context)
                    move_obj.write(cr, uid, create_id, {'basket_status':1})
                    
            #Sedaj si pripravim objekt ki ga posljem v zakljucevanje dobavnic
            #Se sprehodimo skozi stock.move-e
            deliver_dict = {}
            new_move_ids = self.pool.get('stock.move').search(cr, uid, [('picking_id', '=', picking.id)])
            for new_move_line in self.pool.get('stock.move').browse(cr, uid, new_move_ids):
            #for line in picking.move_lines:
                temp_dict = {}
                temp_dict['prodlot_id'] = new_move_line.prodlot_id.id
                temp_dict['product_id'] = new_move_line.product_id.id
                temp_dict['product_uom'] = new_move_line.product_uom.id
                temp_dict['product_qty'] = new_move_line.product_qty
                key_name = 'move' + str(new_move_line.id)
                deliver_dict[key_name] = temp_dict
            #Dodamo se datum dobave in poklicemo funkcijo do_partial
            deliver_dict['delivery_date'] = date_done
            picking_obj.do_partial(cr, uid, [picking.id], deliver_dict, context=context)
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' - Zakljucena dobavnica: ' + str(st_naloga))
            st_naloga = st_naloga + 1
            cr.commit()
        
        #Se enkrat poiscem stock_move-e + kjer je product_qty_returned > 0
        move_ids = move_obj.search(cr, uid, [('type', '=', 'out'),
                                             ('basket_status', 'in', ['0','1']),
                                             ('location_id', '=', 12),
                                             ('product_qty_returned', '>', 0)])
        move_obj.create_return_move(cr, uid, move_ids)
        
            
        #8. Vsem, ki nimajo statusa 4 ga dodelimo
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' - Proizvodnja - dodelimo statuse')
        move_all_ids = move_obj.search(cr, uid, [('basket_status', 'in', ['0','1'])])
        move_obj.write(cr, uid, move_all_ids, {'basket_status': 4})
        
        self.pool.get('bakery.process').process_end(cr, uid, '40', process_id, production_id)
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' - KONEC')
        return {
                'type': 'ir.actions.act_window_close',
        }
    
delivery_order_confirm()

