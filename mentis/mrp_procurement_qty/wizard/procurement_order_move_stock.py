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
#from openerp import pooler
#from datetime import datetime
#import time
from tools.translate import _
from openerp.tools.safe_eval import safe_eval

class procurement_order_move_stock_wizard(osv.osv_memory):
    _name = "procurement.order.move.stock.wizard"
    _description = "Move stock and order points"
    
    def _get_status_move(self, cr, uid, context):
        return self.pool.get('bakery.production').is_stock_moved(cr, uid, '60', context=None)
    
    def _get_status(self, cr, uid, context):
        return self.pool.get('bakery.process').process_running(cr, uid, '60', context=None)
    
    _columns = {
        'status_move': fields.boolean('Stock moved', readonly=True),        
        'status': fields.char('Running status', size=128, readonly=True),
        'override': fields.boolean('Override running process', help='Run the process, even if there is another one running'),
    }
    _defaults = {
        'status_move': _get_status_move,
        'status': _get_status,
    }
                
        
    def execute(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        sale_override = self.browse(cr,uid,ids)[0].override
        
        #Preverimo ali obstaja aktiven zapis ------------------------------------------------------------------
        production_id, production_status = self.pool.get('bakery.production').production_running(cr, uid, '60')
        if production_status: #dobavnice so ze potrjene
            raise osv.except_osv(_('Warning!'),production_status)
        if production_id == []: #se ne obstaja aktiven zapis
            raise osv.except_osv(_('Warning!'),_('Sale orders have today not been confirmed yet!'))
        else:
            production_id = production_id[0]
            
        #Preverimo je lansiranje ze zagnano
        process_status = self.pool.get('bakery.process').process_running(cr, uid, '60')
        if not sale_override and process_status:
            raise osv.except_osv(_('Warning!'),process_status)
        else:
            process_id = self.pool.get('bakery.process').process_start(cr, uid, '60')
        cr.commit()
        #------------------------------------------------------------------------------------------------------
        
        ir_config_parameter = self.pool.get('ir.config_parameter')
        empty_location_id = safe_eval(ir_config_parameter.get_param(cr, uid, 'stock.empty_location', 'False'))
        
        stock_moved =  self.pool.get('bakery.production').is_stock_moved(cr, uid, '60', context=None)
        if not stock_moved:
            #1. Najdemo tocke narocanja in jih umaknemo za navadno lansiranje
            orderpoint_ids = self.pool.get('stock.warehouse.orderpoint').search(cr, uid, [('product_id.product_tmpl_id.categ_id.id','!=', 4),
                                                                                          ('product_id.product_tmpl_id.categ_id.parent_id.id','!=', 4),
                                                                                          ('product_min_qty','>',0)
                                                                                          ])
            for orderpoint in self.pool.get('stock.warehouse.orderpoint').browse(cr, uid, orderpoint_ids):
                self.pool.get('stock.warehouse.orderpoint').write(cr, uid, [orderpoint.id], 
                                                                  {'temp_min_qty':orderpoint.product_min_qty,
                                                                   'temp_max_qty':orderpoint.product_max_qty,
                                                                   'product_min_qty':0,
                                                                   'product_max_qty':0,
                                                                   })
        
            #2. Premaknemo zalogo na zacasno lokacijo
            
        
            _sql_string0 = """UPDATE stock_move sm
                                SET 
                                location_id = 
                                        case 
                                        when location_id = 12 then """ + str(empty_location_id) + """ 
                                        else location_id
                                        end,
                                location_dest_id = 
                                        case 
                                        when location_dest_id = 12 then """ + str(empty_location_id) + """
                                        else location_dest_id
                                        end     
                                where 
                                (
                                        sm.location_id = 12 or location_dest_id = 12
                                )
                                and
                                (
                                        select 1 from product_template pt
                                        inner join product_category pc on
                                        pc.id = pt.categ_id and 
                                        pc.parent_id in(34, 38)
                                        where pt.id = sm.product_id
                                ) = 1 and sm.state = 'done' """
            cr.execute(_sql_string0)
            
        else:
            orderpoint_ids = self.pool.get('stock.warehouse.orderpoint').search(cr, uid, [('product_id.product_tmpl_id.categ_id.id','!=', 4),
                                                                                          ('product_id.product_tmpl_id.categ_id.parent_id.id','!=', 4),
                                                                                          ('temp_min_qty','>',0)
                                                                                          ])
            for orderpoint in self.pool.get('stock.warehouse.orderpoint').browse(cr, uid, orderpoint_ids):
                self.pool.get('stock.warehouse.orderpoint').write(cr, uid, [orderpoint.id], 
                                                                  {'product_min_qty':orderpoint.temp_min_qty,
                                                                   'product_max_qty':orderpoint.temp_max_qty,
                                                                   'temp_min_qty':0,
                                                                   'temp_max_qty':0,
                                                                   })
            
            _sql_string01 = """UPDATE stock_move
                                SET 
                                location_id = 
                                        case 
                                        when location_id = """ + str(empty_location_id) + """ then 12 
                                        else location_id
                                        end,
                                location_dest_id = 
                                        case 
                                        when location_dest_id = """ + str(empty_location_id) + """ then 12 
                                        else location_dest_id
                                        end     
                                where 
                                (
                                        location_id = """ + str(empty_location_id) + """ or location_dest_id = """ + str(empty_location_id) + """
                                )"""
        
        
            cr.execute(_sql_string01)
            #-------------------------------------------------------------------------------------------
        
            _sql_string1 = """update mrp_production
                            SET status_testo = 0, status_izdelki = 0
                            WHERE status_testo = 3 or status_izdelki = 3;"""
            cr.execute(_sql_string1)
            #-------------------------------------------------------------------------------------------

            _sql_string2 = """update stock_move
                                SET basket_status = 2
                                WHERE basket_status = 3 AND state = 'done';"""
        
            cr.execute(_sql_string2)
            #--------------------------------------------------------------------------------------------
        
            _sql_string2a = """update stock_move
                            SET basket_status = 0
                            WHERE basket_status = 3;"""
            cr.execute(_sql_string2a)
            #--------------------------------------------------------------------------------------------

            _sql_string3 = """update stock_move upd 
                                set basket_status = 2
                                where 
                                not upd.id in
                                (
                                
                                    select id from stock_move mov
                                    where mov.basket_status <> 2 and mov.location_id = 12
                                    and exists(
                                        select * from stock_picking pic 
                                        where
                                        pic.id = mov.picking_id and 
                                        pic.type = 'out'
                                    )

                                ) and basket_status != 2;"""
            cr.execute(_sql_string3)
            #--------------------------------------------------------------------------------------------
            self.pool.get('stock.move').get_qty_delivery_available(cr, uid)

        
        self.pool.get('bakery.process').process_end(cr, uid, '60', process_id, production_id)
        return{}
        
procurement_order_move_stock_wizard()

