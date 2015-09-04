# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: Luis Torres (luis_t@vauxoo.com)
############################################################################
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
from openerp.osv import fields, osv
from openerp.tools.translate import _


class UpdateAmountBaseTaxWizard(osv.osv_memory):
    _name = 'update.amount.tax.wizard'

    _columns = {
        'warning': fields.text('WARNING!', readonly=True),
        'update_tax_sec': fields.boolean('Update Tax Secondary', help='If this field is active, '
            'was updated the tax secondary of Journal Items although already have tax secondary'),
        'update_amount_base': fields.boolean('Update Amount Base', help='If this field is '
            'active, was updated the amount base of Journal Items although already have '
            'this amount'),
    }

    _defaults = {
        'warning': _('This wizard only should be used when the company have '
        'configured a tax by purchases and other by sales for each amount to '
        'tax, and the account of each tax is configured correctly')
    }

    def update_tax_secondary(self, cr, uid, ids, company_id, tax_ids, context=None):
        if not context:
            context = {}
        data = self.browse(cr, uid, ids[0], context=context)
        acc_tax_obj = self.pool.get('account.tax')
        move_line_obj = self.pool.get('account.move.line')
        acc_collected_ids = []
        for tax in acc_tax_obj.browse(cr, uid, tax_ids, context=context):
            acc_collected_ids.append(tax.account_collected_voucher_id.id)
            acc_collected_ids.append(tax.account_paid_voucher_id.id)
        attrs = [('account_id', 'in', list(set(acc_collected_ids))), ('company_id', '=', company_id)]
        if not data.update_tax_sec:
            attrs.append(('tax_id_secondary', '=', None))
        line_ids = move_line_obj.search(cr, uid, attrs, context=context)
        for line in move_line_obj.browse(cr, uid, line_ids, context=context):
            tax_line = acc_tax_obj.search(cr, uid, [('name', '=', line.name),
                ('id', 'in', tax_ids)], context=context)
            if tax_line:
                cr.execute("""UPDATE account_move_line
                    SET tax_id_secondary = %s
                    WHERE id = %s""", (tax_line[0], line.id))
        lines_incorects_ids = move_line_obj.search(cr, uid, [('company_id', '=', company_id),
            ('tax_id_secondary', '!=', False),
            ('account_id', 'not in', list(set(acc_collected_ids)))], context=context)
        for line in lines_incorects_ids:
            cr.execute("""UPDATE account_move_line
                SET tax_id_secondary = Null
                WHERE id = %s""", (line,))
        return True

    def apply(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        data = self.browse(cr, uid, ids[0], context=context)
        move_line_obj = self.pool.get('account.move.line')
        acc_tax_category_obj = self.pool.get('account.tax.category')
        acc_tax_obj = self.pool.get('account.tax')
        company_id = self.pool.get('res.company')._company_default_get(cr, uid,
            'update.amount.tax.wizard', context=context)
        category_iva_ids = acc_tax_category_obj.search(cr, uid, [
            ('name', 'in', ('IVA', 'IVA-EXENTO', 'IVA-RET', 'IVA-PART'))], context=context)
        tax_ids = acc_tax_obj.search(cr, uid, [
            ('company_id', '=', company_id),
            ('type_tax_use', '=', 'purchase'),
            ('tax_category_id', 'in', category_iva_ids)], context=context)
        self.update_tax_secondary(cr, uid, ids, company_id, tax_ids, context=context)
        attrs = [('tax_id_secondary', 'in', tax_ids)]
        if not data.update_amount_base:
            attrs.append('|',)
            attrs.append(('amount_base', '=', 0))
            attrs.append(('amount_base', '=', False))
        lines_without_amount = move_line_obj.search(cr, uid, attrs, context=context)
        for move in move_line_obj.browse(cr, uid, lines_without_amount, context=context):
            amount_tax = move.tax_id_secondary.tax_category_id.value_tax or move.tax_id_secondary.amount
            amount_base = 0
            if move.debit != 0:
                amount_base = move.debit
            elif move.credit != 0:
                amount_base = move.credit
            if move.tax_id_secondary.amount == 0:
                amount_base = move.tax_voucher_id and move.tax_voucher_id.amount_base or 0
            if amount_tax != 0:
                cr.execute("""UPDATE account_move_line
                    SET amount_base = %s
                    WHERE id = %s""", (abs(amount_base / amount_tax), move.id))
            else:
                if amount_base:
                    cr.execute("""UPDATE account_move_line
                        SET amount_base = %s
                        WHERE id = %s""", (amount_base, move.id))
        lines_incorects_ids = move_line_obj.search(cr, uid, [('company_id', '=', company_id),
            ('amount_base', '!=', False), ('tax_id_secondary', '=', False)], context=context)
        for line in lines_incorects_ids:
            cr.execute("""UPDATE account_move_line
                SET amount_base = Null
                WHERE id = %s""", (line,))
        #~ move_concile_ids = move_line_obj.search(cr, uid, ['|',\
            #~ ('reconcile_id', '!=', False),\
            #~ ('reconcile_partial_id', '!=', False)], context=context)
        #~ list_moves = []
        #~ for line in move_line_obj.browse(cr, uid, move_concile_ids,\
            #~ context=context):
            #~ list_moves.append(line.move_id)
        #~ list_moves = list(set(list_moves))
        #~ for move in list_moves:
            #~ move_tax = move_line_obj.search(cr, uid, [('move_id', '=', move.id),
            #~ ('tax_id_secondary', '!=', False), ('reconcile_id','=', False),
            #~ ('reconcile_partial_id', '=', False)])
            #~ reconcile_id = False
            #~ reconcile_partial_id = False
            #~ for line in move.line_id:
            #~ if line.reconcile_id:
            #~ reconcile_id = line.reconcile_id.id
            #~ continue
            #~ if line.reconcile_partial_id:
            #~ reconcile_partial_id = line.reconcile_partial_id.id
            #~ continue
            #~ for line in move_line_obj.browse(cr, uid, move_tax, context=context):
            #~ if reconcile_id:
            #~ cr.execute("""UPDATE account_move_line
            #~ SET reconcile_id = %s
            #~ WHERE id = %s""", (reconcile_id, line.id))
            #~ if reconcile_partial_id:
            #~ cr.execute("""UPDATE account_move_line
            #~ SET reconcile_partial_id = %s
            #~ WHERE id = %s""", (reconcile_partial_id, line.id))
        return True
