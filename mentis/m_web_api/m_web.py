# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Mentis d.o.o. (<http://www.mentis.si>)
# 
#    This program is free software: you can redistribute it and/or
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public
#License
#    along with this program.  If not, see
#<http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields
from tools.translate import _

class product_template(osv.Model):
    _name = 'product.template'
    _inherit = 'product.template'
    _columns = {
        'dressing_ok': fields.boolean('Dodelava', help=""),
    }
    _defaults = {
        'dressing_ok': 0,
    }


class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'basket_number': fields.integer('Številka košare'),
        'vehicle': fields.selection([('1','Vozilo 1'), ('2','Vozilo 2'), ('3','Vozilo 3'), ('4','Vozilo 4')], 'Vozilo')
    }
    _defaults = {
        'vehicle': "1",
    }
res_partner()

class mrp_production(osv.osv):
    _inherit = 'mrp.production'
    _columns = {
        'product_cat': fields.related('product_id', 'categ_id', type='integer', string='Category'),
        'produced': fields.integer('Produced'),
        'scrap': fields.integer('Scrap'),
        'produced_stock': fields.integer('Produced_stock'),
        'produced_phantom': fields.integer('Produced_phantom'),
        'scrap_phantom': fields.integer('Scrap_phantom'),
        'status_testo': fields.integer('Status_testo'),
        'status_izdelki': fields.integer('Status_izdelki'),
        'dressing':fields.related('product_id','dressing_ok',type='boolean',string='Dodelava')
       
    }
    _defaults = {
        'produced': lambda *a: 0,
        'produced_stock': lambda *a: 0,
        'scrap': lambda *a: 0,
        'produced_phantom': lambda *a: 0,
        'scrap_phantom': lambda *a: 0,
        'status_testo': lambda *a: 3,
        'status_izdelki': lambda *a: 3,
    }
    
    def check_stock_moved(self, cr, uid, context=None):
        
        running_id = self.pool.get('bakery.production').search(cr, uid, [], order='id desc', limit=1, context=context)
        production = self.pool.get('bakery.production').browse(cr, uid, running_id)[0]
        if production.stock_moved:
            return False
        else:
            return True
#        process_status = self.pool.get('bakery.process').process_running(cr, uid, '60')
#        if process_status:
#            return False
#        else:
#            return True
        
    def set_testo_produced(self, cr, uid, line_id,kol1,kol2, status):
        if self.check_stock_moved(cr, uid):
            self.write(cr, uid, line_id, {'produced_phantom': kol1,'scrap_phantom': kol2,'status_testo':status})
            cr.commit()
            self.get_qty_delivery_available(cr,uid,line_id,False,False)      
            return True
        else:
            return 'stock_moved'
    
    def set_hladilnica_produced(self, cr, uid, line_id, kol1, status):
        if self.check_stock_moved(cr, uid):
            for mrp_line in self.pool.get('mrp.production').browse(cr, uid, [line_id]):
                if mrp_line.product_id.product_tmpl_id.categ_id.parent_id.id == 38: #izdelki
                    mrp_bom_ids = self.pool.get('mrp.production').search(cr, uid, [('product_id','=',mrp_line.product_with_bom_id),
                                                                                   ('state', 'in', ['ready', 'confirmed','in_production'])
                                                                                   ])
                    qty_P_ready = kol1 * mrp_line.product_with_bom_factor
                    self.pool.get('mrp.production').write(cr, uid, mrp_bom_ids, {'product_on_bom_qty_P_ready':qty_P_ready})
                    
                if mrp_line.product_on_bom_qty_stock != 0:
                    self.write(cr, uid, line_id, {'product_on_bom_qty_O_ready': kol1})
                else:
                    self.write(cr, uid, line_id, {'product_on_bom_qty_ready': kol1})
            cr.commit()
            self.get_qty_delivery_available(cr,uid,line_id,False,False)      
            return True
        else:
            return 'stock_moved'
    
    def set_izdelek_produced(self, cr, uid, line_id,kol1,kol2, status):
        #self.write(cr, uid, line_id, {'produced': kol1,'scrap': kol2,'status_izdelki':status})
        if self.check_stock_moved(cr, uid):
            self.write(cr, uid, line_id, {'produced': kol1,'produced_stock': kol2,'status_izdelki':status})
            cr.commit()
            self.get_qty_delivery_available(cr,uid,line_id,False,False)     
            return True
        else:
            return 'stock_moved'
    
    def set_izdelek_produced1(self, cr, uid, line_id,kol1,kol2,kol3,status,vrstaIzdelka):
        if self.check_stock_moved(cr, uid):
            commit = False
            old_produced = self.browse(cr, uid, [line_id])[0]['produced']
            produced_stock = self.browse(cr, uid, [line_id])[0]['produced_stock']
            scrap = self.browse(cr, uid, [line_id])[0]['scrap']
            current_qty_available = self.browse(cr, uid, [line_id])[0]['product_on_bom_qty_available']
            product_bom_id = self.browse(cr, uid, [line_id])[0]['product_with_bom_id'] #Izdelek iz katerega je ta produkt narejen
            current_status_izdelek = self.browse(cr, uid, [line_id])[0]['status_izdelki']
            
            
            #Ce je izdelek v 'gotovo' in ga zelimo vrniti v 'delu' in je izdelano 0 in na voljo 0 prepreci premik
            #Mora povecati kolicino ki je na voljo, da ga lahko premakne nazaj v delo
            if (current_status_izdelek == 1) and (status == 0) and (old_produced == 0) and (current_qty_available == 0):
                return 'must_not_move'
            
            
            #Ce zakljucujemo in ni dodelava in nismo porabili vsega kar je na voljo
            #moramo najti a so se kaki produkti ki imajo enako osnovo in jih se nismo zakljucili
            if  (status == 1) and (vrstaIzdelka == 'Izdelki') and (current_qty_available - (float(kol1)-old_produced) >= 0):
                same_base_ids = self.pool.get('mrp.production').search(cr, uid, [
                                                                                 ('state', 'in', ['ready', 'confirmed', 'in_production']),
                                                                                 ('product_with_bom_id', '=', product_bom_id),
                                                                                 ('id', '!=', line_id),
                                                                                 ('status_izdelki', '=', 0)
                                                                                 ])
                
                if (not same_base_ids): #ni vec izdelka z isto osnovo, torej moramo pri tem uporabiti celo osnovo
                    if (current_qty_available - (float(kol1)-old_produced) > 0):
                        return 'not_all_consumed'
                else:
                    #Se obstajajo produkti, torej ne sme porabiti celotne kolicine ki je na voljo
                    if ((float(kol1) - old_produced) >= current_qty_available):
                        return 'must_not_consume_all'
            
            
            if (float(kol1) > old_produced):
                if ((float(kol1) - old_produced) > current_qty_available):
                    return 'not_available'
                
            
            sum_produced_old = old_produced - produced_stock - scrap
            sum_produced_new = float(kol1) - float(kol2) - float(kol3)
            
            product_id = self.browse(cr, uid, [line_id])[0]['product_id'].id
            
            if (sum_produced_new < sum_produced_old): #smo vpisali manjso kolicino kot je bila prej, moramo preveriti ali imamo se na voljo toliko produktov
                stock_obj = self.pool.get('stock.move')
                stock_ids = stock_obj.search(cr, uid, [('product_id', '=', product_id),
                                           ('type', '=', 'out'),
                                           ('basket_status', 'in', ['0','1'])
                                           ], limit = 1)
                if stock_ids:
                    #preverimo kolicine, ali jih lahko naredimo manj
                    qty_available = stock_obj.browse(cr, uid, stock_ids)[0]['qty_delivery_available']
                    #ce je razlika med staro in novo vecja kot pa jih imamo na voljo
                    if (sum_produced_old - sum_produced_new > qty_available): 
                        return False
                    else:
                        commit = True
                else:
                    commit = True
            
            else:
                commit = True
            
            if commit:
                self.write(cr, uid, line_id, {'produced': kol1,'scrap': kol2,'produced_stock': kol3,'status_izdelki':status})
                cr.commit()
                self.get_qty_delivery_available(cr,uid,line_id,False,False)
                _production = self.browse(cr, uid, [line_id])
                _product_bom = _production[0].product_with_bom_id
                if _product_bom:
                    self.get_qty_delivery_available(cr,uid,False,False,_product_bom)
                return True
        else:
            return 'stock_moved'
    
