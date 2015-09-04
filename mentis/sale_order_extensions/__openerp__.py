# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP s.a. (<http://www.openerp.com>).
#    Copyright (C) 2013-TODAY Mentis d.o.o. (<http://www.mentis.si/openerp>)
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
    'name': 'Sale Order Extensions',
    'version': '1.5',
    'category': 'Sale',
    'description': """
    This module adds following extensions to Sale Order: \n
    - adds new state 'prepared' which is positioned between existing 'draft' and 'sent' states \n
    - adds functionality to return order from state 'prepared' to state 'draft' \n
    - adds method to check if all prices on order are set \n
    - when user changes date prices are updated according to pricelist if needed \n
    - when user changes date it gets saved as user default for new created orders \n
    - automaticly updates prices when duplicating sale order based on user default date \n
    - adds field shop_production on shop for filtering shops \n
    - adds quotations view for quotations from production shop with less fields \n
    - adds quantity returned on sale order line for automatic product returns \n
    - adds sale price functionality on partners and products \n
    - adds sale order unit price recalculation method \n
    """,
    'author': 'Mentis d.o.o.',
    'depends': ['sale_stock'],
    'data': [
        'product_product_view.xml',
        'res_partner_view.xml',
        'sale_shop_view.xml',
        'sale_order_view.xml',
        'sale_order_workflow.xml',
        'wizard/sale_order_recalculation.xml'
    ],
    'installable': True,
    'active': False,
}
