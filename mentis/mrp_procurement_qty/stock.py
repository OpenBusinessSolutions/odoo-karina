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
from openerp.tools.safe_eval import safe_eval

import time
from dateutil.relativedelta import relativedelta
from datetime import datetime
from lxml import etree

class stock_picking_out(osv.osv):
    def _get_relation_tag(self, cr, uid, ids, name, args, context=None):
        result = {}
        stock_picking_obj = self.pool.get('stock.picking')
        for line in stock_picking_obj.browse(cr, uid, ids):
            if line.partner_id and line.partner_id.category_id:
                result[line.id] = line.partner_id.category_id[0].name
        return result
    
    _inherit = "stock.picking.out"
    _columns = {
        'distribution_relation': fields.function(_get_relation_tag, type='char', string='Relacija', store=True),
        'distribution_vehicle': fields.related('partner_id', 'vehicle', type='selection', relation='res.partner', selection=[('1','Vozilo 1'), ('2','Vozilo 2'), ('3','Vozilo 3'), ('4','Vozilo 4')], string='Vozilo', store=True),
        'basket_number': fields.related('partner_id', 'basket_number', type='integer', relation='res.partner', string='Št.košare', store=True),
        'invoice_type_id': fields.many2one('sale_journal.invoice.type', 'Invoice Type') #DARJA 
    }
    
    def duplicate_sale_order(self, cr, uid, id, default=None, context=None):
        if context is None:
            context = {}
        new_sale_order_id = 0
        sale_order_obj = self.pool.get('sale.order')
        ir_values_obj = self.pool.get('ir.values')
        
        for line in self.browse(cr, uid, id):
            if line.sale_id:
                #poiscemo ce obstaja privzeti datum "date_order" na "sale-order" za dolocenega uporabnika
#                default_date = None
#                ir_values_ids = ir_values_obj.search(cr, uid, [
#                                                               ('name','=','date_order'),
#                                                               ('model','=','sale.order'),
#                                                               ])
#                for line_val in ir_values_obj.browse(cr, uid, ir_values_ids):
#                    if line_val.user_id:
#                        if line_val.user_id.id == uid:
#                            default_date = line_val.value_unpickle
#                            break
#                    else:
#                        default_date = line_val.value_unpickle
                        
                default = {'delivery_order_ref_ids': line.id}
                new_sale_order_id = sale_order_obj.copy(cr, uid, line.sale_id.id, default=default)
                
                #Po kopiranju spremenimo datum
                #sale_order_obj.write(cr, uid, [new_sale_order_id], {'date_order':default_date})
            else:
                raise osv.except_osv(_('Opozorilo'), _('Delovni nalog ni nastal na podlagi Prodajnega naloga; kopiranje ni mogoče!'))
            
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sale', 'view_order_form')
        #view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sale_order_extensions', 'view_order_extensions_form_inherit')
        
        view_id = view_ref and view_ref[1] or False,
        context['simple_view'] = True
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': new_sale_order_id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'context': context,
        }
        
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = super(stock_picking_out, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu)
        #if context and context.get('active_model', False) == 'stock.location.product' and view_type == 'search':
        if view_type == 'search':
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//search"):
                _categ_ids = self.pool.get('sale_journal.invoice.type').search(cr, uid, [], order='name')
                for _categ_id in self.pool.get('sale_journal.invoice.type').browse(cr, uid, _categ_ids, context):
                    _name = _categ_id.name
                    _domain = "[('invoice_type_id','='," + str(_categ_id.id) + ")]"

                    _filter = etree.Element('filter')
                    _filter.set('string', _categ_id.name)
                    _filter.set('domain', _domain)
                    node.append(_filter)
            res['arch'] = etree.tostring(doc)            
        
        return res
        
stock_picking_out() 
    
class stock_picking(osv.osv):
    def _get_relation_tag(self, cr, uid, ids, name, args, context=None):
        result = {}
        stock_picking_obj = self.pool.get('stock.picking')
        for line in stock_picking_obj.browse(cr, uid, ids):
            if line.partner_id and line.partner_id.category_id:
                result[line.id] = line.partner_id.category_id[0].name
        return result
    
    _inherit = "stock.picking"
    _columns = {
        'distribution_relation': fields.function(_get_relation_tag, type='char', string='Relacija', store=True),
        'distribution_vehicle': fields.related('partner_id', 'vehicle', type='selection', relation='res.partner', selection=[('1','Vozilo 1'), ('2','Vozilo 2'), ('3','Vozilo 3'), ('4','Vozilo 4')], string='Vozilo', store=True),
        'basket_number': fields.related('partner_id', 'basket_number', type='integer', relation='res.partner', string='Št.košare', store=True),
        'invoice_type_id': fields.many2one('sale_journal.invoice.type', 'Invoice Type') #DARJA
    }
    
    def _get_partner_obj(self, cr, uid, picking, context=None):
        vals = {}
        #Vrne naslov racuna		
        if picking.sale_id:
            vals['parner_invoice'] = picking.sale_id.partner_invoice_id
        vals['parner_invoice'] = super(stock_picking, self)._get_partner_to_invoice(cr, uid, picking, context=context)

        vals['partner_group'] = picking.partner_id and picking.partner_id.id
        
        return vals
    
    def _get_decade_date(self, cr, uid, picking, inv_type, partner, context=None):
        res = ''
        
        curr_lang = context.get('lang', False)
        lang_obj = self.pool.get('res.lang')
        lang_id = lang_obj.search(cr, uid, [('code', '=', curr_lang)])
        DATE_FORMAT = lang_obj.read(cr, uid, lang_id, ['date_format'])[0]['date_format']
        
        invoice_date = context.get('date_inv', False)
        invoice_type = partner.property_invoice_type.name
        
        date = datetime.strptime(invoice_date, "%Y-%m-%d")
        
        last_day = date + relativedelta(day=1, months=+1, days=-1)
        first_day = date + relativedelta(day=1)
        day_10 = date + relativedelta(day=10)
        day_11 = date + relativedelta(day=11)
        day_20 = date + relativedelta(day=20)
        day_21 = date + relativedelta(day=21)
        
        if invoice_type == 'Mesečno' or invoice_type == 'Mesečno za zaposlene':
            res = first_day.strftime(DATE_FORMAT) +' - ' + last_day.strftime(DATE_FORMAT)
        elif invoice_type == 'Dekadno' or invoice_type == 'Interni prenosi':
            if date < day_11:
                res = first_day.strftime(DATE_FORMAT) +' - ' + day_10.strftime(DATE_FORMAT) #dekada1
            elif date < day_21:
                res = day_11.strftime(DATE_FORMAT) +' - ' + day_20.strftime(DATE_FORMAT) #dekada2
            else:
                res = day_21.strftime(DATE_FORMAT) +' - ' + last_day.strftime(DATE_FORMAT) #dekada3
        else:
            res = invoice_date
            
        return res
    
    def _merge_invoice_lines(self, cr, uid, vals, context=None):
        invoice_line_obj = self.pool.get('account.invoice.line')
        
        price_lo = vals['price_unit'] - 0.0001
        price_hi = vals['price_unit'] + 0.0001
        
        invoice_line_ids = invoice_line_obj.search(cr, uid, [
                                                             ('invoice_id', '=', vals['invoice_id']),
                                                             ('product_id', '=', vals['product_id']),
                                                             ('price_unit', '>=', price_lo),
                                                             ('price_unit', '<=', price_hi),
                                                             ('discount', '=', vals['discount'])
                                                             ])
        
        for line_obj in invoice_line_obj.browse(cr, uid, invoice_line_ids):
            quantity_sum = vals['quantity'] + line_obj.quantity
            returned_sum = vals['product_qty_returned'] + line_obj.product_qty_returned
            
            
            invoice_line_obj.write(cr, uid, [line_obj.id], {'quantity':quantity_sum,
                                                            'product_qty_returned':returned_sum})
            return True # ce je bila linija zdruzena
        
        return False 

    def action_invoice_create(self, cr, uid, ids, journal_id=False, group=False, type='out_invoice', context=None):
        """ Creates invoice based on the invoice state selected for picking.
        @param journal_id: Id of journal
        @param group: Whether to create a group invoice or not
        @param type: Type invoice to be created
        @return: Ids of created invoices for the pickings
        """
        
        if type == 'in_invoice':
            return super(stock_picking, self).action_invoice_create(cr, uid, ids, journal_id=journal_id, group=group, type=type, context=context)
        
        if context is None:
            context = {}
            
        #Lahko se zgodi, da uporabnik ne izbere datuma na wizardu, ponastavimo na danasnji datum
        if not context.get('date_inv', False):
            context['date_inv'] = datetime.now().strftime("%Y-%m-%d")

        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        partner_obj = self.pool.get('res.partner')
        invoices_group = {}
        res = {}
        inv_type = type
        
        _picking_ids = self.search(cr, uid, [('id','in',ids)], order='partner_id,date_done')
        for picking in self.browse(cr, uid, _picking_ids, context=context):
        #for picking in self.browse(cr, uid, ids, context=context):
            if picking.invoice_state != '2binvoiced':
                continue
            #Pridobimo naslov za racun in naslov za grupiranje________________________________
            partner_vals = self._get_partner_obj(cr, uid, picking, context=context)
            partner = partner_vals['parner_invoice']
            partner_id_group = partner_vals['partner_group']
            #_________________________________________________________________________________
            
            if isinstance(partner, int):
                partner = partner_obj.browse(cr, uid, [partner], context=context)[0]
            if not partner:
                raise osv.except_osv(_('Error, no partner !'),
                    _('Please put a partner on the picking list if you want to generate invoice.'))

            if not inv_type:
                inv_type = self._get_invoice_type(picking)

            if group and partner_id_group in invoices_group:
                invoice_id = invoices_group[partner_id_group]
                invoice = invoice_obj.browse(cr, uid, invoice_id)
                invoice_vals_group = self._prepare_invoice_group(cr, uid, picking, partner, invoice, context=context)
                invoice_vals_group['delivery_order_origin'] = invoice.delivery_order_origin + ', ' + picking.name
                invoice_vals_group['name'] = '' #customer reference - je ne vpisujejo, naj bo prazna
                invoice_obj.write(cr, uid, [invoice_id], invoice_vals_group, context=context)
            else:
                invoice_vals = self._prepare_invoice(cr, uid, picking, partner, inv_type, journal_id, context=context)
                invoice_vals['address_shipping_id'] = partner_id_group
                invoice_vals['delivery_order_origin'] = picking.name
                
                invoice_vals['decade_date'] = self._get_decade_date(cr, uid, picking, inv_type, partner, context)
                
                invoice_id = invoice_obj.create(cr, uid, invoice_vals, context=context)
                invoices_group[partner_id_group] = invoice_id
            
            if not invoice_id in res.values():
                res[picking.id] = invoice_id
            
            for move_line in picking.move_lines:
                if move_line.state == 'cancel':
                    continue
                if move_line.scrapped:
                    # do no invoice scrapped products
                    continue
                vals = self._prepare_invoice_line(cr, uid, False, picking, move_line,
                                invoice_id, invoice_vals, context=context)
                if vals:
                    vals['product_qty_returned'] = move_line.product_qty_returned #products that were returned
                    if not self._merge_invoice_lines(cr, uid, vals, context):
                        invoice_line_id = invoice_line_obj.create(cr, uid, vals, context=context)
                        self._invoice_line_hook(cr, uid, move_line, invoice_line_id)
            
            invoice_obj.button_compute(cr, uid, [invoice_id], context=context,
                    set_total=(inv_type in ('in_invoice', 'in_refund')))
            self.write(cr, uid, [picking.id], {
                'invoice_state': 'invoiced',
                }, context=context)
            self._invoice_hook(cr, uid, picking, invoice_id)
            
        #raise osv.except_osv(_('Error!'),  _('Safe braking.'))
        #TODO: Moramo spremeniti vrstni red
        #Ker ne poznam id-jev faktur se morap po njih sprehoditi in za vsakega narediti search po linijah sortiranih po imenu
        for invoice_id in res:
            line_ids = invoice_line_obj.search(cr, uid, [('invoice_id', '=', res[invoice_id])], order='name')
            sequence = 1
            for line_id in line_ids:
                invoice_line_obj.write(cr, uid, [line_id], {'sequence': sequence})
                sequence += 1
        
        self.write(cr, uid, res.keys(), {
            'invoice_state': 'invoiced',
            }, context=context)
        return res
    
    def _get_price_unit_invoice(self, cursor, user, move_line, type):
        #Ce obstaja product_id na movu in obstaja povezava na sale line in tam ne obstaja product_id -> vracilo
        if move_line.sale_line_id and not move_line.sale_line_id.product_id.id and move_line.product_id.id:
            return move_line.sale_line_id.price_unit
        return super(stock_picking, self)._get_price_unit_invoice(cursor, user, move_line, type)

