# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP s.a. (<http://www.openerp.com>).
#    Copyright (C) 2012-TODAY Mentis d.o.o. (<http://www.mentis.si/openerp>)
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
    'name': 'Return Goods On Delivery',
    'version': '1.1',
    'category': 'Warehouse',
    'description': """
    Module adds option to return goods on delivery order after it was already confirmed.
    """,
    'author': 'Mentis d.o.o.',
    'depends': ['stock','purchase_recalculation'],
    'data': [
        'stock_picking_out_return_form.xml',
        'stock_partial_return_view.xml',
        'res_config_view.xml'
    ],
    'installable': True,
    'active': False,
}
