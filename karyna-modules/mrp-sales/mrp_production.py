#-*- coding: utf-8 -*-
from openerp.osv import orm, fields
import pdb

class MrpProduction(orm.Model):

    _inherit = 'mrp.production'
    _columns = {
        'order_id': fields.many2one('sale.order', 'Sale Order', readonly=True)
    }


class Procurement(orm.Model):

    _inherit = 'procurement.order'

    def make_mo(self, cr, uid, ids, context=None):

        """Overwrite method to add linked sale.order id for many2one field.
        @return: dict of procurement_id: created_order_id
        """
        mrp_obj = self.pool.get('mrp.production')
        sale_obj = self.pool.get('sale.order')
        res = super(Procurement, self).make_mo(cr, uid, ids, context=context)
        for proc_id in res:
            order = mrp_obj.browse(cr, uid, res.get(proc_id), context=context)
            #sale = sale_obj.search(cr, uid, [('name', '=', order.origin[0:19])],
            #                       limit=1, context=context)
            sale = sale_obj.search(cr, uid, [('name', '=', order.sale_name)],
                                   limit=1, context=context)
            if sale:
                mrp_obj.write(cr, uid, res.get(proc_id), {'order_id': sale[0]})
        return res

Procurement()
