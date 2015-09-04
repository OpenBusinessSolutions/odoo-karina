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

from osv import osv, fields
from tools.translate import _

class account_invoice(osv.osv):
    _inherit = "account.invoice"

    def action_date_assign(self, cr, uid, ids, *args):
        for invoice_id in self.browse(cr, uid, ids, context=None):
            if invoice_id.type in ('in_invoice', 'in_refund'):
                if not invoice_id.supplier_invoice_number:
                    raise osv.except_osv(_('Warning'), _('Please select Supplier Invoice Number'))
                if not invoice_id.reference or invoice_id.reference == invoice_id.origin:
                    self.write(cr, uid, ids, {'reference': invoice_id.supplier_invoice_number})
        return super(account_invoice, self).action_date_assign(cr, uid, ids, *args)

    def action_number(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        super(account_invoice, self).action_number(cr, uid, ids, context)

        invoice_ids = self.browse(cr, uid, ids, context)
        for invoice_id in invoice_ids:
            if invoice_id.type in ('in_invoice', 'in_refund'):
                invoice_reference = invoice_id.supplier_invoice_number
            else:
                invoice_reference = invoice_id.internal_number
            self.pool.get('account.move').write(cr, uid, [invoice_id.move_id.id], {'invoice_reference': invoice_reference})
        return True
    
account_invoice()