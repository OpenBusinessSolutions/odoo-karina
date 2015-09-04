# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Mentis d.o.o. (<http://www.mentis.si/openerp>).
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

from osv import osv, fields
from tools.sql import drop_view_if_exists

class account_invoice_duplicate_line(osv.Model):
    _name = "account.invoice.duplicate.line"
    _description = "Duplicate Invoice Line"
    _auto = False
    _order = "invoice_id, product_id"
    _columns = {
        'invoice_id': fields.many2one('account.invoice', 'Invoice', readonly=True),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True),
        'product_id': fields.many2one('product.product', 'Product', readonly=True),
        'state':      fields.selection([('draft','Draft'),
                                        ('proforma','Pro-forma'),
                                        ('proforma2','Pro-forma'),
                                        ('open','Open'),
                                        ('paid','Paid'),
                                        ('cancel','Cancelled')], 'Status', readonly=True)        
    }
    
    def init(self, cr):
        drop_view_if_exists(cr, 'account_invoice_duplicate_line')
        cr.execute("""CREATE OR REPLACE VIEW account_invoice_duplicate_line AS
                      (WITH invoices AS (SELECT ail.invoice_id, ail.product_id, ROUND(AVG(ail.price_unit), 4) AS price_avg
                                           FROM account_invoice_line AS ail
                                                INNER JOIN account_invoice AS ai ON ai.id = ail.invoice_id
                                                                                    AND ai.type IN ('out_invoice', 'out_refund')
                                          WHERE ail.product_id IS NOT NULL
                                                AND ail.quantity <> 0.0
                                       GROUP BY ail.invoice_id, ail.product_id
                                         HAVING COUNT(ail.product_id) > 1
                                       ORDER BY ail.invoice_id),
                            in_lines AS (SELECT ai.id AS invoice_id,
                                                ai.partner_id AS partner_id,
                                                ail.product_id AS product_id,
                                                ai.state AS state
                                           FROM account_invoice_line AS ail
                                                INNER JOIN account_invoice AS ai ON ai.id = ail.invoice_id
                                                                                    AND ai.type IN ('out_invoice', 'out_refund')
                                                INNER JOIN invoices AS inv ON inv.invoice_id = ail.invoice_id
                                                                              AND inv.product_id = ail.product_id
                                                                              AND inv.price_avg <> ail.price_unit
                                       GROUP BY ai.id, ai.partner_id, ail.product_id, ai.state)
                         SELECT row_number() OVER (ORDER BY invoice_id, product_id) AS id,
                                invoice_id,
                                partner_id,
                                product_id,
                                state
                           FROM in_lines
                       ORDER BY invoice_id, product_id);""")
