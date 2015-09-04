# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2012 OpenERP s.a. (<http://www.openerp.com>).
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
    'name': 'Account Tax Period',
    'version': '1.1',
    'category': 'Accounting',
    'description': """
    This module adds separate tax period on invoices and account moves and
    modifies tax chart and report to use that period.
    """,
    'author': 'Mentis d.o.o.',
    'depends': ['account', 'account_invoice_debt_start_date'],
    'data': [
        'account_invoice_view.xml',
        'account_move_view.xml',
        'account_move_line_view.xml',
        'account_tax_chart_view.xml'
    ],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
