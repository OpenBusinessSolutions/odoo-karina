#-*- coding: utf-8-*-
from openerp.osv import orm, fields
import pdb

class SaleOrder(orm.Model):

    _inherit = 'sale.order'
    _auto = True

    def fill_sale_order(self, cr, uid, ids, context=None):
        """Pass the order id to a wizard to retrieve a list of
        product categories for setting a default list of products."""
        action_obj = self.pool.get('ir.actions.act_window')
        view_obj = self.pool.get('ir.ui.view')
        #Defensive programming.
        if len(ids) > 1:
            raise orm.except_orm("ERROR","You tried to pass more than one order.")
        action_id = action_obj.search(cr, uid, [('name','=','Fill Sale Products'),
                                      ('res_model','=','sale.order.fill')],
                                      limit=1, context=context)
        view_id = view_obj.search(cr, uid, [('name','=','sale.order.fill.view'),
                                  ('model','=','sale.order.fill')], limit=1,
                                  context=context)
        try:
            action_content = action_obj.read(cr, uid, action_id,
                                             context=context)[0]
            action_content.update({'views': [(view_id[0], 'form')]})
            return action_content
        except IndexError:
            raise orm.except_orm('ERROR',
                                 """One or both of the following elements are missing:
                                 Action: Fill Sale Products
                                 View: sale.order.fill.view
                                 Please Update module.""")

    def _prepare_order_picking(self, cr, uid, order, context=None):
      pdb.set_trace()
      """Overloading method to add relation to drivers_order_ids"""
      values = super(SaleOrder, self)._prepare_order_picking(cr, uid, order,
                                                            context)
      if order.drivers_order_ids:
        pick_drivers = []
        for driver in order.drivers_order_ids:
          pick_drivers.append((0,0,{'line_id': driver.line_id.id,
                              'product_id': driver.product_id.id,
                              'order_total': driver.order_total,
                              'driver_1': driver.driver_1,
                              'driver_2': driver.driver_2,
                              'driver_3': driver.driver_3,
                              'driver_4': driver.driver_4,
                              'driver_5': driver.driver_5,
                              'driver_6': driver.driver_6,
                              'driver_7': driver.driver_7,
                              'driver_8': driver.driver_8,
                              'driver_9': driver.driver_9,
                              'driver_10': driver.driver_10,
                              'driver_11': driver.driver_11,
                              'driver_12': driver.driver_12,
                              'driver_13': driver.driver_13,
                              'driver_14': driver.driver_14,
                              'driver_15': driver.driver_15}))
        values.update({'drivers_order_ids': pick_drivers})
      return values


    _columns = {
        'drivers_order_ids': fields.one2many('drivers.order.line', 'sale_order',
                                          'Sales Agent'),
    }
