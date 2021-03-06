# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

class sale_order(osv.osv):
    _inherit = "sale.order"
    
    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        result = super(sale_order, self).onchange_partner_id(cr, uid, ids, part)
        if not part:
            return result
        
        _clause_id = False;
        _partner = self.pool.get('res.partner').browse(cr, uid, part) 
        if _partner.default_clause:
            _clause_id = _partner.default_clause.id
        else:
            _fiscal_position_id = result['value']['fiscal_position'] 
            if _fiscal_position_id:
                _fiscal_position = self.pool.get('account.fiscal.position').browse(cr, uid, _fiscal_position_id)                    
                if _fiscal_position.default_clause:
                    _clause_id = _fiscal_position.default_clause.id
        if _clause_id:
            result['value']['clause_ids'] = [_clause_id]
        else:
            result['value']['clause_ids'] = []
        return result
    
    _columns = {
        'clause_ids': fields.many2many('clause', 'sale_order_clause', 'order_id', 'clause_id', 'Clauses'),
    }

sale_order()