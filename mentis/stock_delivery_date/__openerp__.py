# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    
#    Copyright (c) 2013 Mentis d.o.o. (www.mentis.si/openerp). All rights reserved.
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
    'name': 'Delivery/picking date',
    'version': '1.0',
    'license': 'AGPL-3',
    'author': 'Mentis d.o.o.',
    'category': 'Warehouse',
    'description': """ 
    Module prevents change of deliver/picking date to actual in time of process.
    Delivery date is moved to picking header and changed to required.
    """,
    'depends': ['stock'],
    'data' : [
        'stock_picking_in_view.xml',
        'stock_picking_out_view.xml',
    ],
    'active': False,
    'installable': True,
}
