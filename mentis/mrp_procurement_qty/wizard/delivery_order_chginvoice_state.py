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

class delivery_order_chginvoice_state(osv.osv_memory):
    _name = "delivery.order.chginvoice.state"
    _description = "Change delivery order invoice state to 2binvoiced"
    
    def change_2binvoiced(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        
        picking_obj = self.pool.get('stock.picking')
        active_ids = context.get('active_ids',[])

        for line in picking_obj.browse(cr, uid, active_ids, context=context):
            if (line.invoice_state == 'invoiced'):
                picking_obj.write(cr, uid, [line.id], {'invoice_state': '2binvoiced'})
        
        return {
                'type': 'ir.actions.act_window_close',
        }
    
delivery_order_chginvoice_state()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwi
