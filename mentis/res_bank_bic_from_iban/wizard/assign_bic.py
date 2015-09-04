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

class assign_bic(osv.osv_memory):
    _name = "bank.assign.bic.from.iban"
    _description = "Assign BIC from customer IBAN number"
    _columns = {
            'overwrite': fields.boolean('Re-assign existing one')
    }
    _default = {
            'overwrite': 0
    }
    
    def assign(self, cr, uid, ids, context=None):
        
        if context is None:
            context={}
        active_ids = context.get('active_ids',[])
        overwrite = self.browse(cr,uid,ids)[0].overwrite
        
        bank_obj = self.pool.get('res.bank')
        partner_bank_obj = self.pool.get('res.partner.bank')
        
        if overwrite:
            partner_bank_ids = partner_bank_obj.search(cr, uid, [('acc_number', '=ilike', 'SI56%'),
                                                             ('id', 'in', active_ids)])
        else:
            partner_bank_ids = partner_bank_obj.search(cr, uid, [('acc_number', '=ilike', 'SI56%'),
                                                             ('bank_bic', '=', False),
                                                             ('id', 'in', active_ids)])
            
        for line in partner_bank_obj.browse(cr, uid, partner_bank_ids):
            iban_bic = line.acc_number.replace(" ", "")[4:6]
            
            bank_ids = bank_obj.search(cr, uid, [('bic_iban_id', '=', iban_bic)])
            if bank_ids:
                for bank_line in bank_obj.browse(cr, uid, bank_ids):
                    partner_bank_obj.write(cr, uid, [line.id], {'bank':bank_line.id,
                                                                'bank_bic':bank_line.bic,
                                                                'bank_name':bank_line.name})
        
        return {
                'type': 'ir.actions.act_window_close',
        }
    
assign_bic()
