# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP s.a. (<http://www.openerp.com>).
#    Copyright (C) 2013-TODAY Mentis d.o.o. (<http://www.mentis.si/openerp>)
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

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp.tools import mute_logger
import openerp.addons.decimal_precision as dp

class stock_fill_inventory(osv.TransientModel):
    _inherit = "stock.fill.inventory"

    def _default_location(self, cr, uid, ids, context=None):
        try:
            location = self.pool.get('ir.model.data').get_object(cr, uid, 'stock', 'stock_location_stock')
            with mute_logger('openerp.osv.orm'):
                location.check_access_rule('read', context=context)
            location_id = location.id
        except (ValueError, orm.except_orm), e:
            return False
        return location_id or False

    _columns = {
        'category_id':       fields.many2one('product.category', 'Category', required=False),
        'display_with_zero': fields.boolean('Add with zero quantity', required=False)
    }
 
    def fill_inventory(self, cr, uid, ids, context=None):
        """ To Import stock inventory according to products available in the selected locations.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: the ID or list of IDs if we want more than one
        @param context: A standard dictionary
        @return:
        """
        if context is None:
            context = {}

        _digits_id = self.pool.get('decimal.precision').search(cr, uid, [('name','=','Product Unit of Measure')])
        if len(_digits_id) > 0:
            _digits = self.pool.get('decimal.precision').browse(cr, uid, _digits_id[0])['digits']
        else:
            _digits = 2

        inventory_line_obj = self.pool.get('stock.inventory.line')
        location_obj = self.pool.get('stock.location')
        category_obj = self.pool.get('product.category')
        move_obj = self.pool.get('stock.move')
        uom_obj = self.pool.get('product.uom')
        if ids and len(ids):
            ids = ids[0]
        else:
             return {'type': 'ir.actions.act_window_close'}
        fill_inventory = self.browse(cr, uid, ids, context=context)
        res = {}
        res_location = {}

        if fill_inventory.recursive:
            location_ids = location_obj.search(cr, uid, [('location_id',
                             'child_of', [fill_inventory.location_id.id])], order="id",
                             context=context)
        else:
            location_ids = [fill_inventory.location_id.id]

        category_ids = category_obj.search(cr, uid, [('parent_id',
                             'child_of', [fill_inventory.category_id.id])], order="id",
                             context=context)

        res = {}
        flag = False

        for location in location_ids:
            datas = {}
            res[location] = {}
            move_ids = move_obj.search(cr, uid, ['|',('location_dest_id','=',location),('location_id','=',location),('state','=','done'),('product_id.categ_id','in',category_ids)], context=context)

            for move in move_obj.browse(cr, uid, move_ids, context=context):
                lot_id = move.prodlot_id.id
                prod_id = move.product_id.id
                if move.location_dest_id.id != move.location_id.id:
                    if move.location_dest_id.id == location:
                        qty = uom_obj._compute_qty(cr, uid, move.product_uom.id,move.product_qty, move.product_id.uom_id.id)
                    else:
                        qty = -uom_obj._compute_qty(cr, uid, move.product_uom.id,move.product_qty, move.product_id.uom_id.id)


                    if datas.get((prod_id, lot_id)):
                        qty += datas[(prod_id, lot_id)]['product_qty']

                    datas[(prod_id, lot_id)] = {'product_id': prod_id, 'location_id': location, 'product_qty': round(qty, _digits), 'product_uom': move.product_id.uom_id.id, 'prod_lot_id': lot_id}

            if datas:
                flag = True
                res[location] = datas

        if not flag:
            raise osv.except_osv(_('Warning!'), _('No product in this location. Please select a location in the product form.'))

        for stock_move in res.values():
            for stock_move_details in stock_move.values():
                stock_move_details.update({'inventory_id': context['active_ids'][0]})
                domain = []
                for field, value in stock_move_details.items():
                    if field == 'product_qty' and fill_inventory.set_stock_zero:
                         domain.append((field, 'in', [value,'0']))
                         continue
                    domain.append((field, '=', value))

                if fill_inventory.set_stock_zero:
                    stock_move_details.update({'product_qty': round(0.0, _digits)})

                if fill_inventory.set_stock_zero \
                   or fill_inventory.display_with_zero \
                   or stock_move_details['product_qty'] <> round(0.0, _digits):
                    line_ids = inventory_line_obj.search(cr, uid, domain, context=context)
                    if not line_ids:
                        inventory_line_obj.create(cr, uid, stock_move_details, context=context)

        return {'type': 'ir.actions.act_window_close'}