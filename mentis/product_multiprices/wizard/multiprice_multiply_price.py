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
from tools.translate import _

class multiprice_multiply_price(osv.osv_memory):
    _name = "multiprice.multiply.price"
    _description = "Multiply selected sale price"
    _columns = {
        'column': fields.selection([ ('list_price', 'Sale Price'),
                                        ('lst_price2', 'Sale Price 2'),
                                        ('lst_price3', 'Sale Price 3'),
                                        ('lst_price4', 'Sale Price 4'),
                                        ('lst_price5', 'Sale Price 5'),
                                        ('lst_price6', 'Sale Price 6'),
                                        ('lst_price7', 'Sale Price 7'),
                                        ('lst_price8', 'Sale Price 8'),
                                        ('lst_price9', 'Sale Price 9'),
                                        ('lst_price10', 'Sale Price 10'),
                                        ], 'Column to multiply: ', required=True),
        'by_value': fields.float('Multiply value', digits=(6,3), required=True),
                }
    
    def multiply_price(self, cr, uid, ids, context=None):
        
        if context is None:
            context={}
            
        price_obj = self.pool.get('product.template')
        active_ids = context.get('active_ids',[])
        copy_line = self.browse(cr,uid,ids)[0] #podatki iz trenutne wizard vrstice
        
        for price in price_obj.read(cr, uid, active_ids, [copy_line.column], context=context):
            price_value = price[copy_line.column]
            price_id = price['id']
            
            result = price_value * copy_line.by_value
            
            price_obj.write(cr, uid, [price_id], {copy_line.column:result})
        
        
        return {
                'type': 'ir.actions.act_window_close',
        }
    
multiprice_multiply_price()
