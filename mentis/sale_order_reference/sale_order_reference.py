# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Mentis d.o.o. All rights reserved.
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

import string
from osv import fields, osv
from tools.translate import _

"""
	- sale.order object:
    - Calculates customer reference from sale order number
"""

class sale_order(osv.osv):
    _inherit = 'sale.order'
    _columns = {
        'sale_order_ref': fields.char('Sale Order Reference', size=32),
    }
        
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'sale.order') or '/'
            vals['sale_order_ref'] = self.parse_reference_RF(vals['name'])
        return super(sale_order,self).create(cr, uid, vals, context)

    def parse_reference_RF(self, order_number):
        tmp_ref = filter(lambda c: c.isalnum(), order_number)
        ctrl_num = self.calculate_control_number(tmp_ref + 'RF00')
        ref_num = ctrl_num + ' ' + tmp_ref
        return ref_num
        
    def calculate_control_number(self, ref_string):
        tmp_ref = ''
        for char in ref_string.lower():
            if char == 'a':
                tmp_ref = tmp_ref + '10'
            elif char == 'b':
                tmp_ref = tmp_ref + '11'
            elif char == 'c':
                tmp_ref = tmp_ref + '12'
            elif char == 'd':
                tmp_ref = tmp_ref + '13'
            elif char == 'e':
                tmp_ref = tmp_ref + '14'
            elif char == 'f':
                tmp_ref = tmp_ref + '15'
            elif char == 'g':
                tmp_ref = tmp_ref + '16'
            elif char == 'h':
                tmp_ref = tmp_ref + '17'
            elif char == 'i':
                tmp_ref = tmp_ref + '18'
            elif char == 'j':
                tmp_ref = tmp_ref + '19'
            elif char == 'k':
                tmp_ref = tmp_ref + '20'
            elif char == 'l':
                tmp_ref = tmp_ref + '21'
            elif char == 'm':
                tmp_ref = tmp_ref + '22'
            elif char == 'n':
                tmp_ref = tmp_ref + '23'
            elif char == 'o':
                tmp_ref = tmp_ref + '24'
            elif char == 'p':
                tmp_ref = tmp_ref + '25'
            elif char == 'q':
                tmp_ref = tmp_ref + '26'
            elif char == 'r':
                tmp_ref = tmp_ref + '27'
            elif char == 's':
                tmp_ref = tmp_ref + '28'
            elif char == 't':
                tmp_ref = tmp_ref + '29'
            elif char == 'u':
                tmp_ref = tmp_ref + '30'
            elif char == 'v':
                tmp_ref = tmp_ref + '31'
            elif char == 'w':
                tmp_ref = tmp_ref + '32'
            elif char == 'x':
                tmp_ref = tmp_ref + '33'
            elif char == 'y':
                tmp_ref = tmp_ref + '34'
            elif char == 'z':
                tmp_ref = tmp_ref + '35'
            else:
                tmp_ref = tmp_ref + char
        #calculate MOD 97-10
        ctrl_num = 98 - int(tmp_ref) % 97
        if ctrl_num < 10:
            res = "RF0%s" % ctrl_num
        else:
            res = "RF%s" % ctrl_num
        return res
        
sale_order()
