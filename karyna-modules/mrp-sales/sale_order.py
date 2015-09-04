#-*- coding: utf-8 -*-
from openerp.osv import orm, fields


class SaleOrder(orm.Model):

    _inherit = 'sale.order'
    _columns = {
        'production_ids': fields.one2many('mrp.production', 'order_id',
                                          'Production Order'),
        'picking_ids': fields.one2many('stock.picking', 'order_id',
                                       'Picking Order'),
        
    }

    def _prepare_order_picking(self, cr, uid, order, context=None):
        """Overwrite the method and add a field order_id to values."""
        res = super(SaleOrder, self)._prepare_order_picking(cr, uid, order,
                                                            context=context)
        res.update({'order_id': order.id})
        return res

SaleOrder()
