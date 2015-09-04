#-*- coding: utf-8 -*-
from openerp.osv import orm, fields


class StockPickingOut(orm.Model):

    _inherit = 'stock.picking'
    _columns = {
        'order_id': fields.many2one('sale.order', 'Sale Order', readonly=True)
    }
