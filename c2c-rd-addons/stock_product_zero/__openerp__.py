# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 ChriCar Beteiligungs- und Beratungs- GmbH (<http://www.camptocamp.at>)
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


{ 'sequence': 500,

'name': 'Stock suppress all zero lines',
'version': '0.7',
'category': 'Warehouse Management',
'description': """
This module will not print/display products with zero quantity values in many reports and tree lists.
Especially important if the company has a lot of locations with a very limited number of products
like consignations locations at supplieres or customers
Adds a nice inventory report based on webkit

""",
'author': 'ChriCar Beteiligungs- und Beratungs- GmbH',
'depends': [ 'stock','one2many_sorted',"report_webkit" ],
'data': ['stock_view.xml','inventory_view.xml','stock_inventory_webkit.xml',
  ],
#'data': ['product_view.xml'],
'demo_xml': [],
'installable': False,
'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
