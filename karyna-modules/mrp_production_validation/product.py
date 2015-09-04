#-*- coding: utf-8 -*-
from openerp.osv import orm, fields


class Product(orm.Model):

    _inherit = 'product.template'
    _columns = {
        'yield_sack': fields.float('Yield per sack', digits=(16, 2),
                                   help='The yield per sack for the selected'
                                   'product.'),
    }

Product()
