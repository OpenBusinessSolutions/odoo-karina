#-*- coding: utf-8-*-
from openerp.osv import osv, fields
import logging
import pdb

class SaleOrderFill(osv.osv_memory):

    _name = 'sale.order.fill'
    _auto = True

    _columns = {
        'category_ids': fields.many2many('product.category',
                                         'sale_order_product_category_rel',
                                         'order_id',
                                         'category_id', string="Categories")
    }

    def get_products(self, cr, uid, categ_id=False, context=None):
        """Retrieve all saleable products from a product category.product

        Args:
            categ_id; int, category in wich to look for products.

        Return:
            res; list of products
        """
        product_obj = self.pool.get('product.template')
        if categ_id:
            product_ids = product_obj.search(cr, uid, [('categ_id', '=', categ_id),
                                         ('sale_ok', '=', True),
                                         ('active', '=', True),
                                         ('state', '=', 'sellable')],
                                         context=context)
        else:
            product_ids = product_obj.search(cr, uid, [('sale_ok', '=', True),
                                         ('active', '=', True),
                                         ('state', '=', 'sellable')],
                                         context=context)
        return product_ids

    def get_salesagent_ids(self, cr, uid, context=None):
        """Return a list of salesagents available to create a sale order line.
        """
        log = logging.getLogger(self._name)
        partner_obj = self.pool.get('res.partner')
        salesagents_obj = self.pool.get('salesagent.order.line')
        agents = partner_obj.search(cr, uid, [('active','=', True),
                                    ('salesagent','=', True)], context=context)
        values = []
        for agent in agents:
            values.append((0, 0, {'salesagent_id': agent, 'quantity': 0.0}))
            log.info("Created salesagent.order.line for partner with id {}".format(agent))
        return values
    
    def get_packaging(self, cr, uid, product_id, context=None):
        
        """Return packaging id from a product.

        @params: product_id; int
        @returns: res; dict; {product_id: package_id}"""
        product_obj = self.pool.get('product.template')
        product = product_obj.browse(cr, uid, product_id, context)
        if product.packaging_ids:
            return product.packaging_ids[0].id
        else:
            return False
    
    def prepare_order_line(self, cr, uid, product_id, order_id, context=None):
        """Prepare a sale order line from a product.

        Args:
            product_id; int, product id to retrieve data

        Return:
            values; dict, fields to create the order line.
        """
        product_obj = self.pool.get('product.template')
        product = product_obj.read(cr, uid, product_id, context=context)
        name = product.get('name').encode('utf-8')
        taxes = product.get('taxes_id')
        packaging = self.get_packaging(cr, uid, product_id, context)
        values = {
            'name': name,
            'product_id': product_id,
            'product_uom_qty': 0,
            'product_uom': product.get('uom_id', False)[0],
            'price_unit': product.get('list_price', False),
            'delay': product.get('sale_delay', 0.0),
            'type': product.get('procure_method', False),
            'state': 'draft',
            'order_id': order_id,
            'tax_id': [(6, 0, taxes)],
            'product_packaging': False,
            #'product_packaging': packaging,
        }
        return values

    def prepare_drivers_order_line(self, cr, uid, product_id, order_id, context=None):
        """Prepare a drivers order line from a product.

        Args:
            product_id; int, product id to retrieve data

        Return:
            values; dict, fields to create the order line.
        """
        product_obj = self.pool.get('product.template')
        product = product_obj.read(cr, uid, product_id, context=context)
        name = product.get('name').encode('utf-8')
        taxes = product.get('taxes_id')
        packaging = self.get_packaging(cr, uid, product_id, context)
        values = {
            #'name': name,
            'product_id': product_id,
            #'product_uom_qty': 0,
            #'product_uom': product.get('uom_id', False)[0],
            #'price_unit': product.get('list_price', False),
            #'delay': product.get('sale_delay', 0.0),
            #'type': product.get('procure_method', False),
            #'state': 'draft',
            'sale_order': order_id,
            #'tax_id': [(6, 0, taxes)],
            #'product_packaging': packaging,
        }
        return values

    def fill_sale_order(self, cr, uid, ids, context=None):
        """Main entry point of wizard. Use context active_ids to create
        an order line for every saleable product in the selected category."""
        log = logging.getLogger(self._name)
        line_obj = self.pool.get('sale.order.line')
        drivers_obj = self.pool.get('drivers.order.line')
        order_id = context.get('active_id')
        res = []
        values = self.read(cr, uid, ids[0], context=context)
        if values.get('category_ids'):
            products = self.get_products(cr, uid,
                                         values.get('category_ids')[0],
                                         context)
            log.info("Preparing to create {} lines from category {}".format(
                     len(products), values.get('category_ids')))
        else:
            products = self.get_products(cr, uid, context=context)
            log.info("Preparing to create {}.".format(len(products)))
        for product in products:
            values = self.prepare_order_line(cr, uid, product, order_id,
                                                      context=context)
            line_id = line_obj.create(cr, uid, values, context=context)
            
            drivers_values = self.prepare_drivers_order_line(cr, uid, product, order_id,
                                                      context=context)
            driver_line_id = drivers_obj.create(cr, uid, drivers_values, context=context)
            log.info("Created line for product {}".format(values.get('name')))
            res.append(line_id)
        return res
    

