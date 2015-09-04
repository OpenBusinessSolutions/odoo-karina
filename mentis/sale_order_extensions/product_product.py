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

from osv import fields, osv
from openerp import netsvc
from tools.translate import _
from lxml import etree
import decimal_precision as dp

class product_product(osv.Model):
    _inherit = 'product.product'
    
    _columns = {
        'sale_enabled': fields.boolean('Sale Enabled'),
        'sale_price'  : fields.float('Sale Price', digits_compute=dp.get_precision('Product Price'), ),
    }
    _defaults = {
        'sale_enabled': False,
        'sale_price':   0.0
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = super(product_product, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu)
        if context and context.get('active_model', False) == 'stock.location.product' and view_type == 'search':
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//search"):
                _categ_ids = self.pool.get('product.category').search(cr, uid, [('parent_id','=',False)], order='name')
                for _categ_id in self.pool.get('product.category').browse(cr, uid, _categ_ids, context):
                    _name = _categ_id.name
                    _domain = "[('categ_id.parent_id','child_of'," + str(_categ_id.id) + ")]"

                    _filter = etree.Element('filter')
                    _filter.set('string', _categ_id.name)
                    _filter.set('domain', _domain)
                    node.append(_filter)
            res['arch'] = etree.tostring(doc)            
        
        return res
