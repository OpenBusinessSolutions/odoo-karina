# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2012 Andrea Cometa All Rights Reserved.
#                       www.andreacometa.it
#                       openerp@andreacometa.it
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from datetime import datetime
from report import report_sxw
import locale
from openerp.osv import fields, osv

from tools.translate import translate

class Parser(report_sxw.rml_parse):

	def list_sum(self, lista_elementi, voce):
		totale = 0.0
		for elem in lista_elementi:
			totale += elem[voce]
		return totale

	def __init__(self, cr, uid, name, context):
		super(Parser, self).__init__(cr, uid, name, context)
		
		rows = self.pool.get(context['active_model']).browse(cr, uid, context['active_ids'], context=context)
		
		self.localcontext.update({
			'time': time,
			'ListSum' : self.list_sum,
			'screen_rows': rows,
		})
