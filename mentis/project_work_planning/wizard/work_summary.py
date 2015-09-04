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

from osv import fields, osv
from tools.translate import _

class work_summary_input(osv.osv_memory):
    _name = "project.task.summary.input"
    _description = "Input mask for work summary"
    _columns = {
        'name': fields.char('Description', size=128, required=True),
        'work_type': fields.selection([('delo','Delo'),('malica','Malica'),('privat','Privat odhod')], 'Work type', required=True),
    }
    
    _defaults = {
        'work_type': lambda *a: 'delo',
    }
    
    def write(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
            
        active_ids = context.get('active_ids', [])
        task_id = len(ids) and ids[0] or False
        
        summary_name = self.browse(cr, uid, ids)[0].name
        summary_type = self.browse(cr, uid, ids)[0].work_type
        
        #1. Poiscemo naloge, ki so morda ze v delu in jih premaknemo iz dela
        #1.1 Hkrati pa še kličemo funkcijo ki zaključi nalogo in izracuna ure
        proj_task_obj = self.pool.get('project.task')
        task_ids = proj_task_obj.search(cr, uid, [('user_id', '=', uid), ('in_progress', '=', True)])
        if task_ids:
            proj_task_obj.write(cr, uid, task_ids, {'in_progress': False})
            proj_task_obj.calculate_hours(cr, uid, task_ids, context)
            
        #2. Izbrano nalogo damo v delo
        proj_task_obj = self.pool.get('project.task')
        proj_task_obj.write(cr, uid, active_ids, {'in_progress': True})
        
        #3. Ustvarimo nov work summary
        task_id = len(active_ids) and active_ids[0] or False
        task_work_obj = self.pool.get('project.task.work')
        task_work_obj.create(cr, uid, { 'hours': False,
                                                'user_id': uid,
                                                'name': summary_name,
                                                'task_id': task_id,
                                                'in_progress': 1,
                                                'work_type': summary_type,
                                               })
        
        
        return {
                'type': 'ir.actions.act_window_close',
        }
    
work_summary_input()

