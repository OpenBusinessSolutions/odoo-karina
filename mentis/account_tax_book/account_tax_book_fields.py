# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Mentis d.o.o. (<http://www.mentis.si>)
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

class account_tax_book_fields(osv.osv):
    _description = 'Tax book fields'
    _name = 'account.tax.book.fields'
    _columns = {
	    'name': fields.char('Field description', required=True, size=128),
        'position': fields.char('Column', required=True, size=8),
	}
account_tax_book_fields()

class account_tax(osv.osv):
    _inherit = 'account.tax.code'
    _columns = {
        'tax_book_issued_colums_id': fields.many2many('account.tax.book.fields', 'account_tax_book_fields_issued_tax_code_rel', 'tax_code_id', 'tax_book_fields_id', 'Tax records issued columns'),
        'tax_book_received_colums_id': fields.many2many('account.tax.book.fields', 'account_tax_book_fields_received_tax_code_rel', 'tax_code_id', 'tax_book_fields_id', 'Tax records received columns'),
    }
account_tax()
    

