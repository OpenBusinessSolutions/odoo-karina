# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Mentis d.o.o. All rights reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Sale Order reference number - RF",
    "version": "1.0",
    "author": "Mentis d.o.o.",
    "category": "Sales",
    "depends": ['sale'],
    "description": """Calculates sale order reference number-RF from order number.""",
    "init_xml": [],
    "update_xml": ['sale_order_reference_view.xml'],
    "demo_xml": [],
    "active": False,
    "installable": True,
}


