# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Mentis d.o.o. (<http://www.mentis.si>)
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
    "name": "Receivables & Payables card of customer",
    "version": "1.0",
    "author": "Mentis d.o.o.",
    "category": "Accounting",
    "depends": ['account'],
    "description": """ Receivables & Payables card of customer
	
	""",
    "init_xml": [],
    "update_xml": [
	    'wizard/rec_pay_wizard_view.xml',
    ],
    "demo_xml": [],
    "active": False,
    "installable": True,
}
