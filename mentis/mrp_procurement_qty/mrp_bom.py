# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Mentis d.o.o.
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

#import time
#from datetime import datetime

from openerp.osv import fields, osv
from openerp.tools import float_compare
from openerp import netsvc


class mrp_bom(osv.osv):
    _inherit = 'mrp.bom'

    def _bom_explode(self, cr, uid, bom, factor, properties=None, addthis=False, level=0, routing_id=False):
        
        result, result2 = super(mrp_bom, self)._bom_explode(cr, uid, bom, factor, properties, addthis, level, routing_id)
        
        if len(result) > 1:
            product_dict = {}
            for res in result:
                if res['product_id'] in product_dict:
                    tmp_dict = product_dict[res['product_id']] #dobimo obstojeci produkt h kateremo bomo dodajali
                    tmp_dict['product_qty'] = tmp_dict['product_qty'] + res['product_qty']
                    
                    product_dict[res['product_id']] = tmp_dict
                else:
                    tmp_dict = {}
                    tmp_dict['product_uos_qty'] = res['product_uos_qty']
                    tmp_dict['name'] = res['name']
                    tmp_dict['product_uom'] = res['product_uom']
                    tmp_dict['product_qty'] = res['product_qty']
                    tmp_dict['product_uos'] = res['product_uos']
                    tmp_dict['product_id'] = res['product_id']
                    product_dict[res['product_id']] = tmp_dict
                    
            #Sedaj zapisemo dictionaly of dictionaries v list of dictionaries
            result = []
            for dict in product_dict:
                result.append(product_dict[dict])
            
        return result, result2

mrp_bom()
    
