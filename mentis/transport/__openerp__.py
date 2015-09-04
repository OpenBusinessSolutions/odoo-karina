# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
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
    "name": "Manage transportations from suppliers to customers",
    "version": "1.0",
    "author": "Mentis d.o.o.",
    "category": "Sales, Purchases",
    "depends": ['purchase', 'sale'],
    "description": """Manage transportations from suppliers to customers.""",
    "init_xml": [],
    "update_xml": [
	    'transport_view.xml',
        'transport_purchase_report.xml',
        'wizard/customer_report_wiz.xml',
        'res_config_view.xml',
        'security/ir.model.access.csv',
    ],
    "demo_xml": [],
    "active": False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
