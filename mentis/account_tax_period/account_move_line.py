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

class account_move_line(osv.osv):
    _inherit = 'account.move.line'

    def _default_get(self, cr, uid, fields, context=None):
        data = super(account_move_line, self)._default_get(cr, uid, fields, context=context)
        if context.get('date', False):
            data['date'] = context['date']
        return data
        
        
    def _get_move_lines(self, cr, uid, ids, context=None):
        result = []
        for move in self.pool.get('account.move').browse(cr, uid, ids, context=context):
            for line in move.line_id:
                result.append(line.id)
        return result

    def _get_tax_period(self, cr, uid, context=None):
        """
        Return  default account period value
        """
        context = context or {}
        if context.get('tax_period_id', False):
            return context['tax_period_id']
        account_period_obj = self.pool.get('account.period')
        ctx = dict(context, account_period_prefer_normal=True)
        ids = account_period_obj.find(cr, uid, context=ctx)
        tax_period_id = False
        if ids:
            tax_period_id = ids[0]
        return tax_period_id
    
    _columns = {
        'tax_period_id': fields.related('move_id', 'tax_period_id', string='Tax Period', type='many2one', relation='account.period', select=True,
                                        store = {
                                            'account.move': (_get_move_lines, ['tax_period_id'], 20)
                                        }),
        
    }
    _defaults = {
        'tax_period_id': _get_tax_period
    }
    
account_move_line()