#-*- coding: utf-8 -*-
from openerp.osv import orm, fields


class StockPicking(orm.Model):
    """Class description"""

    _inherit = 'stock.picking'
    _columns = {
        'drivers_order_ids': fields.one2many('drivers.stock.move',
                                             'picking_id',
                                             'Sales Agent'),
    }
