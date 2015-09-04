# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Andrea Cometa All Rights Reserved.
#                       www.andreacometa.it
#                       openerp@andreacometa.it
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv

class product_category(osv.osv):

    _inherit = "product.category"

    _columns = {
        # ----- Commission for product
        'commission' : fields.float('Commission %'),
    }

product_category()

class product_product(osv.osv):

    _inherit = "product.product"

    _columns = {
        # ----- Commission for category
        'commission' : fields.float('Commission %'),
        # ----- No commission for this product
        'no_commission' : fields.boolean('No Commission'),
        # ----- Product used as standard product for new salesagent
        'standard_commission_product' : fields.boolean('Standard Commission',
            help='All the products with this value set on True will be insert in the salesagent product list when you click on "Rapid Product Filling"'),
    }

product_product()
