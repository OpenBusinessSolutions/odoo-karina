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


import openerp.netsvc
from openerp.osv import osv, fields
from openerp.tools.translate import _


class purchase_requisition_line(osv.osv):

    _inherit = "purchase.requisition.line"

    def _get_status(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, 'draft')
        for line in self.browse(cr, uid, ids, context=context):
#             if  not (line.po_line_ids or (line.selected_flag and line.partner_ids)):
#                 res[line.id] = 'cancel'
            for  po in line.po_line_ids:
                if po.state == 'draft' and res[line.id] != 'done':
                    res[line.id] = 'in_purchase'
                else:
                    if po.state == 'confirmed' or po.state == 'done':
                        res[line.id] = 'done'
                    else:
                        if po.state == 'cancel' and res[line.id] != 'done':
                                res[line.id] = 'cancel'
        return res

    _columns = {
        'partner_ids': fields.many2many('res.partner', 'pr_rel_partner',
                                        'pr_line_id',
                                        'partner_id', 'Suppliers', ),
        'selected_flag': fields.boolean("Select"),
        'po_line_ids': fields.many2many('purchase.order.line', 'pr_rel_po',
                                        'pr_id', 'po_id',
                                        'Purchase Line Orders',
                                        ondelete='cascade'),
        'state': fields.function(_get_status, string='Status', readonly=True,
                                 type='selection',
                                 selection=[('draft', 'New'),
                                        ('in_purchase', 'In Progress'),
                                        ('done', 'Purchase Done'),
                                        ('cancel', 'Cancelled')]),
    }
    _default = {
               'selected_flag': True,
               'po_line_ids': False,
               }

    def copy(self, cr, uid, ids, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'po_line_ids': False,
        })
        return super(purchase_requisition_line,
                      self).copy(cr, uid, ids, default, context)

    def write(self, cr, uid, ids, vals, context=None):
        res = super(purchase_requisition_line,
                    self).write(cr, uid, ids, vals, context=context)
        return res

    def create(self, cr, uid, vals, context=None):
        #Remove po_line_ids if duplicate data
        if context.get('__copy_data_seen', False):
            vals.update({'po_line_ids': False})
        res_id = super(purchase_requisition_line,
                        self).create(cr, uid, vals, context=context)
        return res_id

    def selected_flag_onchange(self, cr, uid, ids, selected_flag, context=None):
        res = {'value': {'all_selected': True}}
        if not selected_flag:
            res['value'].update({'all_selected': False})
        return res

    def default_get(self, cr, uid, fields, context=None):
        return super(purchase_requisition_line,
                        self).default_get(cr, uid, fields, context=context)
purchase_requisition_line()


class purchase_requisition(osv.osv):
    _inherit = 'purchase.requisition'
    _columns = {
        'all_selected': fields.boolean("All Select(s)"),
    }
    _default = {
               'all_selected': True,
               }

    def all_selected_onchange(self, cr, uid, ids,
                               all_selected, line_ids, context=None):
        res = {'value': {'line_ids': False}}

        for index in range(len(line_ids)):
            if line_ids[index][0] in (0, 1, 4):
                if line_ids[index][2]:
                    line_ids[index][2].update({'selected_flag': all_selected})
                else:
                    if line_ids[index][0] == 4:
                        line_ids[index][0] = 1
                    line_ids[index][2] = {'selected_flag': all_selected}

        res['value']['line_ids'] = line_ids

        return res

    def update_done(self, cr, uid, ids, context=None):
        pr_recs = self.browse(cr, uid, ids, context=context)
        prs_done = []

        for rec in pr_recs:
            is_done = True
            for line in rec.line_ids:
                is_done = is_done and line.state in ('done', 'cancel')

            if is_done:
                prs_done.append(rec.id)

        self.tender_done(cr, uid, prs_done, context=None)
        return True

    def copy(self, cr, uid, ids, default=None, context=None):
        if not default:
            default = {}
        return super(purchase_requisition,
                      self).copy(cr, uid, ids, default, context)

    def action_createPO(self, cr, uid, ids, context=None):

        selected = False
        for pr in self.browse(cr, uid, ids, context):
            for line_id in pr.line_ids:
                if line_id.selected_flag:
                    selected = True

        if not selected:
            raise osv.except_osv(_('Warning!'), _('Please select the PR Line(s) at least one line'))

        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        result = mod_obj.get_object_reference(cr, uid, 'purchase_requisition', 'action_purchase_requisition_partner')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]

        return result
purchase_requisition()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
