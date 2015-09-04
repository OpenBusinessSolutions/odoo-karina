# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Mentis d.o.o. (www.mentis.si/openerp)
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

class stock_picking(osv.osv):
    _inherit = "stock.picking"

    def action_done(self, cr, uid, ids, context=None):
        picking = self.browse(cr, uid, ids[0], context)
        if picking.date_done:
            stock_move_obj = self.pool.get('stock.move')
            account_move_obj = self.pool.get('account.move')
            account_move_line_obj = self.pool.get('account.move.line')
            period_obj = self.pool.get('account.period')
    
            picking_ids = self.pool.get('stock.picking').browse(cr, uid, ids, context)
            for picking in picking_ids:
                account_move_ids = account_move_obj.search(cr, uid, [('ref','=',picking.name)])
                account_moves = account_move_obj.browse(cr, uid, account_move_ids)
                for account_move in account_moves:
                    period_id = period_obj.find(cr, uid, picking.date_done, context)
                    account_move.write({'date': picking.date_done,
                                        'period_id': period_id[0],
                                        'tax_period_id': period_id[0]})
                    for account_line in account_move.line_id:
                        account_line.write({'date': picking.date_done,
                                            'period_id': period_id[0],
                                            'tax_period_id': period_id[0]})
                for stock_move in picking.move_lines:
                    stock_move.write({'date': picking.date_done})
            self.write(cr, uid, ids, {'state': 'done'})
            return True
        else:
            return super(stock_picking, self).action_done(cr, uid, ids, context)

stock_picking()
