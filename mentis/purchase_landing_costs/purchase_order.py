# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP s.a. (<http://www.openerp.com>).
#    Copyright (C) 2012-TODAY Mentis d.o.o. (<http://www.mentis.si/openerp>)
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

from osv import osv, fields

class purchase_order(osv.osv):
    _inherit = "purchase.order"
    _columns = {
        'landing_costs_line_ids': fields.one2many('purchase.landing.cost.position', 'purchase_order_id', 'Landing Costs'),
     }

    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, context=None):
        res = super(purchase_order,self)._prepare_order_line_move( cr, uid, order, order_line, picking_id, context)
        res['price_unit_without_costs'] =  res['price_unit']
        return res

    def _prepare_order_picking(self, cr, uid, order, context=None):
        res = super(purchase_order,self)._prepare_order_picking( cr, uid, order, context)
        return res

    def _create_pickings(self, cr, uid, order, order_lines, picking_id=False, context=None): 
        res = super(purchase_order,self)._create_pickings(cr, uid, order, order_lines, picking_id, context)
        picking_id = int(res[0])
        landing_cost_object = self.pool.get('purchase.landing.cost.position')
        for order_cost in order.landing_costs_line_ids:
            vals = {}
            vals['product_id'] = order_cost.product_id.id
            vals['partner_id'] = order_cost.partner_id.id
            vals['amount'] = order_cost.amount
            vals['distribution_type'] = order_cost.distribution_type
            vals['picking_id'] = picking_id
            landing_cost_object.create(cr, uid, vals, context=None)

        picking_obj = self.pool.get('stock.picking.in')
        for picking in picking_obj.browse(cr, uid, [picking_id], context=None):
            for line in picking.move_lines:
                for line_cost in line.purchase_line_id.landing_costs_line_ids:
                    vals = {}
                    vals['product_id'] = line_cost.product_id.id
                    vals['partner_id'] = line_cost.partner_id.id
                    vals['amount'] = line_cost.amount
                    vals['distribution_type'] = line_cost.distribution_type
                    vals['move_line_id'] = line.id
                    landing_cost_object.create(cr, uid, vals, context=None) 

        return res
