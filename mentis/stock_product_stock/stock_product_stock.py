# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP s.a. (<http://www.openerp.com>)
#    Copyright (C) 2014-TODAY Mentis d.o.o. (<http://www.mentis.si/openerp>)
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
from decimal_precision import decimal_precision as dp
import time

class stock_product_stock(osv.osv):
    _name = "stock.product.stock"
    _description = "Product Stock And Costs on Date"
    _auto = False
    _order = "product_id"
    _columns = {
        'product_id': fields.many2one('product.product', 'Product', readonly=True),
        'categ_id': fields.many2one('product.category', 'Category', readonly=True),
        'location_id': fields.many2one('stock.location', 'Location', readonly=True),
        'price_unit': fields.float('Unit Price', digits_compute=dp.get_precision('Product Price'), readonly=True),
        'qty_stock': fields.float('Quantity On Stock', digits_compute=dp.get_precision('Product Unit of Measure'), readonly=True)
    }
    
    def init(self, cr):
        drop_view_if_exists(cr, 'stock_product_moves')
        cr.execute("""CREATE OR REPLACE VIEW stock_product_moves AS
                      (SELECT sm.id AS id,
                              sm.product_id AS product_id,
                              sp.id AS picking_id,
                              sm.date AS date,
                              pa.id AS partner_id,
                              CASE
                                WHEN sp.type = 'in'
                                  THEN pai.id
                                WHEN sp.type = 'out'
                                  THEN sai.id
                                ELSE NULL
                              END AS invoice_id,
                              CASE
                                WHEN sp.type = 'in'
                                     OR sp.id IS NULL
                                  THEN sm.product_qty
                                ELSE NULL
                              END AS qty_received,
                              CASE
                                WHEN sp.type = 'out'
                                  THEN sm.product_qty
                                ELSE NULL
                              END AS qty_delivered,
                              (SELECT SUM(CASE
                                            WHEN sp1.type = 'in'
                                                 OR sp1.id IS NULL
                                              THEN sm1.product_qty
                                            ELSE sm1.product_qty * -1
                                          END)
                                 FROM stock_move AS sm1
                                      LEFT OUTER JOIN stock_picking AS sp1 ON sp1.id = sm1.picking_id
                                WHERE sm1.product_id = sm.product_id
                                      AND sm1.state = 'done'
                                      AND sm1.date <= sm.date) AS qty_stock,
                              sm.price_unit AS price_unit,
                              sm.product_qty * sm.price_unit AS amount
                         FROM stock_move AS sm
                              LEFT OUTER JOIN res_partner AS pa ON pa.id = sm.partner_id
                              LEFT OUTER JOIN stock_picking AS sp ON sp.id = sm.picking_id
                              LEFT OUTER JOIN sale_order_line_invoice_rel AS solir ON solir.order_line_id = sm.sale_line_id
                              LEFT OUTER JOIN purchase_order_line_invoice_rel AS polir ON polir.order_line_id = sm.purchase_line_id
                              LEFT OUTER JOIN account_invoice_line AS sail ON sail.id = solir.invoice_id
                              LEFT OUTER JOIN account_invoice AS sai ON sai.id = sail.invoice_id
                              LEFT OUTER JOIN account_invoice_line AS pail ON pail.id = polir.invoice_id
                              LEFT OUTER JOIN account_invoice AS pai ON pai.id = pail.invoice_id
                        WHERE sm.state = 'done');""")
