# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Mentis d.o.o. (<http://mentis.si/openerp>).
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
import time

class intrastat_transaction_type(osv.osv):
    _name = "intrastat.transaction.type"
    _description = "Intrastat transaction types"
    
    def _concat_code_name(self, cr, uid, ids, fields, arg, context=None):
        res={}
        for codes in self.browse(cr,uid,ids,context=context):
            res[codes.id] = codes.code + ' ' + codes.short_name
        return res
        
    _columns = {
        'code': fields.char('Transaction Type Code', size=2, required=True),
        'short_name': fields.char('Short description', size=36, required=True),
        'name': fields.function(_concat_code_name, type='char', method=True, string='Description', store=True),
        'full_description': fields.text('Full Description'),
    }
    _order = "code"

intrastat_transaction_type()
