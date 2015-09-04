#-*- coding: utf-8 -*-
from openerp.tests import common
from datetime import date
from openerp.osv import orm

class TestSaleOrderFill(common.TransactionCase):

    def create_sale_orders(self, cr, uid, partner_id):
        """Helper method to create demo sale order."""
        res = []
        sale_shop = self.registry('sale.shop').search(cr, uid, [], limit=1)[0]
        pricelist = self.registry('product.pricelist').search(cr, uid, [], limit=1)[0]
        sale_obj = self.registry('sale.order')
        value = {
                'partner_id': partner_id,
                'partner_invoice_id': partner_id,
                'partner_shipping_id': partner_id,
                'date_order': date.today().isoformat(),
                'sale_shop': sale_shop,
                'picking_policy': 'direct',
                'order_policy': 'picking',
                'pricelist_id': pricelist
        }
        res.append(sale_obj.create(cr, uid, value))
        return res

    def setUp(self):
        super(TestSaleOrderFill, self).setUp()

        cr, uid = self.cr, self.uid
        self.sale_order = self.registry('sale.order')
        self.sale_line = self.registry('sale.order.line')
        self.partner_obj = self.registry('res.partner')
        self.sale_fill_obj = self.registry('sale.order.fill')

        #Create Demo Data
        partner_id = self.partner_obj.search(cr, uid,[], limit=1)[0]
        self.order_ids = self.create_sale_orders(cr, uid, partner_id)

    def testSaleOrderCallsWizard(self):
        """Check that we are calling the correct wizard from the sale order."""
        cr, uid = self.cr, self.uid
        action_obj = self.registry('ir.actions.act_window')
        view_obj = self.registry('ir.ui.view')
        action_id = action_obj.search(cr, uid, [('name', '=', 'Fill Sale Products'),
                                      ('res_model', '=', 'sale.order.fill')])
        view_id = view_obj.search(cr, uid, [('name', '=', 'sale.order.fill.view'),
                                  ('model', '=', 'sale.order.fill')])
        action_content = action_obj.read(cr, uid, action_id[0])
        action_content['views'] = [(view_id[0], 'form')]
        expected = action_content
        received = self.sale_order.get_category_defaults(cr, uid, self.order_ids)
        self.assertDictEqual(expected, received)

    def testSaleOrderFailsAtNoAction(self):
        """Check that exception is raised if the action is deleted."""
        cr, uid = self.cr, self.uid
        action_obj = self.registry('ir.actions.act_window')
        action_id = action_obj.search(cr, uid, [('name', '=', 'Fill Sale Products'),
                                      ('res_model', '=', 'sale.order.fill')])
        action_obj.unlink(cr, uid, action_id[0])
        self.assertRaises(orm.except_orm, self.sale_order.get_category_defaults,
                              cr, uid, self.order_ids)

    def testSaleOrderFailsAtNoView(self):
        """Check that exception is raised if the view is deleted."""
        cr, uid = self.cr, self.uid
        view_obj = self.registry('ir.ui.view')
        view_id = view_obj.search(cr, uid, [('name', '=', 'sale.order.fill.view'),
                                  ('model', '=', 'sale.order.fill')])
        view_obj.unlink(cr, uid, view_id)
        self.assertRaises(orm.except_orm, self.sale_order.get_category_defaults,
                              cr, uid, self.order_ids)

    def testExceptionAtMoreThanOneOrder(self):
        """This is just for making sure we are passing only one order."""
        cr, uid = self.cr, self.uid
        self.assertRaises(orm.except_orm, self.sale_order.get_category_defaults,
                          cr, uid, [1,2])

    def testCheckForAllSaleableProducts(self):
        """Check that returns all products for sale of a set category."""
        cr, uid = self.cr, self.uid
        category_obj = self.registry('product.category')
        product_obj = self.registry('product.product')
        category_id = category_obj.search(cr, uid, [], limit=1)[0]
        expected_products = product_obj.search(cr, uid, [('categ_id', '=', category_id),
                                               ('sale_ok', '=', True)])
        result = self.sale_fill_obj.get_products(cr, uid, category_id)
        self.assertEqual(expected_products, result)

    def testCheckForAllSaleableProductsWithNoCategory(self):
        """Check that when passed no category id the returned list
        is composed of all products that can be sold."""
        cr, uid = self.cr, self.uid
        product_obj = self.registry('product.product')
        expected = product_obj.search(cr, uid, [('sale_ok','=',True)])
        result = self.sale_fill_obj.get_products(cr, uid)
        self.assertEqual(expected, result)

    def testOrderLineValues(self):
        """Check that the order line values are correctly passed."""
        cr, uid = self.cr, self.uid
        product_obj = self.registry('product.product')
        product_id = product_obj.search(cr, uid, [('sale_ok','=',True)],
                                        limit=1)[0]
        product = product_obj.browse(cr, uid, product_id)
        taxes = product.taxes_id
        expected_values = {
            'product_id': product_id,
            'name': unicode(product.name),
            'product_uom_qty': 1,
            'product_uom': product.uom_id.id,
            'price_unit': product.list_price,
            'delay': product.sale_delay,
            'type': product.procure_method,
            'state': 'draft',
            'order_id': self.order_ids[0],
            'tax_id': [(6, 0, [tax.id for tax in taxes])]
        }
        result = self.sale_fill_obj.prepare_order_line(cr, uid, product_id,
                                                       self.order_ids[0])
        self.assertEqual(result, expected_values)

    def testFillOrderLines(self):
        """Check that the order is filled with the expected products."""
        cr, uid = self.cr, self.uid
        category_obj = self.registry('product.category')
        product_obj = self.registry('product.product')
        fill_obj = self.registry('sale.order.fill')
        category_ids = category_obj.search(cr, uid, [('name','<>','All Products')],
                                           limit=1)
        product_ids = product_obj.search(cr, uid, [('sale_ok','=',True),
                                         ('categ_id','in',category_ids)])
        expected_lines = len(product_ids)
        fill_id = fill_obj.create(cr, uid, {'category_ids': [(6, 0, category_ids)]})
        context={'active_id': self.order_ids[0], 'active_ids': self.order_ids}
        self.sale_fill_obj.fill_sale_order(cr, uid, [fill_id], context=context)
        order = self.sale_order.browse(cr, uid, self.order_ids[0])
        self.assertEqual(len(order.order_line), expected_lines)

    def testFillOrderLinesWithoutCategory(self):
        """Check that the order lines are filled without categories."""
        cr, uid = self.cr, self.uid
        product_obj = self.registry('product.product')
        fill_obj = self.registry('sale.order.fill')
        context = {'active_id': self.order_ids[0]}
        fill_id = fill_obj.create(cr, uid, {}, context=context)
        product_ids = product_obj.search(cr, uid, [('sale_ok','=',True)])
        expected_lines = len(product_ids)
        self.sale_fill_obj.fill_sale_order(cr, uid, [fill_id], context=context)
        order = self.sale_order.browse(cr, uid, self.order_ids[0])
        self.assertEqual(len(order.order_line), expected_lines)
