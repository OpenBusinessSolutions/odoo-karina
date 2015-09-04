# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP s.a. (<http://www.openerp.com>).
#    Copyright (C) 2013-TODAY Mentis d.o.o. (<http://www.mentis.si/openerp>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from osv import osv, fields
from tools.translate import _
import openerp.addons.decimal_precision as dp

class product_template(osv.osv):
    _inherit = "product.template"
    _columns = {
        'aq_spare_part' : fields.boolean('Spare Part',  help="Used if this product is spare part"),
        'aq_uop_coeff'  : fields.float('Purchase UOM coeff', digits_compute= dp.get_precision('Product UoM'), help="Used to calculate uom quatity to purchase uom quantity"),
        'aq_pallete_qty': fields.float('Pallete quantity', digits_compute= dp.get_precision('Product UoM'), help="Number of items on pallete"),
        'aq_box_weight' : fields.float('Box Weight', digits_compute= dp.get_precision('Stock Weight'), help="Box weight"),
    }
    _defaults = {
        'aq_spare_part': False,
        'aq_uop_coeff' : 1.0,        
    }

product_template()
