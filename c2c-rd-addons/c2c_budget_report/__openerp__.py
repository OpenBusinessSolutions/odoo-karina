# -*- coding: utf-8 -*- 
##############################################################################
#
# Copyright (c) Camptocamp SA - http://www.camptocamp.com
# Author: Arnaud WÃŒst ported by nbessi
#
#    This file is part of the c2c_budget_chricar module
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
{ 'sequence': 500,
"name" : "Advanced Budget Webkit Report"
, "version" : "6.1"
, "author" : "ChriCar Beteiligungs- und Beratungs- GmbH"
, "category" : "Generic Modules/Accounting"
, "website" : "http://camptocamp.com"
, "description": """
Budget Module:
    * Webkit report compares real to budget

"""
, "depends" : 
[ "c2c_budget_chricar","chricar_account_period_sum",
]
, "init_xml" : []
, "data" : 
[ "security/ir.model.access.csv"
, "report_chart.xml"
, "wizard/chart.xml"
]
, "auto_install": False
, 'installable': False
, 'application'  : False
}
