# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
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
#################################################################################

{
    "name" : "Invoice blocked if Follow Up",
    "version" : "1.0",
    "author" : "Julius Network Solutions",
    "website" : "http://julius.fr",
    "category" : "Accounting & Finance",
    "depends" : [
        'account',
        'account_followup',
    ],
    "description": """
    This module will block invoice validation if the partner got a current
    follow up. A financial validator will be able to unlock this invoice.
    """,
    "demo" : [],
    "data" : [
        'security/group.xml',
        'account_followup.xml',
        'account_invoice_workflow.xml',
    ],
    'installable' : False,
    'active' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
