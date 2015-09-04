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
from datetime import datetime

class account_move_line(osv.osv):
    
    def _days_overdue(self, cr, uid, ids, name, args, context=None):
        result = {}
        for line in self.browse(cr, uid, ids):
            if line.date_maturity:
                razlika = datetime.today() - datetime.strptime(line.date_maturity, "%Y-%m-%d")
                result[line.id] = razlika.days
            else:
                result[line.id] = 0
        return result
    
    _inherit = "account.move.line"
    _columns = {
        'days_overdue': fields.function(_days_overdue, type='integer', string='Days overdue'),
    }
    
account_move_line()


