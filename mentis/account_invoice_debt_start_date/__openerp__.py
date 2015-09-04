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
    'name': 'Invoice Start Debt Relation Date',
    'version': '1.1',
    'category': 'Accounting',
    'description': """
    This module adds two new date fields on invoice.
    
    According to Slovenian legislation old 'invoice_date' field on invoice acts
    as start debt relation date, while new 'invoice_date_creation' field serves as
    date of invoice.
    New field 'invoice_date_recieved' also exist on supplier invoices.
    """,
    'author': 'Mentis d.o.o.',
    'depends': ['account'],
    'init_xml': [],
    'update_xml': ['account_invoice_view.xml',
                   ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
