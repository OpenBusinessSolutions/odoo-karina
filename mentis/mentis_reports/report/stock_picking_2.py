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

import time
from openerp.report import report_sxw
from openerp.osv import osv
from openerp import pooler

class picking(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(picking, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_product_desc':self._get_product_desc,
            'get_product_notes':self._get_product_notes,
        })
    def _get_product_desc(self,move_line):
        if move_line.sale_line_id.name:
            desc = move_line.sale_line_id.name
        else:
            desc = move_line.product_id.name
        return desc
    
    def _get_product_notes(self,move_line):
        if move_line.sale_line_id.product_notes:
            return move_line.sale_line_id.product_notes
        else:
            return ''

report_sxw.report_sxw('report.stock.picking.list.mentis2','stock.picking','mentis_reports/report/stock_picking_2.rml',parser=picking)
