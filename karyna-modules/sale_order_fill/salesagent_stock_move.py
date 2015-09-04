#-*- coding: utf-8 -*-
from openerp.osv import orm, fields
from datetime import date


class SalesAgentStockMove(orm.Model):
    """Class description"""

    _name = 'salesagent.stock.move'
    _columns = {
        'line_id': fields.many2one('sale.order.line', 'Order Line'),
        'picking_id': fields.many2one('stock.move', 'Stock Move'),
        'salesagent_id': fields.many2one('res.partner', 'Sales Agent',
                                         domain=[('salesagent', '=', True)]),
        'product_id': fields.many2one('product.product', 'Product'),
        'sale_order': fields.many2one('sale.order', 'Order'),
        'quantity': fields.float('Qty', digits=(16, 2)),
        'date_order': fields.date('Date', required=True, readonly=True,
                                  select=True),
    }

    _defaults = {
        'date_order': date.today().isoformat()
    }