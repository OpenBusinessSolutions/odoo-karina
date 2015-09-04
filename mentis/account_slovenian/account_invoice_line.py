# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP s.a. (<http://www.openerp.com>)
#    Copyright (C) 2013-TODAY Mentis d.o.o. (<http://www.mentis.si/openerp>)
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

from openerp.osv import osv

class account_invoice_line(osv.Model):
    _inherit = "account.invoice.line"

    def move_line_get(self, cr, uid, invoice_id, context=None):
        res = super(account_invoice_line,self).move_line_get(cr, uid, invoice_id, context=context)
        inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)

        if inv.type in ('in_invoice', 'out_invoice'):
            return res

        _res = []
        for _line in res:
            if _line.get('product_id', False):
                _product_id = self.pool.get('product.product').browse(cr, uid, _line ['product_id'], context)
                if _product_id and _product_id.valuation == 'real_time':

                    acc_out = _product_id.property_stock_account_output and _product_id.property_stock_account_output.id
                    if not acc_out:
                        acc_out = _product_id.categ_id.property_stock_account_output_categ and _product_id.categ_id.property_stock_account_output_categ.id                    

                    acc_in = _product_id.property_stock_account_input and _product_id.property_stock_account_input.id
                    if not acc_in:
                        acc_in = _product_id.categ_id.property_stock_account_input_categ and _product_id.categ_id.property_stock_account_input_categ.id

                    if acc_out and acc_in:
                        if inv.type == 'in_refund' and _line['account_id'] == acc_out:
                            _line['account_id'] = acc_in
                        if inv.type == 'out_refund' and _line['account_id'] == acc_in:
                            _line['account_id'] = acc_out
            _res.append(_line)
        return _res

    def product_id_change(self, cr, uid, ids, product, uom_id, qty=0, name='', type='out_invoice', partner_id=False, fposition_id=False, price_unit=False, currency_id=False, context=None, company_id=None):
        fiscal_pool = self.pool.get('account.fiscal.position')
        res = super(account_invoice_line, self).product_id_change(cr, uid, ids, product, uom_id, qty, name, type, partner_id, fposition_id, price_unit, currency_id, context, company_id)
        if not product:
            return res
        if type in ('in_invoice','in_refund'):
            product_obj = self.pool.get('product.product').browse(cr, uid, product, context=context)
            oa = product_obj.property_stock_account_input and product_obj.property_stock_account_input.id
            if not oa:
                oa = product_obj.categ_id.property_stock_account_input_categ and product_obj.categ_id.property_stock_account_input_categ.id
            if oa:
                fpos = fposition_id and fiscal_pool.browse(cr, uid, fposition_id, context=context) or False
                a = fiscal_pool.map_account(cr, uid, fpos, oa)
                res['value'].update({'account_id':a})
        return res
