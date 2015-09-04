# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2012 OpenERP s.a. (<http://www.openerp.com>).
#    Copyright (C) 2012 Mentis d.o.o. (<http://www.mentis.si>)
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


{
    'name': 'Clauses',
    'version': '1.0',
    'category': 'General',
    'description': """
    This module adds clauses to documents.
    
    """,
    'author': 'Mentis d.o.o.',
    'depends': ['account','sale'],
    'init_xml': [
            'data/clause.xml',
    ],
    'data': [
             'clause_view.xml',
             'account_fiscal_position_view.xml',
             'res_partner_view.xml',
             'account_invoice_view.xml',
             'sale_order_view.xml',
             'security/ir.model.access.csv',
    ],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
