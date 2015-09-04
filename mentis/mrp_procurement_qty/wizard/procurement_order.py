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
from openerp import pooler
from datetime import datetime
import time
from tools.translate import _
from openerp.tools.safe_eval import safe_eval

class procurement_order_run_wizard(osv.osv_memory):
    _name = "procurement.order.run.wizard"
    _description = "Run Procurement scheduler multiple times"
    
    def _get_status(self, cr, uid, context):
        return self.pool.get('bakery.process').process_running(cr, uid, '20', context=None)
    
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
    
    
    def execute(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        sale_override = self.browse(cr,uid,ids)[0].override
        proc_obj = self.pool.get('procurement.order')
        
        #Preverimo ali obstaja aktiven zapis in nezakljucene dobavnice----------------------------------------
        production_id, production_status = self.pool.get('bakery.production').production_running(cr, uid, '20')
        if production_status: #dobavnice so ze potrjene
            raise osv.except_osv(_('Warning!'),production_status)
        if production_id == []: #se ne obstaja aktiven zapis
            raise osv.except_osv(_('Warning!'),_('Sale orders have today not been confirmed yet!'))
        else:
            production_id = production_id[0]
            
        #Preverimo ce je lansiranje ze zagnano
        process_status = self.pool.get('bakery.process').process_running(cr, uid, '20')
        if not sale_override and process_status:
            raise osv.except_osv(_('Warning!'),process_status)
        else:
            process_id = self.pool.get('bakery.process').process_start(cr, uid, '20')
        #------------------------------------------------------------------------------------------------------
        
        
        ir_config_parameter = self.pool.get('ir.config_parameter')
        ir_config_parameter.set_param(cr, uid, 'stock.empty_location_active', '1')
        empty_location_id = safe_eval(ir_config_parameter.get_param(cr, uid, 'stock.empty_location', 'False'))
        proc_uid = safe_eval(ir_config_parameter.get_param(cr, uid, 'res.users.process_uid', 'False'))
        if not proc_uid:
            proc_uid = uid
            
        
        #Ce je stevilo ponovitev != 0 potem tolikokrat, drugace 4x
        repeat_number = self.browse(cr,uid,ids)[0].repeat_number
        if repeat_number == 0:
            repeat_number = 4
        elif repeat_number == -1:
            repeat_number = 0
        
        cr.commit()
        new_cr = pooler.get_db(cr.dbname).cursor()
        use_new_cursor = new_cr.dbname
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' - Start')
        err = 0
        for x in range(0, repeat_number):
            try:
                err = 0
                produrement_ids = proc_obj.search(new_cr, uid, [('state', '=', 'confirmed'),
                                                            ('procure_method', '=', 'make_to_stock')])
                err = 1
                proc_obj._procure_confirm(new_cr, proc_uid, ids=produrement_ids, use_new_cursor=use_new_cursor, context=context)
                err = 2
                proc_obj._procure_orderpoint_confirm(new_cr, proc_uid, automatic=False, use_new_cursor=use_new_cursor, context=context)
                err = 3
                self.pool.get('bakery.process').write(new_cr, uid, [process_id], {'misc':str(x+1)})
                err = 4
                new_cr.commit() 
            except Exception, e:
                new_cr.rollback()
                new_cr.close()
                self.pool.get('bakery.process').write(cr, uid, [process_id], {'error':str(err)+'---'+str(e)})
                cr.commit()
                raise osv.except_osv('Opozorilo!', u'Napaka lansiranja v %s. krogu. Err: %s' % (str(x+1), str(err)+';'+str(e)))
                return{}
            print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' - Close: ' + str(x+1))
        #------------------------------------------------------------------------------------------------------------------------
        try:
            self._group_manufacturing_orders(new_cr, uid, context)
            new_cr.commit()
        except Exception, e:
            new_cr.rollback()
            new_cr.close()
            raise osv.except_osv('Opozorilo!', 'Napaka pri zdruzevanju d.n.:' + str(e))
            return{}
        new_cr.close()
        #-------------------------------------------------------------------------------------------
        
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' - KONEC Lansiranja')
        self.pool.get('bakery.process').process_end(cr, uid, '20', process_id, production_id)
        return{}
        
procurement_order_run_wizard()