stock_picking()

class stock_move(osv.osv):
    _inherit = "stock.move"    
    _columns = {
        'qty_delivery_available': fields.integer('qty_delivery_available'),
        'default_code': fields.related('product_id', 'default_code', type='char', string='Koda', store=True),
    }
    
    def get_qty_delivery_available(self, cr, uid, production_id=False, stock_id=False,product_id=False, context=None):
        _product = False
        
        if product_id:
            _product = product_id
        elif production_id and production_id != 0:
            _production = self.pool.get('mrp.production').browse(cr, uid, [production_id], context)
            _product = _production[0].product_id.id 
        elif stock_id and stock_id != 0:
            _stock_move = self.pool.get('stock.move').browse(cr, uid, [stock_id], context)
            _product = _stock_move[0].product_id.id
        
        if _product and _product != 0:
            _where_product = " AND sm.product_id = " + str(_product)
        else:
            _where_product = ""
            
        _sql_string = """WITH stock_moves AS (SELECT sm.id AS stock_move_id,
                            sm.product_id AS product_id
                       FROM stock_move AS sm
                            INNER JOIN stock_picking AS sp ON sp.id = sm.picking_id
                                                              AND sp.type = 'out'
                      WHERE sm.basket_status IN (0,1) """ + _where_product + "), " \
     """products AS (SELECT sm.product_id AS product_id
                       FROM stock_moves AS sm
                   GROUP BY sm.product_id),
   in_production AS (SELECT pp.product_id AS product_id,
                            (SELECT SUM(CASE
                                          WHEN mrp.produced IS NULL
                                            THEN 0
                                          ELSE mrp.produced
                                        END -
                                        CASE
                                          WHEN mrp.scrap IS NULL
                                            THEN 0
                                          ELSE mrp.scrap
                                        END -
                                        CASE
                                          WHEN mrp.produced_stock IS NULL
                                            THEN 0
                                          ELSE mrp.produced_stock
                                        END)
                               FROM mrp_production AS mrp
                              WHERE mrp.product_id = pp.product_id
                                    AND mrp.state IN ('ready','confirmed')) AS qty_in_production,
                            (SELECT SUM(CASE
                                          WHEN mrp2.produced IS NULL
                                            THEN 0
                                          ELSE mrp2.produced
                                        END *
                                        CASE
                                          WHEN mrp2.product_with_bom_factor IS NULL
                                               OR mrp2.product_with_bom_factor = 0
                                            THEN 1
                                          ELSE mrp2.product_with_bom_factor
                                        END)
                               FROM mrp_production AS mrp2
                              WHERE mrp2.product_with_bom_id = pp.product_id
                                    AND mrp2.state IN ('ready','confirmed')) AS qty_bom_in_production
                       FROM products AS pp),
       locations AS (SELECT wh.lot_stock_id AS location_id
                       FROM stock_warehouse AS wh
                            INNER JOIN stock_location AS lo ON lo.id = wh.lot_stock_id
                                                               AND lo.scrap_location = FALSE 
                   GROUP BY wh.lot_stock_id),
        on_stock AS (SELECT pp.product_id AS product_id,
                            (SELECT SUM(sm.product_qty)
                               FROM stock_move AS sm
                              WHERE sm.product_id = pp.product_id
                                    AND sm.state = 'done'
                                    AND sm.location_id NOT IN (SELECT *
                                                                 FROM locations)
                                    AND sm.location_dest_id IN (SELECT *
                                                                  FROM locations)) AS qty_recieved,
                                (SELECT SUM(sm.product_qty)
                                   FROM stock_move AS sm
                                  WHERE sm.product_id = pp.product_id
                                        AND sm.basket_status = 2
                                        AND sm.state IN ('confirmed','assigned','done')
                                        AND sm.location_id IN (SELECT *
                                                                 FROM locations)
                                        AND sm.location_dest_id NOT IN (SELECT *
                                                                          FROM locations)) AS qty_delivered
                           FROM products AS pp),
         delivered AS (SELECT pp.product_id AS product_id,
                              SUM(sm.basket_deliverd) AS qty_delivered
                         FROM products AS pp
                              INNER JOIN stock_move AS sm ON sm.product_id = pp.product_id
                                                             AND sm.basket_status IN (0,1)
                     GROUP BY pp.product_id),
        quantities AS (SELECT pp.product_id AS product_id,
                              os.qty_recieved AS qty_recieved,
                              os.qty_delivered AS qty_delivered,
                              ip.qty_in_production AS qty_in_production,
                              ip.qty_bom_in_production AS qty_bom_in_production,
                              CASE
                                WHEN os.qty_recieved IS NULL
                                  THEN 0
                                ELSE os.qty_recieved
                              END -
                              CASE
                                WHEN os.qty_delivered IS NULL
                                  THEN 0
                                ELSE os.qty_delivered
                              END +
                              CASE
                                WHEN ip.qty_in_production IS NULL
                                  THEN 0
                                ELSE ip.qty_in_production
                              END -
                              CASE
                                WHEN ip.qty_bom_in_production IS NULL
                                  THEN 0
                                ELSE ip.qty_bom_in_production
                              END -
                              CASE
                                WHEN de.qty_delivered IS NULL
                                  THEN 0
                                ELSE de.qty_delivered
                              END::NUMERIC AS qty_available
                         FROM products AS pp
                              LEFT OUTER JOIN on_stock AS os ON os.product_id = pp.product_id
                              LEFT OUTER JOIN in_production AS ip ON ip.product_id = pp.product_id
                              LEFT OUTER JOIN delivered AS de ON de.product_id = pp.product_id)                                                       
       UPDATE stock_move
          SET qty_delivery_available = (SELECT FLOOR(quantities.qty_available)
                                          FROM quantities
                                         WHERE quantities.product_id = stock_move.product_id)
        WHERE id IN (SELECT stock_move_id
                       FROM stock_moves) AND basket_status != 3;"""
        cr.execute(_sql_string)
        return 0
    
stock_move()

