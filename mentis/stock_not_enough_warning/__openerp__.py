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
    "name": "Disables warning 'Not enough stock !'",
    "version": "1.0",
    "author": "Mentis d.o.o.",
    "category": "Sale Orders",
    "depends": ['sale_stock'],
    "description": """Disables warning 'Not enough stock !' for product that has 'make to stock' procure method and not enough quantity.""",
    "init_xml": [],
    "update_xml": [],
    "demo_xml": [],
    "active": False,
    "installable": True,
}
