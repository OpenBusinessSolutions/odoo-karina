# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Mentis d.o.o. (<http://www.mentis.si>)
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

{
    "name": "Extends task management with auto task managements, Work summary, ...",
    "version": "1.0",
    "author": "Mentis d.o.o.",
    "category": "Project",
    "depends": ['project'],
    "description": """Task stage has new work types ('on hold' and 'in progress'). If task is moved to stage with type 'in_progress'
                      new 'Work summary' is created and all other tasks are moved back to stage with type 'on_hold'. 
                      There the 'Work summary is completed and working time is calculated...""",
    "init_xml": [],
    "update_xml": [	'wizard/work_summary_view.xml',
					'project_work_planning_view.xml',
	],
    "demo_xml": [],
    "active": False,
    "installable": True,
}
