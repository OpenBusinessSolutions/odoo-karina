﻿# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 CodUP (<http://codup.com>).
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
    'name': 'Assets & Purchase',
    'version': '1.1',
    'summary': 'Integrate Asset and Purchase',
    'description': """
Integrate Maintenance and Purchase.
===========================

This module allows use the same Assets for purchase and maintenance purposes.
Keep one entity in one place for escape mistakes!
    """,
    'author': 'CodUP',
    'website': 'http://codup.com',
    'images': ['static/description/icon.png'],
    'category': 'Enterprise Asset Management',
    'sequence': 0,
    'depends': ['purchase','asset'],
    'demo': ['asset_demo.xml'],
    'data': [
        'security/ir.model.access.csv',
        'purchase_view.xml'
    ],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: