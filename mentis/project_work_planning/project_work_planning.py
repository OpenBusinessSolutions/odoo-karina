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
from datetime import datetime
import time

from openerp.addons.base_status.base_stage import base_stage

class task(base_stage, osv.osv):
    _inherit = "project.task"
    _columns = {
        'in_progress': fields.boolean('In progress', readonly=True),
    }
    _defaults = {
        'in_progress': lambda *a: 0,
    }
    
    def calculate_hours(self, cr, uid, ids, context=None):
        task_work_obj = self.pool.get('project.task.work')
        task_work_ids = task_work_obj.search(cr, uid, [('task_id', '=', ids), ('in_progress', '=', 1)])
        for task_work in task_work_obj.browse(cr, uid, task_work_ids):
            ure = task_work.hours
            datum = datetime.strptime(task_work.date,'%Y-%m-%d %H:%M:%S') 
            datum_sedaj = datetime.now()
            
            if (datum.day == datum_sedaj.day and datum.month == datum_sedaj.month):
            
                razlike = datum_sedaj - datum
                minute = (razlike.seconds // 60)
                hours_double = float(minute) / 60
                
                task_work_obj.write(cr, uid, [task_work.id], {'hours': hours_double, 'in_progress': 0})
                
    def action_to_work(self, cr, uid, ids, context=None):
        
        #1. Poiscemo naloge, ki so morda ze v delu in jih premaknemo iz dela
        #1.1 Hkrati pa še kličemo funkcijo ki zaključi nalogo in izracuna ure
        task_ids = self.search(cr, uid, [('user_id', '=', uid), ('in_progress', '=', True)])
        if task_ids:
            self.write(cr, uid, task_ids, {'in_progress': False})
            self.calculate_hours(cr, uid, task_ids, context)
        
        #2. Izbrano nalogo damo v delo
        self.write(cr, uid, ids, {'in_progress': True})
        
        #3. Ustvarimo nov work summary
        task_id = len(ids) and ids[0] or False
        task_work_obj = self.pool.get('project.task.work')
        task_work_obj.create(cr, uid, { 'hours': False,
                                                'user_id': uid,
                                                'name': '',
                                                'task_id': task_id,
                                                'in_progress': 1,
                                                'work_type': 'delo',
                                               })
        return True
    
    def action_from_work(self, cr, uid, ids, context=None):
        #1. Izbrano nalogo damo iz dela
        self.write(cr, uid, ids, {'in_progress': False})
        
        #2. Izracunamo ure
        self.calculate_hours(cr, uid, ids, context)

    
    def write_staro(self, cr, uid, ids, vals, context=None):
        
        #Lovimo dogodek ob spremembi stage-a
        if vals and not 'kanban_state' in vals and 'stage_id' in vals:
            
            old_stage  = self.browse(cr, uid, ids, context=None)[0].stage_id.id
            new_stage = vals.get('stage_id')
            
            task_work_obj = self.pool.get('project.task.work')
            ptt_obj = self.pool.get('project.task.type')
            stage_working = ptt_obj.search(cr, uid, [('stage_type', '=', 'in_progress')])[0]
            stage_waiting = ptt_obj.search(cr, uid, [('stage_type', '=', 'on_hold')])[0]
            
            #Ce smo premaknili v delo
            if new_stage == stage_working: 
                #Ustvarimo nov work summary
                task_work_obj.create(cr, uid, { 'hours': False,
                                                'user_id': uid,
                                                'name': '',
                                                'task_id': ids[0],
                                                'in_progress': 1,
                                                'work_type': 'delo',
                                               })
                
                #Poiscemo ali so v delu ze katere druge naloge in jih premaknemo iz dela
                task_ids = self.search(cr, uid, [('user_id', '=', uid), ('stage_id', '=', stage_working), ('id', '!=', ids[0])])
                for task_id in task_ids:
                    self.write(cr, uid, [task_id], {'stage_id':stage_waiting})
                    
                    
            #Ce je premik iz dela (manualni ali avtomatski) potem zakljucimo nalogo in zapisemo ure
            elif old_stage == stage_working:
                
                task_work_ids = task_work_obj.search(cr, uid, [('task_id', '=', ids), ('in_progress', '=', 1)])
                for task_work in task_work_obj.browse(cr, uid, task_work_ids):
                    ure = task_work.hours
                    datum = datetime.strptime(task_work.date,'%Y-%m-%d %H:%M:%S') 
                    datum_sedaj = datetime.now()
                    
                    if (datum.day == datum_sedaj.day and datum.month == datum_sedaj.month):
                    
                        razlike = datum_sedaj - datum
                        minute = (razlike.seconds // 60)
                        hours_double = float(minute) / 60
                        
                        task_work_obj.write(cr, uid, [task_work.id], {'hours': hours_double, 'in_progress': 0})
        
        res = super(task,self).write(cr, uid, ids, vals, context)
task()


class project_work(osv.osv):
    _inherit = "project.task.work"
    _columns = {
        'in_progress': fields.boolean('In progress'),
        'work_type': fields.selection([('delo','Delo'),('malica','Malica'),('privat','Privat odhod')], 'Work type', required=True),
    }

    _defaults = {
        'in_progress': lambda *a: 0,
        'work_type': lambda *a: 'delo',
    }
    
project_work()


class project_task_type(osv.osv):
    _inherit = 'project.task.type'
    _columns = {
        'stage_type': fields.selection([('default','Default'),('on_hold','Working - on hold'),('in_progress','Working - in progress')], 'Stage type', required=True),
    }

    _defaults = {
        'stage_type': lambda *a: 'default',
    }
    
    def _check_stage_type(self, cr, uid, ids, context=None):
        
        stage_working = self.search(cr, uid, [('stage_type', '=', 'in_progress')])
        if len(stage_working) > 1:
            return False
        
        stage_waiting = self.search(cr, uid, [('stage_type', '=', 'on_hold')])
        if len(stage_waiting) > 1:
            return False
        
        return True

    _constraints = [
        (_check_stage_type, '\n\nStage type "Working - on hold" and "Working - in progress" can be assigned only ones!', ['stage_type'])
    ]

project_task_type()
