# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 Cubic ERP - Teradata SAC (<http://cubicerp.com>).
#       (Modified by)   Vauxoo - http://www.vauxoo.com/
#                       info Vauxoo (info@vauxoo.com)
#    Modified by - juan@vauxoo.com
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

from openerp.osv import osv, fields


class ProductTemplate(osv.Model):
    _name = 'product.template'
    _inherit = 'product.template'
    _columns = {
        'customs_rate_id': fields.many2one('product.customs.rate',
                                           'Customs Rate',
                                           domain=[('type', '=', 'normal')]),
    }
