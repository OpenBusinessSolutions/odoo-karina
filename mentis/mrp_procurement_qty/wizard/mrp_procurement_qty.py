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
from tools.translate import _
from datetime import datetime
import time
import openerp.addons.decimal_precision as dp
from openerp.tools.safe_eval import safe_eval

class mrp_procurement_qty(osv.osv_memory):
    _name = "mrp.procurement.qty"
    _description = "Change product quantity on manufacturing orders"
    
    def _get_status(self, cr, uid, context):
        return self.pool.get('bakery.process').process_running(cr, uid, '50', context=None)
    
    _columns = {
        'status': fields.char('Status', size=128, readonly=True),
        'override': fields.boolean('Override running process', help='Run the process, even if there is another one running'),
    }
    
    _defaults = {
        'status': _get_status,
    }
    
    def _update_product_to_produce(self, cr, uid, prod, qty, context=None):
        move_lines_obj = self.pool.get('stock.move')
        for m in prod.move_created_ids:
            move_lines_obj.write(cr, uid, [m.id], {'product_qty': qty})
            
    def change_prod_qty(self, cr, uid, order_id, prod_qty, context=None):

        prod_obj = self.pool.get('mrp.production')
        bom_obj = self.pool.get('mrp.bom')
        move_obj = self.pool.get('stock.move')

        prod = prod_obj.browse(cr, uid, order_id, context=context)
        prod_obj.write(cr, uid, [prod.id], {'product_qty': prod_qty})
        prod_obj.action_compute(cr, uid, [prod.id])

        for move in prod.move_lines:
            bom_point = prod.bom_id
            bom_id = prod.bom_id.id
            if not bom_point:
                bom_id = bom_obj._bom_find(cr, uid, prod.product_id.id, prod.product_uom.id)
                if not bom_id:
                    raise osv.except_osv(_('Error!'), _("Cannot find bill of material for this product."))
                prod_obj.write(cr, uid, [prod.id], {'bom_id': bom_id})
                bom_point = bom_obj.browse(cr, uid, [bom_id])[0]

            if not bom_id:
                raise osv.except_osv(_('Error!'), _("Cannot find bill of material for this product."))

            factor = prod.product_qty * prod.product_uom.factor / bom_point.product_uom.factor
            product_details, workcenter_details = \
                bom_obj._bom_explode(cr, uid, bom_point, factor / bom_point.product_qty, [])
            product_move = dict((mv.product_id.id, mv.id) for mv in prod.picking_id.move_lines)
            for r in product_details:
                if r['product_id'] == move.product_id.id:
                    move_obj.write(cr, uid, [move.id], {'product_qty': r['product_qty']})
                if r['product_id'] in product_move:
                    move_obj.write(cr, uid, [product_move[r['product_id']]], {'product_qty': r['product_qty']})
        if prod.move_prod_id:
            move_obj.write(cr, uid, [prod.move_prod_id.id], {'product_qty' : prod_qty})
        self._update_product_to_produce(cr, uid, prod, prod_qty, context=context)
        
        return {}
    
    def _get_product_category_parent_id(self, cr, uid, prod_id, context=None):
        product_obj = self.pool.get('product.template')
        category_obj = self.pool.get('product.category')
        
        _prod = product_obj.browse(cr, uid, prod_id)
        _categ = category_obj.browse(cr, uid, _prod.categ_id.id)
        
        return _categ.parent_id.id
    
    def _product_cost_calculation(self, cr, uid, ids, context=None):
        _production_ids = self.pool.get('mrp.production').browse(cr, uid, ids, context=None)
        for _production_id in _production_ids:
            _name = _production_id.name
            _product_id = _production_id.product_id.id
            
            product_obj=self.pool.get('product.product')
            accounts = product_obj.get_product_accounts(cr, uid, _product_id, context)
            
            if _production_id.product_id.cost_method == 'average' and accounts['stock_account_input'] and accounts['property_stock_valuation_account_id']:
                _debit= 0.00
                _credit = 0.00
                _move_line_ids = self.pool.get('account.move.line').search(cr, uid, [('name','=',_name),
                                                                                     ('product_id','!=',_product_id)])
                _move_lines = self.pool.get('account.move.line').browse(cr, uid, _move_line_ids, context=None)
                for _move_line in _move_lines:
                    _debit += _move_line.debit
                    _credit += _move_line.credit
                
                _move_line_ids = self.pool.get('account.move.line').search(cr, uid, [('name','=',_name),
                                                                                     ('product_id','=',_product_id)], order='id')
                _move_lines = self.pool.get('account.move.line').browse(cr, uid, _move_line_ids, context=None)

                for _move_line in _move_lines:
                    if _move_line.account_id.id == accounts['stock_account_input']:
                        _move_line.write({'credit': _credit}, context)
                    elif _move_line.account_id.id == accounts['property_stock_valuation_account_id']:
                        _move_line.write({'debit': _debit}, context)
                if _debit and _debit != 0.00:
                    _old_inventory_qty = _production_id.product_id.qty_available or 0.00
                    _old_inventory_value = _old_inventory_qty * _production_id.product_id.standard_price
                    _new_inventory_value = _production_id.product_qty * _debit
                    _new_inventory_qty = _old_inventory_qty + _production_id.product_qty
                    if _new_inventory_qty and _new_inventory_qty != 0.00:
                        _new_standard_price = (_old_inventory_value + _new_inventory_value) / _new_inventory_qty
                    elif _production_id.product_qty and _product_id.product_qty != 0.00:
                        _new_standard_price = _debit / _production_id.product_qty
                    else:
                        _new_standard_price = _debit                        
                    product_obj.write(cr, uid, [_product_id], {'standard_price': _new_standard_price}, context)
    
    def execute(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
            
        new_qty = 0
        sale_override = self.browse(cr,uid,ids)[0].override
        man_order_obj = self.pool.get('mrp.production')
        move_obj = self.pool.get('stock.move')
        picking_obj = self.pool.get('stock.picking')
        
#        proc_jour_obj = self.pool.get('procurement.order.journal')
#        proc_jour_ids = proc_jour_obj.search(cr, uid, [('state', '=' , True)]) #tabela za zapis statusa procurementa in zakljucevanja
        
        #Preverimo ali je proces aktiven in ce so bile dobavnice zakljucene
        production_id, production_status = self.pool.get('bakery.production').production_running(cr, uid, '50')
        if production_status: #obstaja, pa ni bil zacet vceraj
            raise osv.except_osv('Warning!',production_status)
        if production_id == []: #se ne obstaja aktiven zapis
            raise osv.except_osv('Warning!','Production has not been started yet!')
        else:
            production_id = production_id[0]

        process_status = self.pool.get('bakery.process').process_running(cr, uid, '50')
        if not sale_override and process_status:
            raise osv.except_osv('Warning!',process_status)
        else:
            process_id = self.pool.get('bakery.process').process_start(cr, uid, '50')
        cr.commit()
        #-------------------------------------------------------------------------------------------------------
        
        
        ir_config_parameter = self.pool.get('ir.config_parameter')
        return_location_id = safe_eval(ir_config_parameter.get_param(cr, uid, 'stock.return_location', 'False'))
        
        print('Zakljucevanje proizvodnje - zacetek delovnih nalogov')
        st_naloga = 1
        commit_error = False
        
        for x in range(0, 3):
            commit_error = False
            ready_ids = man_order_obj.search(cr, uid, [('state', 'in', ['ready', 'confirmed','in_production'])], order='id DESC')
            for mrp_order in man_order_obj.browse(cr, uid, ready_ids):
                #0. Preverimo ali je bil delovni nalog sploh narejen/izveden - ce ne ga preklicemo
                if mrp_order.produced == 0 and mrp_order.scrap == 0 and mrp_order.produced_phantom == 0:
                    if mrp_order.picking_id.id:
                        picking_obj.action_cancel(cr, uid, [mrp_order.picking_id.id], context) #najprej preklicemo picking
                    man_order_obj.action_cancel(cr, uid, [mrp_order.id], context) #nato preklicemo manufacturing order
                    if mrp_order.move_prod_id.id:
                        move_obj.action_cancel(cr, uid, [mrp_order.move_prod_id.id], context) #preklicemo se stock move
                    #Preklicemo procurement_order
                    procurement_id = self.pool.get('procurement.order').search(cr, uid, [('production_id', '=', mrp_order.id)])
                    self.pool.get('procurement.order').action_cancel(cr, uid, procurement_id)
                        
                else:
                    #1. Spremenimo kolicino
                    if mrp_order.product_id.product_tmpl_id.categ_id.parent_id.id == 38: #if order['parent_id'] == 38: #Izdelki
                        new_qty = mrp_order.produced
                        if (mrp_order.product_qty != new_qty):
                            self.change_prod_qty(cr, uid, mrp_order.id, new_qty, context)
                    else: #Polizdelki
                        new_qty = mrp_order.produced_phantom
                        if new_qty == 0:
                            new_qty = 1
                        if (mrp_order.product_qty != new_qty):
                            self.change_prod_qty(cr, uid, mrp_order.id, new_qty, context)
            
                    #2. Izvedemo narocilo/proizvodnjo 
                    exec_mode = 'consume_produce'
                    man_order_obj.action_produce(cr, uid, mrp_order.id, new_qty, exec_mode, context=context)
                    
                    #2.1 Na stock.move popravimo vrednost qty za polizdelek, ker ga je lahko bilo narejeno vec - dal je vec testa v izdelavo 
                    if mrp_order.product_id.product_tmpl_id.categ_id.parent_id.id != 38:
                        move_ids = move_obj.search(cr, uid, (
                                                             ['production_id', '=', mrp_order.id],
                                                             ['location_dest_id', '=', mrp_order.location_dest_id.id],
                                                            ))
                        move_obj.write(cr, uid, move_ids, {'product_qty': mrp_order.produced})
                        
                    
                    #3. SCRAP; Ce je produkt izdelek se izracuna kot razlika med narejenimi in danimi v košare + scrap pri izdelavi
                    #drugace pa samo kolko je blo v resnici odpada pri izdelavi
                    new_scrap = mrp_order.scrap
                    if mrp_order.product_id.product_tmpl_id.categ_id.parent_id.id == 38: #Izdelki
                        #3.1 Dobimo kolicine dane v kosare, da lahko dodamo scrapu
                        move_ids = move_obj.search(cr, uid, (
                                                     ['type', '=', 'out'],
                                                     ['basket_status', '=', 4],
                                                     ['product_id', '=', mrp_order.product_id.id]
                                                     ))
                        #Koliko smo jih naredili - spodaj koliko dali v kosare + pravi scrap - koliko v hladilnici
                        new_scrap = mrp_order.produced - mrp_order.produced_stock 
                        for move in move_obj.browse(cr, uid, move_ids):
                            new_scrap = new_scrap - move.basket_deliverd
                            
                        #Product pa je bil lahko uporabljen tudi v dodatni obdelavi, zato je potrebno odsteti koliko je bilo narejeno tega
                        manuf_ids = man_order_obj.search(cr, uid, [
                                                                   ('status_izdelki', 'in', ['0','1']), #('state', 'in', ['ready', 'confirmed']),
                                                                   ('product_with_bom_id', '=', mrp_order.product_id.id)
                                                                   ])
                        
                        for man_order in man_order_obj.browse(cr, uid, manuf_ids):
                            new_scrap = new_scrap - man_order.produced
                        
                    #3.2 Naredimo scrap ce je potreben
                    if new_scrap > 0:
                        move_id = move_obj.search(cr, uid, (
                                                            ['production_id', '=', mrp_order.id],
                                                            ['location_dest_id', '=', mrp_order.location_dest_id.id]
                                                            ))
                        move_obj.action_scrap(cr, uid, move_id, new_scrap, return_location_id)
                        
                print('Zakljucen nalog: ' + str(st_naloga))
                st_naloga = st_naloga + 1
                try:
                    cr.commit()
                except Exception, e:
                    commit_error = True
            
            if not commit_error: #ce ni prislo do napake ne ponavljamo zanke
                break
        
        #4.5 Ker ne smem prej popravljat status testo naredim to sedaj
        if not commit_error:
            status_ids = man_order_obj.search(cr, uid, [('status_izdelki', '!=', 2)])
            man_order_obj.write(cr, uid, status_ids, {'status_izdelki': 2, 'status_testo': 2})
            
            move_all_ids = move_obj.search(cr, uid, [('basket_status', '=', 4)])
            move_obj.write(cr, uid, move_all_ids, {'basket_status': 2})
            cr.commit()
        
        self.pool.get('bakery.process').process_end(cr, uid, '50', process_id, production_id)
        return {
                'type': 'ir.actions.act_window_close',
        }
    
mrp_procurement_qty()

