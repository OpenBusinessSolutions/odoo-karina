# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Mentis d.o.o.
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

class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'business_partner_type': fields.selection([('1','D.D.'),
                                                   ('2','D.O.O.'),
                                                   ('3','S.P.'),
                                                   ('4','Bolnice'),
                                                   ('5','Šole'),
                                                   ('6','Sindikati'),
                                                   ('7','Društva'),
                                                   ('8','Zavarovalnice'),
                                                   ('9','Vrtec'),
                                                   ('10','Občine')], 'Type of Business Partner')
    }
    
res_partner()

#class stock_move(osv.osv):
#    def _get_total_weight(self, cr, uid, ids, name, args, context=None):
#        res={}
#        for line in self.browse(cr, uid, ids):
#            res[line.id] = line.product_qty * line.product_id.weight_net
#        return res
#    
#    def _get_stock_move(self, cr, uid, ids, context=None):
#        result = {}
#        move_ids = self.pool.get('stock.move').search(cr, uid, [('product_id', 'in', ids)])
#        for move_id in move_ids:
#            result[move_id] = True
#            nekaj = result.keys()
#        return result.keys()
#    
#    _inherit = 'stock.move'
#    _columns = {
#        'total_weight': fields.function(_get_total_weight, type='float', string='Total Weight',
#            store={
#                   'stock.move': (lambda self, cr, uid, ids, c={}: ids, ['product_qty'], 20),
#                   'product.product': (_get_stock_move, ['weight_net'], 20),
#                   })
#    }
#    
#stock_move()
