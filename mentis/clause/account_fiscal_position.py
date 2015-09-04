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

class account_fiscal_position(osv.osv):
    _inherit = 'account.fiscal.position'
    
    def _get_clause_id(self, cr, uid, *args):
        cr.execute('select id from clause order by id limit 1')
        res = cr.fetchone()
        return res and res[0] or False
    
    _columns = {
        'default_clause': fields.many2one('clause', 'Default Clause', required=True, help="Clause to be written on output documents when there is no other clause set on partner."),
    }
    _defaults = {
        'default_clause': _get_clause_id,
    }

account_fiscal_position()
