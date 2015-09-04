#-*- coding: utf-8 -*-
from openerp.osv import orm, fields
import datetime

class AgentOrderLine(orm.Model):
    """Class description""" 

    _name = 'salesagent.order.line'
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

    def create(self, cr, uid, values, context=None):
        """Overwrite create method to access data from order.line model."""
        line_obj = self.pool.get('sale.order.line')
        line = line_obj.browse(cr, uid, values.get('line_id'), context)
        try:
            values.update({'product_id': line.product_id.id,
                          'sale_order': line.order_id.id,
                          'date_order': line.order_id.date_order.date()})
        except AttributeError, e:
            pass
        finally:
            return super(AgentOrderLine, self).create(cr, uid, values, context)

    _defaults = {
        #'date_order': fields.date.context_today,
    }