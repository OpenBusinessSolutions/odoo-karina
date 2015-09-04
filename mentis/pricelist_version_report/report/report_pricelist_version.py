# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import time
from report import report_sxw
from osv import osv
import pooler

class pricelist_version(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(pricelist_version, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                        'time': time,
                        'get_description': self._get_description,
                        'get_price': self._get_price
                        })
    
    def _get_description(self, item):
        if item.product_id:
            _description = item.product_id.name
        elif item.categ_id:
            _description = item.categ_id.complete_name
        else:
            _description = ""        
        return _description
        
    def _get_price(self, item):
        _price = ""
        if item.price_discount != 0.0 and item.price_discount != -1.0:
            _pool = pooler.get_pool(self.cr.dbname)
            _price_base = self.pool.get('product.price.type').browse(self.cr, self.uid, [item.base])
            if _price_base[0]:
                _price += _price_base[0].name + " " + str(round(item.price_discount * 100, 0)) + "%"
            else:
                _price += str(round(item.price_discount * 100, 0)) + "%"
        if item.price_surcharge != 0.0:
            if _price != "":
                _price += " + "
            _price += str(item.price_surcharge) + item.price_version_id.pricelist_id.currency_id.symbol
        return _price
    
report_sxw.report_sxw('report.pricelist.version','product.pricelist.version','pricelist_version_report/report/report_pricelist_version.rml', parser=pricelist_version, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