mrp_production()


class stock_move_basket(osv.osv):
    _inherit = 'stock.move'
    _columns = {
        'basket_number': fields.related('partner_id', 'basket_number', type='integer', string='Basket number'),       
        'basket_status': fields.integer('Basket status'),
        'basket_deliverd': fields.integer('Basket deliverd'),
        'tags': fields.related('partner_id', 'category_id', type='many2many', string='Tags'),   
    }
    
    _defaults = {
        'basket_status': lambda *a: 0,
        'basket_deliverd': lambda *a: 0,
    }
    
    def create(self, cr, user, vals, context=None):
        if 'sale_line_id' not in vals:
            vals['basket_status'] = 2
        else:
            if vals['sale_line_id']:
                sale_line = self.pool.get('sale.order.line').browse(cr, user, [vals['sale_line_id']])[0]
                if sale_line.order_id.shop_id.shop_production:
                    vals['basket_status'] = 3
                    vals['product_qty_returned'] = sale_line.product_qty_returned
                else:
                    vals['basket_status'] = 2
                    vals['basket_deliverd'] = sale_line.product_uom_qty
            else:
                vals['basket_status'] = 2
                
        res = super(stock_move_basket, self).create(cr, user, vals, context=context)
        return res
    
    def set_basket_status(self, cr, uid, line_id, status):
        self.write(cr, uid, line_id, {'basket_status': status})
        return True
    
    #stock.call('set_basket_deliverd',        [id1,    kol,    1])
    def set_basket_deliverd(self, cr, uid, line_id, deliverd, status):
        if self.pool.get('mrp.production').check_stock_moved(cr, uid):
            qty_available = self.browse(cr, uid, [line_id])[0]['qty_delivery_available']
            deliverd_old = self.browse(cr, uid, [line_id])[0]['basket_deliverd']
            
            if ( (float(deliverd)-deliverd_old) <= qty_available):
                self.write(cr, uid, line_id, {'basket_deliverd': deliverd,'basket_status': status})
                cr.commit()
                self.get_qty_delivery_available(cr,uid,False,line_id)
                return True
            else:
                return False
        else:
            return 'stock_moved'
    
    def sum_basket_deliverd(self,cr,uid, product_id, i):
        move_ids = self.search(cr, uid, (
                                                 ['type', '=', 'out'],
                                                 ['basket_status', '=', 1],
                                                 ['product_id', '=', product_id[0]]
                                                 ))
        sumB=0
        for move in self.browse(cr, uid, move_ids):
            sumB = sumB + move.basket_deliverd
        return [i,sumB]
    
stock_move_basket()
