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

class stock_partial_picking(osv.osv_memory):
    _inherit = "stock.partial.picking"
    
    def get_backorder(self, cr, uid, active_ids, picking_obj, context=None):
        res = []
        for pick in picking_obj.browse(cr, uid, active_ids, context=context):
            if pick.backorder_id:
                res_sub = self.get_backorder(cr, uid, [pick.backorder_id.id], picking_obj, context)
                for sub in res_sub:
                    res.append(sub)
            
            res.append(active_ids[0])
        return res
        
    
    def do_partial(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        list_move_ids = [] #shranimo id-je stock.move, ker se lahko po SUPER metodi spremenijo, ce nek produkt prevzames do konca
        
        picking_obj = self.pool.get('stock.picking')
        move_obj = self.pool.get('stock.move')
        active_ids = context.get('active_ids')
            
        if context.get('active_model') == 'stock.picking.in':                      
            for pick in picking_obj.browse(cr, uid, active_ids, context=context):
                for move in pick.move_lines:
                    list_move_ids.append(move.id)
            
        res = super(stock_partial_picking,self).do_partial(cr, uid, ids, context)

        # =====================================================
        #Rekurzijo - dobimo vse picking IDS in po delnih prevzemih sestavimo skupno vsoto
        res_ids = self.get_backorder(cr, uid, active_ids, picking_obj, context)
        dict_vsota = {}
        for pick in picking_obj.browse(cr, uid, res_ids, context=context):
            for move in pick.move_lines:    
                if move.state == 'done': #original ne smemo racunat zraven, ker je not zapisan ostanek delnega prevzema
                    #sestevamo po purchase_line_id, da na koncu vemo h katerem stock.move zapisat vsoto
                    if not move.purchase_line_id.id in dict_vsota:
                        dict_vsota[move.purchase_line_id.id] = move.product_qty
                    else:
                        dict_vsota[move.purchase_line_id.id] += move.product_qty
                
                
        if context.get('active_model') == 'stock.picking.in':                      
            for move in move_obj.browse(cr, uid, list_move_ids, context=context): #list_move_ids - vrednosti pred SUPER funkcijo, ker ce en produkt prevzamers do konca picking_id na movu spremeni
                #v slovarju imamo zapisane purchase_line_id-je in njihove vsote
                tmp_id = move.purchase_line_id.id
                if tmp_id in dict_vsota:
                    vsota = dict_vsota[tmp_id]
                else:
                    vsota = 0
                    
                if move.move_dest_id:
                    orig_line_id = move.move_dest_id.id
                    move_obj.write(cr, uid, orig_line_id, {'product_qty':vsota, 'product_uos_qty':vsota})
        # =====================================================                
        return res
stock_partial_picking()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwi
