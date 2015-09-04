# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 ChriCar Beteiligungs- und Beratungs- GmbH (<http://www.camptocamp.at>)
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
#import openerp.addons.decimal_precision as dp

import re  
from openerp.tools.translate import _
        
        
#----------------------------------------------------------
#  Account Tax
#----------------------------------------------------------

class account_tax(osv.osv):
    _inherit = 'account.tax'
    _columns = {
        'line_precision' : fields.boolean('Rounding Precision', help="Calculates floating point tax per line to simulate vertical calculation"),
    }
     
account_tax()

class account_tax_template(osv.osv):
    _inherit = 'account.tax.template'
    _columns = {
        'line_precision' : fields.boolean('Rounding Precision', help="Calculates floating point tax per line to simulate vertical calculation"),
    }
     
account_tax_template()

#----------------------------------------------------------
#  Tax Calculation
#----------------------------------------------------------
class account_tax(osv.osv):
    _inherit = 'account.tax'
    def _compute(self, cr, uid, taxes, price_unit, quantity, address_id=None, product=None, partner=None, precision=None):
        """
        Compute tax values for given PRICE_UNIT, QUANTITY and a buyer/seller ADDRESS_ID.

        RETURN:
            [ tax ]
            tax = {'name':'', 'amount':0.0, 'account_collected_id':1, 'account_paid_id':2}
            one tax for each tax id in IDS and their children
        """
        res = self._unit_compute(cr, uid, taxes, price_unit, address_id, product, partner, quantity)
        total = 0.0
        for t in taxes:
            prec = t.line_precision
        precision_pool = self.pool.get('decimal.precision')
        for r in res:
            if r.get('balance',False):
                if prec:
                    r['amount'] = r.get('balance', 0.0) * quantity - total
                else:
                    r['amount'] = round(r.get('balance', 0.0) * quantity, precision_pool.precision_get(cr, uid, 'Account')) - total
            else:
                if prec:
                    r['amount'] = r.get('amount', 0.0) * quantity
                else:
                    r['amount'] = round(r.get('amount', 0.0) * quantity, precision_pool.precision_get(cr, uid, 'Account'))
                total += r['amount']
        return res

account_tax()
