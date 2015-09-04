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

import time
from openerp.report import report_sxw
from openerp.osv import osv
from openerp import pooler

class rec_pay(report_sxw.rml_parse):
	_name = 'receivable.payable.report'
	def __init__(self, cr, uid, name, context):
		super(rec_pay, self).__init__(cr, uid, name, context=context)
		self.localcontext.update({
            'time': time,
        })

	
#        
report_sxw.report_sxw('report.receivable.payable.report','res.partner','addons/account_receivables_payables/report/rec_pay_report.rml',parser=rec_pay)

