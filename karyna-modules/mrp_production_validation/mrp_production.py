#-*- coding: utf-8 -*-
from openerp.osv import orm
import logging

class ProductValidation(orm.Model):

    _inherit = 'mrp.production'

    def _check_product_qty(self, cr, uid, ids, context=None):
        """Apply constraints to manufacturing order."""
        for order in self.browse(cr, uid, ids, context=context):
            valid = self.validate_product_pack(cr, uid, order.bom_id.id,
                                               order.product_qty, context)
        return valid

    _constraints = [
    (_check_product_qty, "Product quantity can't be set 'cause of bom list",
    ['product_qty'])]

    def log(self):
        return logging.getLogger(self._name)

    def onchange_product_qty(self, cr, uid, ids, product_qty, product_id,
                         bom_id, context=None):
        """Validation for the product quantities in the production process

        params:
            product_qty; float.
            product_id; int.
            bom_id; int, bill of materials.

        return:
            values; dict, dict of fields, values.
        """
        if not product_id:
            return {}
        valid = self.validate_product_pack(cr, uid, bom_id, product_qty, context)
        if not valid:
            raise orm.except_orm("Error",
                                 "Check that the desired amount is a multiple of the bom amount.")
        else:
            return {}


    def validate_product_pack(self, cr, uid, bom_id, product_qty, context=None):
        """Validate the product quantity against package quantity.

        params:
            bom_id; int, bill of materials
            product_qty; float, amount desired to produce

        return:
            boolean"""
        bom_obj = self.pool.get('mrp.bom')
        bom = bom_obj.browse(cr, uid, bom_id, context=context)
        for line in bom.bom_lines:
            self.log().info("Validating against line {} of bom {}".format(line,
                     bom.name))
            res = product_qty % bom.product_qty
            if res:
                self.log().info('Product pack not valid; {} % {} = {}'.format(
                         product_qty, bom.product_qty, res))
                return False
        return True

    def action_confirm(self, cr, uid, ids, context=None):
        """Overwrite of action_confirm method to first validate the quantities
        of the product pack to produce."""
        for order in self.browse(cr, uid, ids, context=context):
            valid = self.validate_product_pack(cr, uid, order.bom_id.id,
                                              order.product_qty,
                                              context=context)
            if valid:
                return super(ProductValidation, self).action_confirm(cr,
                                                                     uid,
                                                                     ids,
                                                                     context)
            else:
                raise orm.except_orm("Error", """Error trying to accomodate quantities.
                                     Check that the desired amount is a multiple of the bom amount.""")
                return {}
