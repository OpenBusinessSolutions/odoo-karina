# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2013 OpenERP s.a. (<http://www.openerp.com>).
#    Copyright (C) 2013 Mentis d.o.o. (<http://www.mentis.si/openerp>)
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

from osv import fields, osv
from lxml import etree

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"

    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        res = super(account_invoice_line, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        if context and context.get('type', False):
            for node in doc.xpath("//field[@name='account_analytic_id']"):
                node.set('modifiers', '{"required": true}')
            for node in doc.xpath("//field[@name='analytics_id']"):
                node.set('modifiers', '{"required": true}')
            for node in doc.xpath("//field[@name='invoice_line_tax_id']"):
                node.set('modifiers', '{"required": true}')

            res['arch'] = etree.tostring(doc)
        
        return res