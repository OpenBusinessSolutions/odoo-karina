# -*- encoding: utf-8 -*- #
############################################################################
#    Module Writen to OpenERP, Open Source Management Solution             #
#    Copyright (C) Vauxoo (<http://vauxoo.com>).                           #
#    All Rights Reserved                                                   #
###############Credits######################################################
#    Coded by: Sabrina Romero (sabrina@vauxoo.com)                         #
#    Planified by: Nhomar Hernandez (nhomar@vauxoo.com)                    #
#    Finance by: Vauxoo <info@vauxoo.com>                                  #
#    Audited by: Moises Lopez <moylop260@vauxoo.com>                       #
############################################################################
#    This program is free software: you can redistribute it and/or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation, either version 3 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>. #
############################################################################

from openerp.osv import osv


class UserStory(osv.osv):
    _description = "User Story Messages"
    _inherit = 'user.story'

    _track = {
        'state': {
            'user_story_messages.mt_us_new': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
            'user_story_messages.mt_us_open': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'open',
            'user_story_messages.mt_us_pending': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'pending',
            'user_story_messages.mt_us_done': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'done',
            'user_story_messages.mt_us_cancelled': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'cancelled',
        },
        'approved': {
            'user_story_messages.mt_us_approved': lambda self, cr, uid, obj, ctx=None: obj['approved'] == True,
        },
    }

    def message_track(self, cr, uid, ids, tracked_fields, initial_values, context=None):
        for proc in self.browse(cr, uid, ids, context=context):
            if tracked_fields.get("description", False) and proc.state == 'draft':
                return True
        return super(UserStory, self).message_track(cr, uid, [proc.id], tracked_fields, initial_values, context=context)
