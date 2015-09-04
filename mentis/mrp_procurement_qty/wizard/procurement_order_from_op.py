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
from openerp import pooler
from datetime import datetime
import time
from tools.translate import _

class procurement_order_run_wizard(osv.osv_memory):
    _name = "procurement.order.orderpoint.run.wizard"
    _description = "Run Procurement scheduler from orderpoint multiple times"
    
    def _get_status(self, cr, uid, context):
        return self.pool.get('bakery.process').process_running(cr, uid, '30', context=None)
    
    _columns = {
        'repeat_number': fields.integer('Repeat Number'),
        'status': fields.char('Status', size=128, readonly=True),
        'override': fields.boolean('Override running process', help='Run the process, even if there is another one running'),
    }
    _defaults = {
        'repeat_number': lambda *a: 0,
        'status': _get_status,
    }
                
    def _group_manufacturing_orders(self, cr, uid, context=None):
        
        man_order_obj = self.pool.get('mrp.production')
        picking_obj = self.pool.get('stock.picking')
        procurement_obj = self.pool.get('procurement.order')
        mrp_obj = self.pool.get('mrp.procurement.qty')
        stock_move_obj = self.pool.get('stock.move')
        
        ready_ids = man_order_obj.search(cr, uid, [
                                                   ('state', 'in', ['ready', 'confirmed', 'in_production']),
                                                   ('status_izdelki', '=', 3),
                                                   ], order='product_id')
        
        qty_produced = 0
        qty_scrap = 0
        qty_scrap_phantom = 0
        qty_product_qty = 0
        qty_produced_stock = 0 
        qty_produced_phantom = 0
        PR_ID = -1
        OR_ID = -1
        
        for order in man_order_obj.browse(cr, uid, ready_ids):
            if order.product_id != PR_ID:
                qty_produced = order.produced
                qty_scrap = order.scrap
                qty_scrap_phantom = order.scrap_phantom
                qty_product_qty = order.product_qty
                qty_produced_stock = order.produced_stock
                qty_produced_phantom = order.produced_phantom
                PR_ID = order.product_id
                OR_ID = order.id
            else: #produkt na liniji je enak kot na zgornji -> sestejemo vrednosti
                qty_produced = qty_produced + order.produced
                qty_scrap = qty_scrap + order.scrap
                qty_scrap_phantom = qty_scrap_phantom + order.scrap_phantom
                qty_product_qty = qty_product_qty + order.product_qty
                qty_produced_stock = qty_produced_stock + order.produced_stock
                qty_produced_phantom = qty_produced_phantom + order.produced_phantom
                
                #Spremenimo kolicino na D.N.
                mrp_obj.change_prod_qty(cr, uid, OR_ID, qty_product_qty, context)
                
                #vrednosti zapisemo na prvi D.N. s tem produktom
                man_order_obj.write(cr, uid, [OR_ID],
                                    {'scrap':qty_scrap,
                                     'produced':qty_produced,
                                     'scrap_phantom':qty_scrap_phantom,
                                     #'product_qty':qty_product_qty,
                                     'produced_stock':qty_produced_stock,
                                     'produced_phantom':qty_produced_phantom,
                                     'status_izdelki':0,
                                     'status_testo':0,
                                     })
                
                picking_obj.action_cancel(cr, uid, [order.picking_id.id], context) #najprej preklicemo picking
                man_order_obj.action_cancel(cr, uid, [order.id], context) #nato preklicemo manufacturing order
                stock_move_obj.action_cancel(cr, uid, [order.move_prod_id.id], context) #preklicemo se stock move
                #Preklicemo procurement_order
                procurement_id = procurement_obj.search(cr, uid, [('production_id', '=', order.id)])
                procurement_obj.action_cancel(cr, uid, procurement_id)
            
        return 0
    
    
    def execute_op(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        sale_override = self.browse(cr,uid,ids)[0].override
        proc_obj = self.pool.get('procurement.order')
#        proc_jour_obj = self.pool.get('procurement.order.journal')
        
        #Preverimo ali obstaja aktiven zapis in nezakljucene dobavnice----------------------------------------
        production_id, production_status = self.pool.get('bakery.production').production_running(cr, uid, '30')
        if production_status: #dobavnice so ze potrjene
            raise osv.except_osv(_('Warning!'),production_status)
        if production_id == []: #se ne obstaja aktiven zapis
            raise osv.except_osv(_('Warning!'),_('Sale orders have today not been confirmed yet!'))
        else:
            production_id = production_id[0]
            
        #Preverimo je lansiranje ze zagnano
        process_status = self.pool.get('bakery.process').process_running(cr, uid, '30')
        if not sale_override and  process_status:
            raise osv.except_osv('Warning!',process_status)
        else:
            process_id = self.pool.get('bakery.process').process_start(cr, uid, '30')
        #------------------------------------------------------------------------------------------------------
        #Nastavimo da zacasna lokacija zaloge ni aktivna
        ir_config_parameter = self.pool.get('ir.config_parameter')
        ir_config_parameter.set_param(cr, uid, 'stock.empty_location_active', '0')

        
        #Ce je stevilo ponovitev != 0 potem tolikokrat, drugace 4x
        repeat_number = self.browse(cr,uid,ids)[0].repeat_number
        if repeat_number == 0:
            repeat_number = 4
        elif repeat_number == -1:
            repeat_number = 0
        
        
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' - Start from OP')
        
        cr.commit()
        use_new_cursor = cr.dbname
        for x in range(0, repeat_number):
            try:
                #proc_obj.run_scheduler(new_cr, uid, automatic=False, use_new_cursor=new_cr.dbname, context=context)
                produrement_ids = proc_obj.search(cr, uid, [('state', '=', 'confirmed'),
                                                            ('procure_method', '=', 'make_to_stock')])
                proc_obj._procure_confirm(cr, uid, ids=produrement_ids, use_new_cursor=use_new_cursor, context=context)
                proc_obj._procure_orderpoint_confirm(cr, uid, automatic=False, use_new_cursor=use_new_cursor, context=context)
                
                self.pool.get('bakery.process').write(cr, uid, [process_id], {'misc':str(x+1)})
                cr.commit()
                    
            except Exception, e:
                self.pool.get('bakery.process').write(cr, uid, [process_id], {'error':str(e)})
                cr.commit()
                raise osv.except_osv('Opozorilo!', u'Napaka lansiranja iz OP v %s. krogu. Err: %s' % (str(x), str(e)))
                return{}
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' - Close: ' + str(x+1))
        #------------------------------------------------------------------------------------------------------------------------
        cr.commit() #Da si nalozimo sprememb    
        self._group_manufacturing_orders(cr, uid, context)
        #raise osv.except_osv('Opozorilo!', 'Napaka pri zdruzevanju d.n.:' + str(e))
        #-------------------------------------------------------------------------------------------
        _sql_string1 = """update mrp_production
                            SET status_testo = 0, status_izdelki = 0, created_from_op = True
                            WHERE status_testo = 3 or status_izdelki = 3;"""
        cr.execute(_sql_string1)
        cr.commit()
        #raise osv.except_osv('Opozorilo!', 'Napaka pri zagonu query-ja: status_testo; ' +str(e))

        _sql_string2 = """update stock_move
                            SET basket_status = 2
                            WHERE basket_status = 3 AND state = 'done';"""
        cr.execute(_sql_string2)
        cr.commit()
        #raise osv.except_osv('Opozorilo!', 'Napaka pri zagonu query-ja: basket_status_2_done; ' +str(e))
        
        _sql_string3 = """update stock_move
                            SET basket_status = 0
                            WHERE basket_status = 3;"""
        cr.execute(_sql_string3)
        cr.commit()
        #raise osv.except_osv('Opozorilo!', 'Napaka pri zagonu query-ja: basket_status_0; ' +str(e))

        _sql_string4 = """update stock_move upd 
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
        cr.execute(_sql_string4)
        cr.commit()
        #raise osv.except_osv('Opozorilo!', 'Napaka pri zagonu query-ja: basket_status2; ' +str(e))
        
        self.pool.get('stock.move').get_qty_delivery_available(cr, uid)
        #raise osv.except_osv('Opozorilo!', 'Napaka pri zagonu query-ja delivery_available' + str(e))
        
        self.pool.get('bakery.process').process_end(cr, uid, '30', process_id, production_id)
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' - KONEC Lansiranja')
        return{}
        
procurement_order_run_wizard()

