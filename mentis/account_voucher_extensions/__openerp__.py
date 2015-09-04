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


{
    'name': 'Account Voucher Extensions',
    'version': '1.0',
    'category': 'Accounting',
    'description': """
Account Voucher Extensions
==========================
This module adds or changes next functionality:
    
* Import Invoices wizard on Bank Statements (domain reconcile_partial_id removed)
* Allocation wizard on Bank Statements no more reloads for times (option to disable auto allocation)
* Amount sum on Bank Statements
    
    """,
    'author': 'Mentis d.o.o.',
    'depends': ['account_voucher'],
    'init_xml': [],
    'data': [
             'account_voucher_extensions_view.xml',
    ],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
