# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Mentis d.o.o. (<http://www.mentis.si/openerp>).
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

class account_move(osv.osv):
    _inherit = "account.move"

    _columns = {
        'invoice_reference': fields.char('Invoice Reference', size=64, help="The partner reference of this invoice."),
    }    
    
    def post(self, cr, uid, ids, context=None):
        move_ids = self.browse(cr, uid, ids, context=context)
        for move_id in move_ids:
            invoice_reference = move_id.invoice_reference and move_id.invoice_reference or move_id.ref
            invoice = context.get('invoice', False)
            if invoice:
                if invoice.type in ('in_invoice', 'in_refund'):
                    invoice_reference = invoice.supplier_invoice_number
                else:
                    invoice_reference = invoice.internal_number
            if invoice_reference != move_id.invoice_reference:
                self.write(cr, uid, [move_id.id], {'invoice_reference': invoice_reference})
        return super(account_move, self).post(cr, uid, ids, context=context)

account_move()