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

from osv import fields, osv

class stock_picking(osv.Model):
    _inherit = "stock.picking"

    def _picking_update(self, cr, uid, ids, ctx):
        context = {}
        for _picking in self.pool.get('stock.picking').browse(cr, uid, ids, context):
            _costs_installed = self.pool.get('stock.picking').fields_get(cr, uid, ['landing_costs_line_ids'], context) != {}
            
            _move_ids = self.pool.get('stock.move').search(cr, uid, [('picking_id','=',_picking.id)])
            _date_delivered = ctx.get('date_delivered', False)
            if _date_delivered:
                self.pool.get('stock.picking').write(cr, uid, [_picking.id], {'date_done': _date_delivered})

            if _costs_installed:
                _picking_has_costs = len(_picking.landing_costs_line_ids) > 0
            else:
                _picking_has_costs = False
            
            _moves_have_costs = False
            for _move in _picking.move_lines:
                if _costs_installed:
                    if len(_move.landing_costs_line_ids) > 0:
                        _moves_have_costs = True
                _move_data = ctx.get('move%s'%(_move.id), {})
                if _move_data == {}:
                    continue
                _price_unit = _move_data.get('price_unit', False)
                _quantity = _move_data.get('quantity', False)
                self.pool.get('stock.move')._move_update_values(cr, uid, [_move.id], context, _date_delivered, _quantity, _price_unit)
            if _costs_installed and (_picking_has_costs or _moves_have_costs):
                self.pool.get('stock.move')._move_update_costs(cr, uid, _move_ids, context)
            self.pool.get('stock.move')._move_update_valuation(cr, uid, _move_ids, context)
        return True
