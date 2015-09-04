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

class multiprice_copy_price(osv.osv_memory):
    _name = "multiprice.copy.price"
    _description = "Copy one sale price to another"
    _columns = {
        'copy_from': fields.selection([ ('list_price', 'Sale Price'),
                                        ('lst_price2', 'Sale Price 2'),
                                        ('lst_price3', 'Sale Price 3'),
                                        ('lst_price4', 'Sale Price 4'),
                                        ('lst_price5', 'Sale Price 5'),
                                        ('lst_price6', 'Sale Price 6'),
                                        ('lst_price7', 'Sale Price 7'),
                                        ('lst_price8', 'Sale Price 8'),
                                        ('lst_price9', 'Sale Price 9'),
                                        ('lst_price10', 'Sale Price 10'),
                                        ], 'Copy from column: ', required=True),
        'copy_to': fields.selection([   ('list_price', 'Sale Price'), 
                                        ('lst_price2', 'Sale Price 2'),
                                        ('lst_price3', 'Sale Price 3'),
                                        ('lst_price4', 'Sale Price 4'),
                                        ('lst_price5', 'Sale Price 5'),
                                        ('lst_price6', 'Sale Price 6'),
                                        ('lst_price7', 'Sale Price 7'),
                                        ('lst_price8', 'Sale Price 8'),
                                        ('lst_price9', 'Sale Price 9'),
                                        ('lst_price10', 'Sale Price 10'),
                                        ], 'Copy to column: ', required=True),
                }
    
    def copy_price(self, cr, uid, ids, context=None):
        
        if context is None:
            context={}
            
        price_obj = self.pool.get('product.template')
        active_ids = context.get('active_ids',[])
        copy_line = self.browse(cr,uid,ids)[0] #podatki iz trenutne wizard vrstice
        
        if copy_line.copy_from == copy_line.copy_to:
            raise osv.except_osv(_('Warning'), _('Please select two different price columns!'))
        
        for price in price_obj.read(cr, uid, active_ids, [copy_line.copy_from], context=context):
            price_value = price[copy_line.copy_from]
            price_id = price['id']
            
            price_obj.write(cr, uid, [price_id], {copy_line.copy_to:price_value})
        
        
        return {
                'type': 'ir.actions.act_window_close',
        }
    
multiprice_copy_price()