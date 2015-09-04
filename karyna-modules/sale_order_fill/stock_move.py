#-*- coding: utf-8 -*-
from openerp.osv import orm, fields


class StockMove(orm.Model):
    """Class description"""

    _inherit = 'stock.move'

    _columns = {
        # 'salesagent_ids': fields.one2many('salesagent.stock.move',
        #                                   'picking_id', 'Salesagents'),
        'product_qty_available': fields.related('product_id', 'qty_available', type='float', string='Quantity On Hand', 
                                                 store=False, readonly=True),
    }
    
    def get_quantity(self, cr, uid, ids, context=None):
        """Calculate the quantity based on all the quantities of the related
        salesagent quantities."""
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            if not line.salesagent_ids:
                break
            quantity = 0.0
            for agent in line.salesagent_ids:
                quantity += agent.quantity
            res[line.id] = quantity
        return res
    
    #~ def write(self, cr, uid, ids, values, context=None):
        #~ """Overwrite the write method and add all the quantities from
        #~ the salesagent"""
        #~ new_quantity = self.get_quantity(cr, uid, ids,
                                         #~ context=context)
        #~ for move in ids:
            #~ values.update({'product_qty': new_quantity.get(move),
                           #~ 'product_uos_qty': new_quantity.get(move)})
        #~ return super(StockMove, self).write(cr, uid, ids, values,
                                            #~ context=context)
    #~ 
    #~ def create(self, cr, uid, values, context=None):
        #~ """Overwrite the create method and add all the quantities from
        #~ the salesagent."""
        #~ agent_obj = self.pool.get('salesagent.order.line')
        #~ #Access the one2many field
        #~ #salesagent_ids value is of format [(6, 0, [#, #])]
        #~ if 'salesagent_ids' in values.keys():
            #~ new_quantity = 0.0
            #~ for agent in values.get('salesagent_ids'):
                #~ new_quantity += agent[2].get('quantity')
            #~ values.update({'product_qty': new_quantity,
                          #~ 'product_uos_qty': new_quantity})
        #~ return super(StockMove, self).create(cr, uid, values,
                                             #~ context=context)
    
StockMove()
