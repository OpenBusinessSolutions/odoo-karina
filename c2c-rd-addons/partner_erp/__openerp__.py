# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

"name" : "Partner ERP Access",
"version" : "1.0",
"author" : "ChriCar Beteiligungs- und Beratungs- GmbH",
"category": 'Project',
'complexity': "easy",
"description": """
ERP Access Data for Clients
""",
'website': 'http://www.camptocamp.com',
"depends" : ["base"],
'init_xml': [],
'data': ['partner_view.xml', 'security/group.xml', 'security/ir.model.access.csv','security/partner_erp_security.xml'],
'demo_xml': [],
'installable': False,
'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
