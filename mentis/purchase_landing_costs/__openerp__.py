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
    'name': 'Purchase Landing Costs',
    'version': '1.1',
    'category': 'Warehouse Management',
    'description': """
    This module extends average price computation with landing costs definition 
    
    The landed costs can be defined for purchase orders and/or stock pickings
    and are distributed through per value or per unit method.
    """,
    'author': 'Mentis d.o.o.',
    'depends': ['purchase'],
    'init_xml': [],
    'update_xml': ['security/ir.model.access.csv',
                   'product_template_view.xml',
                   'purchase_order_view.xml',
                   'stock_picking_in_view.xml',
                   #'stock_move_landing_costs_view.xml',
                   ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
