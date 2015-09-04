# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
############################################################################
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
from openerp.osv import osv, fields
from openerp.addons.decimal_precision import decimal_precision as dp


class MrpProduction(osv.Model):
    _inherit = 'mrp.production'

    _columns = {
        'bom_qty': fields.related('bom_id', 'product_qty', type='float',
                string='Bom Qty', store=True,
                digits_compute=dp.get_precision('Product UoM'),
                readonly=True, states={'draft': [('readonly', False)]},
                help="BoM's Quantity to change from production order"
                                  ),
        'bom_uom': fields.related('bom_id', 'product_uom', type='many2one',
                relation='product.uom', string='Bom UoM',
                store=True, readonly=True,
                states={'draft': [('readonly', False)]},
            help="BoM's UoM to change from production order"
        ),
    }
