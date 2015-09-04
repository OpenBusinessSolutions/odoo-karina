# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP s.a. (<http://www.openerp.com>)
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

from osv import fields, osv
from tools.translate import _
import openerp.addons.decimal_precision as dp

class product_period_cost(osv.Model):
    _name = "product.period.cost"
    _description = "Product Cost By Period"

    _columns = {
        'product_id': fields.many2one('product.product','Product', required=True),
        'period_id':  fields.many2one('account.period', 'Period', required=True),
        'price_unit': fields.float('Cost for period', required=True, digits_compute=dp.get_precision('Product Price'))
    }
    _defaults = {
        'price_unit': 0.0
    }