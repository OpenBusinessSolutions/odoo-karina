#-*- coding: utf-8 -*-
from openerp.osv import orm, fields
import logging


class DriversOrderLines(orm.Model):
    """Class description""" 
    
    _name = 'drivers.order.line'

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

    _columns = {
        'line_id': fields.many2one('sale.order.line', 'Order Line'),
        'picking_id': fields.many2one('stock.move', 'Stock Move'),
        'product_id': fields.many2one('product.template', 'Product'),
        'order_total': fields.float('Order Total', digits=(16, 2)),
        'sale_order': fields.many2one('sale.order', 'Order'),
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

    def create(self, cr, uid, values, context=None):
        """Overwrite create method to access data from order.line model."""
        line_obj = self.pool.get('sale.order.line')
        line_id = line_obj.search(cr, uid, [('order_id','=',
                                  values.get('sale_order')),('product_id','=',
                                  values.get('product_id'))], context=context)
        try:
            line = line_obj.browse(cr, uid, line_id[0], context)
            values.update({'product_id': line.product_id.id,
                          'sale_order': line.order_id.id,
                          'line_id': line.id})
        except IndexError, e:
            raise orm.except_orm('Error', e.message)
        finally:
            return super(DriversOrderLines, self).create(cr, uid, values, context)

    _defaults = {
        'date_order': fields.date.context_today,
    }

DriversOrderLines()


class OrderLine(orm.Model):

    _inherit = 'sale.order.line'

    def get_quantity(self, cr, uid, values, context=None):
        """Calculate the quantity based on all the quantities of the related
        salesagent quantities.

        params: values; dict of fields

        return: quantity; float, new amount for field product_uom_qty"""
        salesagent_obj = self.pool.get('salesagent.order.line')
        if 'salesagent_ids' in values.keys():
            log = logging.getLogger(self._name)
            quantity = 0.0
            #salesagent_ids value format is [[#, #, {'quantity':#}]]
            for agent in values.get('salesagent_ids'):
                try:
                    quantity += agent[2].get('quantity')
                except AttributeError:
                    log.info("Catched exception for a False value.")
                    quantity += salesagent_obj.browse(cr, uid, agent[1],
                                                    context).quantity
            return quantity
        else:
            return False

    def write(self, cr, uid, ids, values, context=None):
        """Overwrite the write method and add all the quantities from
        the salesagent"""
        new_quantity = self.get_quantity(cr, uid, values, context=context)
        if new_quantity:
            values.update({'product_uom_qty': new_quantity,
                          })
        return super(OrderLine, self).write(cr, uid, ids, values,
                                            context=context)

    def create(self, cr, uid, values, context=None):
        """Overwrite the create method and add all the quantities from
        the salesagent."""
        new_quantity = 0.0
        #Access the one2many field
        for agent in values.get('salesagent_ids', []):
            try:
                new_quantity += agent[2].get('quantity')
                values.update({'product_uom_qty': new_quantity,
                              })
            #If we get this error means the salesagents are already created
            #so there is no need to add quantities.
            except AttributeError:
                break
        return super(OrderLine, self).create(cr, uid, values, context=context)

    def sack_yield(self, cr, uid, ids, field_name, args, context=None):
        """Calculate the amount of sacks required for this sale order."""
        res = {}
        for order in self.browse(cr, uid, ids, context):
            if not order.product_id.yield_sack:
                return res
            else:
                sack_amt = order.product_uom_qty / order.product_id.yield_sack
                res.update({order.id: sack_amt})
        return res

    def onchange_sacks_quantity(self, cr, uid, ids, product_packaging,
                                sacks_quantity, context=None):
        """Method to establish the suggested_quantity quantity according to
        the product quantity."""
        pack_obj = self.pool.get('product.packaging')
        res = {}
        for line in self.browse(cr, uid, ids, context):
            pack = pack_obj.browse(cr, uid, product_packaging, context)
            sack_yield = line.product_id.yield_sack
            suggested_quantity = sacks_quantity * sack_yield
            if product_packaging:
                if not (suggested_quantity % pack.qty):
                    res.update({'warning': {'title': 'Error',
                               'message': 'Packaging amount leaves'
                                         ' some product out.'}})
            res.update({'value':{'suggested_quantity': suggested_quantity,
                                 'product_uom_qty': suggested_quantity,
                                 }})
            return res

    _columns = {
        'salesagent_ids': fields.one2many('salesagent.order.line', 'line_id',
                                          'Sales Agent'),
        #'drivers_order_lines_ids': fields.one2many('drivers.order.line', 'line_id',
        #                                  'Drivers Order Line'),
        'sacks_quantity': fields.function(sack_yield, type='float',
                                          store=True, readonly=False),
        'suggested_quantity': fields.float('Suggested Quantity',
                                           digits=(16, 2), readonly=True),
        'product_qty_available': fields.related('product_id', 'qty_available', type='float', string='Quantity On Hand', store=True, readonly=True),
    }

OrderLine()


class MrpSackQty(orm.Model):

    def _sack_qty(self, cr, uid, ids, field_name, args, context=None):
        """Calculate the amount of sacks required for this manufacturing order."""
        res = {}
        for mrp in self.browse(cr, uid, ids, context):
            if not mrp.product_id.yield_sack:
                return res
            else:
                sack_amt = mrp.product_qty / mrp.product_id.yield_sack
                res.update({mrp.id: sack_amt})
        return res

    def onchange_sacks_quantity(self, cr, uid, ids, sacks_quantity, product_id, context=None):
        res = {}

        if not product_id:
            res.update({'warning': {'title': 'Warning',
                               'message': 'No product selected'
                                         ' to calculate sacks sugested amount. Please select a product first'}})
            return res

        if sacks_quantity:
            prod = self.pool.get('product.template').browse(cr, uid, product_id, context=context)
            sack_yield = prod.yield_sack
            if sack_yield == 0:
                res.update({'warning': {'title': 'Warning',
                               'message': 'The selected product does not have a sack yield value. Unable to calculate sack sugested amount. Please modify product first'}})
                return res

            suggested_quantity = sacks_quantity * sack_yield
            return {'value': 
            {'product_uom_qty': suggested_quantity,
            } }
            return res

    _inherit = 'mrp.production'
    _columns = {
        'sacks_quantity': fields.function(_sack_qty, 'Sack Quantity', type='float',
                                          store=True, readonly=True),
    }
    
MrpSackQty()


class MrpBomSackQty(orm.Model):

    def _sack_qty(self, cr, uid, ids, field_name, args, context=None):
        """Calculate the amount of sacks required for this mrp bom"""
        res = {}
        for bom in self.browse(cr, uid, ids, context):
            if not bom.product_id.yield_sack:
                return res
            else:
                sack_amt = bom.product_qty / bom.product_id.yield_sack
                res.update({bom.id: sack_amt})
        return res

    def onchange_sacks_quantity(self, cr, uid, ids, sacks_quantity, product_id,
                                context=None):
        res = {}

        if not product_id:
            res.update({'warning': {'title': 'Warning',
                               'message': 'No product selected'
                                         ' to calculate sacks sugested amount. Please select a product first'}})
            return res

        if sacks_quantity:
            prod = self.pool.get('product.template').browse(cr, uid, product_id, context=context)
            sack_yield = prod.yield_sack
            if sack_yield == 0:
                res.update({'warning': {'title': 'Warning',
                               'message': 'The selected product does not have a sack yield value. Unable to calculate sack sugested amount. Please modify product first'}})
                return res
            suggested_quantity = sacks_quantity * sack_yield
            return {'value': {'product_uom_qty': suggested_quantity} }
            return res
    
    _inherit = 'mrp.bom'
    _columns = {
        'sacks_quantity': fields.function(_sack_qty, 'Sack Quantity', type='float',
                                          store=True, readonly=True),
    }
    
MrpBomSackQty()

