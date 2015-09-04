# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2011 Acysos S.L. (http://acysos.com) All Rights Reserved.
#                       Ignacio Ibeas <ignacio@acysos.com>
#    $Id$
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
    "name" : "MRP Operator",
    "version" : "1.0",
    "author" : "Acysos S.L.",
    "website" : "www.acysos.com",
    "category": "Generic Modules/Production",
    "description": """Assign to the manufacturing order the operator that have produced the product. Registry products produced by operator. 
    Sponsored by Gatakka and Polux""",
    "license" : "AGPL-3",
    "depends" : ["base", "mrp", "hr","stock"],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" :["mrp_operator_view.xml","mrp_operator_registry_sequence.xml","mrp_production_view.xml"],
    "active": False,
    "installable": True
}