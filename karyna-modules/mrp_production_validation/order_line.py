#-*- coding: utf-8 -*-
from openerp.osv import orm

'''
class SaleOrderLine(orm.Model):
    
    _inherit = 'sale.order.line'

    def _check_product_qty(self, cr, uid, ids, context=None):
        """Validate the product quantity before writing or creating a record.

        returns: boolean"""
        bom_obj = self.pool.get('mrp.bom')
        mrp_obj = self.pool.get('mrp.production')
        for line in self.browse(cr, uid, ids, context=context):
            for bom in line.product_id.bom_ids:
                valid = mrp_obj.validate_product_pack(cr, uid,
                                                      bom.id,
                                                      line.product_uom_qty,
                                                      context=context)
            else:
                valid = True
        return valid

    _constraints = [
    (_check_product_qty, "Product quantity can't be set 'cause of bom list",
     ['product_uom_qty'])]
     
'''
