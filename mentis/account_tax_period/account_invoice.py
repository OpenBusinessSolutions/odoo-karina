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

class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    _columns = {
        'tax_period_id': fields.many2one('account.period', 'Tax Period', domain=[('state','<>','done')], help="Keep empty to use the period of the validation date.", readonly=True, states={'draft':[('readonly',False)]}),
    }

    def action_move_create(self, cr, uid, ids, context=None):
        if super(account_invoice, self).action_move_create(cr, uid, ids, context):
            period_obj = self.pool.get('account.period')
            if context is None:
                context = {}
            for inv in self.browse(cr, uid, ids, context):
                tax_period_id = inv.tax_period_id and inv.tax_period_id.id or False
                context.update(company_id = inv.company_id.id,
                               account_period_prefer_normal = True)
                
                if not tax_period_id:
                    if inv.type in ('out_invoice', 'out_refund'):
                        period_ids = period_obj.find(cr, uid, inv.date_invoice, context)
                    else:
                        period_ids = period_obj.find(cr, uid, inv.date_invoice_recieved, context)
                    tax_period_id = period_ids and period_ids[0] or False                
                
                self.write(cr, uid, [inv.id], {'tax_period_id': tax_period_id}, context=None)

                if tax_period_id and inv.move_id:
                    self.pool.get('account.move').write(cr, uid, [inv.move_id.id], {'tax_period_id': tax_period_id}, context)
#                    move_line_ids = self.pool.get('account.move.line').search(cr, uid, [('move_id','=',inv.move_id.id)])
#                    self.pool.get('account.move.line').write(cr, uid, move_line_ids, {'tax_period_id': tax_period_id}, context)
            return True


account_invoice()