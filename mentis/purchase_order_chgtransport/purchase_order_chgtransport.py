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

class purchase_order_chgtransport(osv.osv_memory):
    _name = "purchase.order.chgtransport"
    _description = "Select transport on Purchase Orders"
    _columns = {
        'transport_id': fields.many2one('transport', 'Transport'),
    }
    
    def change_transport(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        
        transport_id_id = self.browse(cr,uid,ids)[0].transport_id.id
        if not transport_id_id:
            raise osv.except_osv(_('Warning'),
            _('Please select transport!'))
            
        
        order_obj = self.pool.get('purchase.order')
        active_ids = context.get('active_ids',[])

        for order in order_obj.browse(cr, uid, active_ids, context=context):
            if (order.state == 'draft'):
                order_obj.write(cr, uid, [order.id], {'transport_id': transport_id_id})
        
        return {
                'type': 'ir.actions.act_window_close',
        }
    
purchase_order_chgtransport()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwi
