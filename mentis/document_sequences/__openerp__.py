# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    
#    Copyright (c) 2012 Mentis d.o.o.
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
    'name': 'Document lines sequences',
    'version': '1.0',
    'license': 'AGPL-3',
    'author': 'Mentis d.o.o.',
    'category': 'Accounting,Purchase',
    'description': """ 
    Module adds sequence field on purchase order and invoice lines.
    Sequence can be set with line dragging.
    """,
    'depends': ['account','purchase'],
    'data' : [
        'account_invoice_view.xml',
        'purchase_order_view.xml',
    ],
    'active': False,
    'installable': True,
}
