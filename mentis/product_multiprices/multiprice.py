# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Mentis d.o.o.
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

from osv import fields, osv
import decimal_precision as dp

class product_template(osv.osv):
    _inherit = "product.template"
    _columns = {
        'lst_price0': fields.float('Sale Price 0', digits_compute=dp.get_precision('Product Price')),
        'lst_price2': fields.float('Sale Price 2', digits_compute=dp.get_precision('Product Price')),
        'lst_price3': fields.float('Sale Price 3', digits_compute=dp.get_precision('Product Price')),
        'lst_price4': fields.float('Sale Price 4', digits_compute=dp.get_precision('Product Price')),
        'lst_price5': fields.float('Sale Price 5', digits_compute=dp.get_precision('Product Price')),
        'lst_price6': fields.float('Sale Price 6', digits_compute=dp.get_precision('Product Price')),
        'lst_price7': fields.float('Sale Price 7', digits_compute=dp.get_precision('Product Price')),
        'lst_price8': fields.float('Sale Price 8', digits_compute=dp.get_precision('Product Price')),
        'lst_price9': fields.float('Sale Price 9', digits_compute=dp.get_precision('Product Price')),
        'lst_price10': fields.float('Sale Price 10', digits_compute=dp.get_precision('Product Price')),
    }
    _defaults = {
        'lst_price0': lambda *a: 0,
    }
    
product_template()
