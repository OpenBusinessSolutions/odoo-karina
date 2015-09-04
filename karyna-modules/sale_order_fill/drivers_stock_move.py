#-*- coding: utf-8 -*-
from openerp.osv import orm, fields


class DriversStockMove(orm.Model):
    """Class description""" 

    _name = 'drivers.stock.move'
    _table = 'drivers_stock_move'
    _columns = {
        'line_id': fields.many2one('sale.order.line', 'Order Line'),
        'picking_id': fields.many2one('stock.picking', 'Stock Picking'),
        'product_id': fields.many2one('product.product', 'Product'),
        'order_total': fields.float('Order Total', digits=(16, 2)),
        'quantity_hand': fields.related('product_id', 'qty_available',
                                        type='float',
                                        string='Quantity on Hand'),
        'driver_1': fields.float('Driver 1', digits=(16, 2)),
        'driver_2': fields.float('Driver 2', digits=(16, 2)),
        'driver_3': fields.float('Driver 3', digits=(16, 2)),
        'driver_4': fields.float('Driver 4', digits=(16, 2)),
        'driver_5': fields.float('Driver 5', digits=(16, 2)),
        'driver_6': fields.float('Driver 6', digits=(16, 2)),
        'driver_7': fields.float('Driver 7', digits=(16, 2)),
        'driver_8': fields.float('Driver 8', digits=(16, 2)),
        'driver_9': fields.float('Driver 9', digits=(16, 2)),
        'driver_10': fields.float('Driver 10', digits=(16, 2)),
        'driver_11': fields.float('Driver 11', digits=(16, 2)),
        'driver_12': fields.float('Driver 12', digits=(16, 2)),
        'driver_13': fields.float('Driver 13', digits=(16, 2)),
        'driver_14': fields.float('Driver 14', digits=(16, 2)),
        'driver_15': fields.float('Driver 15', digits=(16, 2)),
        'date_order': fields.date('Date', required=True, readonly=True,
                                  select=True),
    }

    def onchange_total(self, cr, uid, ids, context=None, *args):
        """Calculate the total cost of quantity per driver."""
        res = {}
        for order in self.browse(cr, uid, ids, context):
            total = 0
            for driver in args:
                total += driver
            res['value'] = {'order_total': total}
        return res
    '''
    def onchange_total(self, cr, uid, ids, context=None, *args):
        """Calculate the total cost of quantity per driver."""
        line_obj = self.pool.get('sale.order.line')
        res = {}
        for order in self.browse(cr, uid, ids, context):
            total = 0
            for driver in args:
                total += driver
            res['value'] = {'order_total': total}
            line_obj.write(cr, uid, order.line_id.id, {'product_uom_qty': total,
                           }, context)
        return res
    '''