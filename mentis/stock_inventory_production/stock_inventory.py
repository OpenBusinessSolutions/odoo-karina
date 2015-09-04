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

class stock_inventory(osv.Model):    
    _inherit = "stock.inventory"

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}

        res = super(stock_inventory, self).default_get(cr, uid, fields, context)
        res.update({'inventory_production': context.get('inventory_production', False)})
        return res

    _columns = {
        'inventory_production': fields.boolean('Production Inventory')
    }
    _defaults = {
        'inventory_production': False
    }

    def action_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        if context.get('inventory_production', False):
            return self.action_confirm_production(cr, uid, ids, context)
        else:
            return super(stock_inventory, self).action_confirm(cr, uid, ids, context)


    def action_done(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        if context.get('inventory_production', False):
            return self.action_done_production(cr, uid, ids, context)
        else:
            return super(stock_inventory, self).action_done(cr, uid, ids, context)


    def action_done_production(self, cr, uid, ids, context=None):
        """ Finish the inventory
        @return: True
        """
        if context is None:
            context = {}
        move_obj = self.pool.get('stock.move')
        for inv in self.browse(cr, uid, ids, context=context):
            move_obj.action_done(cr, uid, [x.id for x in inv.move_ids], context=context)
            move_obj.write(cr, uid, [x.id for x in inv.move_ids], {'date': inv.date}, context=context)
            self.write(cr, uid, [inv.id], {'state':'done', 'date_done': inv.date}, context=context)
        return True

    def action_confirm_production(self, cr, uid, ids, context=None):
        """ Confirm the inventory and writes its finished date
        @return: True
        """
        if context is None:
            context = {}
        # to perform the correct inventory corrections we need analyze stock location by
        # location, never recursively, so we use a special context
        product_context = dict(context, compute_child=False)

        location_obj = self.pool.get('stock.location')
        for inv in self.browse(cr, uid, ids, context=context):
            move_ids = []
            for line in inv.inventory_line_id:
                pid = line.product_id.id
                product_context.update(uom=line.product_uom.id, to_date=inv.date, date=inv.date, prodlot_id=line.prod_lot_id.id)
                amount = location_obj._product_get(cr, uid, line.location_id.id, [pid], product_context)[pid]
                change = line.product_qty - amount
                lot_id = line.prod_lot_id.id
                if change:
                    location_id = line.product_id.property_stock_production.id
                    value = {
                        'name': _('INV_PR:') + (line.inventory_id.name or ''),
                        'product_id': line.product_id.id,
                        'product_uom': line.product_uom.id,
                        'prodlot_id': lot_id,
                        'date': inv.date,
                        'date_expected': inv.date_done
                    }

                    if change > 0:
                        value.update( {
                            'product_qty': change,
                            'location_id': location_id,
                            'location_dest_id': line.location_id.id,
                        })
                    else:
                        value.update( {
                            'product_qty': -change,
                            'location_id': line.location_id.id,
                            'location_dest_id': location_id,
                        })
                    move_ids.append(self._inventory_line_hook(cr, uid, line, value))
            self.write(cr, uid, [inv.id], {'state': 'confirm', 'move_ids': [(6, 0, move_ids)]})
            self.pool.get('stock.move').action_confirm(cr, uid, move_ids, context=context)
        return True
