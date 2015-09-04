# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Ecosoft Co., Ltd. (http://ecosoft.co.th).
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
    'name': 'Product Stock Card',
    'version': '1.0',
    'category': 'Warehouse',
    'description': """

Normally, when user want to see the movement of a product, they will use Inventory Move.
Although it give full information about the movement of the product, it is not easy for user to understand quickly.
Stock Card will give the movement view of a product for a location is a simpler way.

For a given location, it gives,
  * In Qty
  * Out Qty
  * Balance

2 ways to use stock card,
  * Open a product, click More > Stock Card, then choose Location and Date Range.
  * New Stock Card menu in Warehouse > Inventory Control > Stock Card, then choose Product, Location and Date Range.

    """,
    'author': 'Ecosoft',
    'website': 'http://www.ecosoft.co.th',
    'depends': ['stock', 'product', 'jasper_reports', 'report_menu_restriction'],
    'data': [
             'product_stock_card_view.xml',
             'wizard/product_stock_card_location_view.xml',
             'security/ir.model.access.csv',
             'product_view.xml',
             'reports.xml',
    ],
    'active': False,
    'installable': True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
