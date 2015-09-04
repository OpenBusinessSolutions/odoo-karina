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

from openerp.osv import fields, osv

class account_balance_report(osv.osv_memory):
    _inherit = "account.common.account.report"
    _name = 'account.balance.report.mentis'
    _description = 'Trial Balance Report with Opening'

    _columns = {
        'journal_ids': fields.many2many('account.journal', 'account_balance_report_journal_rel', 'account_id', 'journal_id', 'Journals', required=True),
        'account_ids': fields.many2one('account.account', 'Account', domain=[('level', '=', 1)]),
    }

    _defaults = {
        'journal_ids': [],
    }

    def _print_report(self, cr, uid, ids, data, context=None):
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        
        account_ids = self.browse(cr,uid,ids)[0].account_ids
        if account_ids:
            data['form']['account_id'] = [account_ids.id]
        
        return {'type': 'ir.actions.report.xml', 'report_name': 'account.account.balance.mentis', 'datas': data}

account_balance_report()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
