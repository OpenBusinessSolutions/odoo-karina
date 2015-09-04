# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Mentis d.o.o. (<http://www.mentis.si>)
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
    "name": "Change quantity of products on Manufacturing order and Procurement",
    "version": "1.0",
    "author": "Mentis d.o.o.",
    "category": "Accounting",
    "depends": ['mrp', 'procurement', 'sale', 'stock', 'stock_return_on_delivery', 'sale_order_extensions', 'sale_stock'],
    "description": """ Change quantity of products on Manufacturing order and Procurement
    Disables Quotation confirmation and adds a new menu for Quotation confirmation
    New menu for Procurement running multiple times

    Merging Invoice Lines from Delivery Orders
	
	
	""",
    "init_xml": [],
    "update_xml": [
	    'wizard/mrp_procurement_qty_view.xml',
        'wizard/sale_order_view.xml',
        'wizard/procurement_order_view.xml',
		'account_invoice_view.xml',
		'procurement_view.xml',
        'wizard/delivery_order_chginvoice_state_view.xml',
		'wizard/sale_order_journal_view.xml',
        'stock_view.xml',
        'sale_view.xml',
		'wizard/delivery_order_return_view.xml',
        'wizard/delivery_order_confirm_view.xml',
		'security/ir.model.access.csv',
        'mrp_production_view.xml',
        'wizard/procurement_order_from_op_view.xml',
        'wizard/procurement_order_move_stock_view.xml',
        'bakery_production_view.xml',
        'res_config_view.xml',
    ],
    "demo_xml": [],
    "active": False,
    "installable": True,
}
