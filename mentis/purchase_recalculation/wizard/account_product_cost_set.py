# -*- coding: utf-8 -*-
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

from osv import fields, osv
from tools.translate import _
from datetime import datetime
import time
import openerp.addons.decimal_precision as dp

class account_product_cost_set(osv.TransientModel):
    _name="account.product.cost.set"
    _description="Set Product Costs"
    
    _columns = {
        'period_id': fields.many2one('account.period', "Period", required=True, help="Period to set cost values for."),
        'type': fields.selection((('0', 'Set cost value on existing account move lines'),
                                  ('1', 'Create cost moves per period/product'),
                                  ('2', 'Create cost moves per period/product category'),
                                  ('3', 'Create cost moves per period/account')), 'Type', translate=True, required=True)
    }
    _defaults = {
        'period_id': False,
        'type': '0'
    }
    
    def _get_valuation_data(self, cr, uid, _period_id, _date_from, _date_to, _type):
        _res = []
        _journal_ids = []
        
        if _type == '1':
            _fields = 'product_id,'
        elif _type == '2':
            _fields = 'category_id,'
        else:
            _fields = ''
        
        _sql_string = 'WITH loc_stock AS (SELECT lot_stock_id AS location_id \n ' \
                      '                     FROM stock_warehouse \n ' \
                      '                 GROUP BY lot_stock_id), \n ' \
                      '      loc_supp AS (SELECT id AS location_id \n ' \
                      '                     FROM stock_location \n ' \
                      '                    WHERE usage = \'supplier\'), \n ' \
                      '    stock_data AS (SELECT sm.product_id AS product_id, \n ' \
                      '                          SUM(CASE \n ' \
                      '                                WHEN sm.date < \'{date_from}\' \n ' \
                      '                                  THEN \n ' \
                      '                                    CASE \n ' \
                      '                                      WHEN sm.location_id IN (SELECT location_id \n ' \
                      '                                                                FROM loc_stock) \n ' \
                      '                                           AND sm.location_dest_id NOT IN (SELECT location_id \n ' \
                      '                                                                             FROM loc_stock) \n ' \
                      '                                        THEN sm.product_qty * -1 \n ' \
                      '                                      WHEN sm.location_id NOT IN (SELECT location_id \n ' \
                      '                                                                    FROM loc_stock) \n ' \
                      '                                           AND sm.location_dest_id IN (SELECT location_id \n ' \
                      '                                                                         FROM loc_stock) \n ' \
                      '                                        THEN sm.product_qty \n ' \
                      '                                      ELSE 0.0 \n ' \
                      '                                    END \n ' \
                      '                                ELSE 0.0 \n ' \
                      '                              END) AS stock_start, \n ' \
                      '                          SUM(CASE \n ' \
                      '                                WHEN sm.date BETWEEN \'{date_from}\' AND \'{date_to}\' \n ' \
                      '                                  THEN \n ' \
                      '                                    CASE \n ' \
                      '                                      WHEN sm.location_id IN (SELECT location_id \n ' \
                      '                                                                FROM loc_stock) \n ' \
                      '                                           AND sm.location_dest_id IN (SELECT location_id \n ' \
                      '                                                                         FROM loc_supp) \n ' \
                      '                                        THEN sm.product_qty * -1 \n ' \
                      '                                      WHEN sm.location_id IN (SELECT location_id \n ' \
                      '                                                                FROM loc_supp) \n ' \
                      '                                           AND sm.location_dest_id IN (SELECT location_id \n ' \
                      '                                                                         FROM loc_stock) \n ' \
                      '                                        THEN sm.product_qty \n ' \
                      '                                      ELSE 0.0 \n ' \
                      '                                    END \n ' \
                      '                                ELSE 0.0 \n ' \
                      '                              END) AS stock_in, \n ' \
                      '                          SUM(CASE \n ' \
                      '                                WHEN sm.date <= \'{date_to}\' \n ' \
                      '                                  THEN \n ' \
                      '                                    CASE \n ' \
                      '                                      WHEN sm.location_id IN (SELECT location_id \n ' \
                      '                                                                FROM loc_stock) \n ' \
                      '                                           AND sm.location_dest_id NOT IN (SELECT location_id \n ' \
                      '                                                                             FROM loc_stock) \n ' \
                      '                                        THEN sm.product_qty * -1 \n ' \
                      '                                      WHEN sm.location_id NOT IN (SELECT location_id \n ' \
                      '                                                                    FROM loc_stock) \n ' \
                      '                                           AND sm.location_dest_id IN (SELECT location_id \n ' \
                      '                                                                         FROM loc_stock) \n ' \
                      '                                        THEN sm.product_qty \n ' \
                      '                                      ELSE 0.0 \n ' \
                      '                                    END \n ' \
                      '                                ELSE 0.0 \n ' \
                      '                              END) AS stock_end \n ' \
                      '                     FROM stock_move AS sm \n ' \
                      '                          INNER JOIN product_product AS pp ON pp.id = sm.product_id \n ' \
                      '                                                              AND pp.valuation = \'manual_periodic\' \n ' \
                      '                          INNER JOIN product_template AS pt ON pt.id = pp.product_tmpl_id \n ' \
                      '                                                               AND pt.type = \'product\' \n ' \
                      '                                                               AND pt.cost_method = \'average\' \n ' \
                      '                    WHERE sm.state = \'done\' \n ' \
                      '                          AND sm.date <= \'{date_to}\' \n ' \
                      '                          AND (sm.location_id IN (SELECT location_id \n ' \
                      '                                                    FROM loc_stock) \n ' \
                      '                               OR sm.location_dest_id IN (SELECT location_id \n ' \
                      '                                                            FROM loc_stock)) \n ' \
                      '                 GROUP BY sm.product_id), \n ' \
                      '         costs AS (SELECT sd.product_id AS product_id, \n ' \
                      '                          pt.categ_id AS category_id, \n ' \
                      '                          ppc.price_unit AS price_unit, \n ' \
                      '                          CASE \n ' \
                      '                            WHEN EXISTS (SELECT ir.value_reference \n ' \
                      '                                           FROM ir_property AS ir \n ' \
                      '                                          WHERE ir.name = \'property_stock_journal\' \n ' \
                      '                                                AND ir.res_id = \'product.template,\' || sd.product_id::VARCHAR \n ' \
                      '                                                AND ir.value_reference IS NOT NULL) \n ' \
                      '                              THEN (SELECT SUBSTRING(ir.value_reference, POSITION(\',\' IN ir.value_reference) + 1) \n ' \
                      '                                      FROM ir_property AS ir \n ' \
                      '                                     WHERE ir.name = \'property_stock_journal\' \n ' \
                      '                                           AND ir.res_id = \'product.template,\' || sd.product_id::VARCHAR) \n ' \
                      '                            WHEN EXISTS (SELECT ir.value_reference \n ' \
                      '                                           FROM ir_property AS ir \n ' \
                      '                                          WHERE ir.name = \'property_stock_journal\' \n ' \
                      '                                                AND ir.res_id = \'product.category,\' || pt.categ_id::VARCHAR \n ' \
                      '                                                AND ir.value_reference IS NOT NULL) \n ' \
                      '                              THEN (SELECT SUBSTRING(ir.value_reference, POSITION(\',\' IN ir.value_reference) + 1) \n ' \
                      '                                      FROM ir_property AS ir \n ' \
                      '                                     WHERE ir.name = \'property_stock_journal\' \n ' \
                      '                                           AND ir.res_id = \'product.category,\' || pt.categ_id::VARCHAR) \n ' \
                      '                            ELSE (SELECT SUBSTRING(ir.value_reference, POSITION(\',\' IN ir.value_reference) + 1) \n ' \
                      '                                    FROM ir_property AS ir \n ' \
                      '                                   WHERE ir.name = \'property_stock_journal\' \n ' \
                      '                                         AND ir.res_id IS NULL) \n ' \
                      '                          END::INTEGER AS stock_journal, \n ' \
                      '                          CASE \n ' \
                      '                            WHEN EXISTS (SELECT ir.value_reference \n ' \
                      '                                           FROM ir_property AS ir \n ' \
                      '                                          WHERE ir.name = \'property_stock_valuation_account_id\' \n ' \
                      '                                                AND ir.res_id = \'product.template,\' || sd.product_id::VARCHAR \n ' \
                      '                                                AND ir.value_reference IS NOT NULL) \n ' \
                      '                              THEN (SELECT SUBSTRING(ir.value_reference, POSITION(\',\' IN ir.value_reference) + 1) \n ' \
                      '                                      FROM ir_property AS ir \n ' \
                      '                                     WHERE ir.name = \'property_stock_valuation_account_id\' \n ' \
                      '                                           AND ir.res_id = \'product.template,\' || sd.product_id::VARCHAR) \n ' \
                      '                            WHEN EXISTS (SELECT ir.value_reference \n ' \
                      '                                           FROM ir_property AS ir \n ' \
                      '                                          WHERE ir.name = \'property_stock_valuation_account_id\' \n ' \
                      '                                                AND ir.res_id = \'product.category,\' || pt.categ_id::VARCHAR \n ' \
                      '                                                AND ir.value_reference IS NOT NULL) \n ' \
                      '                              THEN (SELECT SUBSTRING(ir.value_reference, POSITION(\',\' IN ir.value_reference) + 1) \n ' \
                      '                                      FROM ir_property AS ir \n ' \
                      '                                     WHERE ir.name = \'property_stock_valuation_account_id\' \n ' \
                      '                                           AND ir.res_id = \'product.category,\' || pt.categ_id::VARCHAR) \n ' \
                      '                            ELSE (SELECT SUBSTRING(ir.value_reference, POSITION(\',\' IN ir.value_reference) + 1) \n ' \
                      '                                    FROM ir_property AS ir \n ' \
                      '                                    WHERE ir.name = \'property_stock_valuation_account_id\' \n ' \
                      '                                          AND ir.res_id IS NULL) \n ' \
                      '                          END::INTEGER AS stock_account_valuation, \n ' \
                      '                          CASE \n ' \
                      '                            WHEN EXISTS (SELECT ir.value_reference \n ' \
                      '                                           FROM ir_property AS ir \n ' \
                      '                                          WHERE ir.name = \'property_stock_account_input\' \n ' \
                      '                                                AND ir.res_id = \'product.template,\' || sd.product_id::VARCHAR \n ' \
                      '                                                AND ir.value_reference IS NOT NULL) \n ' \
                      '                              THEN (SELECT SUBSTRING(ir.value_reference, POSITION(\',\' IN ir.value_reference) + 1) \n ' \
                      '                                      FROM ir_property AS ir \n ' \
                      '                                     WHERE ir.name = \'property_stock_account_input\' \n ' \
                      '                                           AND ir.res_id = \'product.template,\' || sd.product_id::VARCHAR) \n ' \
                      '                            WHEN EXISTS (SELECT ir.value_reference \n ' \
                      '                                           FROM ir_property AS ir \n ' \
                      '                                          WHERE ir.name = \'property_stock_account_input_categ\' \n ' \
                      '                                                AND ir.res_id = \'product.category,\' || pt.categ_id::VARCHAR \n ' \
                      '                                                AND ir.value_reference IS NOT NULL) \n ' \
                      '                              THEN (SELECT SUBSTRING(ir.value_reference, POSITION(\',\' IN ir.value_reference) + 1) \n ' \
                      '                                      FROM ir_property AS ir \n ' \
                      '                                     WHERE ir.name = \'property_stock_account_input_categ\' \n ' \
                      '                                           AND ir.res_id = \'product.category,\' || pt.categ_id::VARCHAR) \n ' \
                      '                            ELSE (SELECT SUBSTRING(ir.value_reference, POSITION(\',\' IN ir.value_reference) + 1) \n ' \
                      '                                    FROM ir_property AS ir \n ' \
                      '                                   WHERE ir.name = \'property_stock_account_input\' \n ' \
                      '                                         AND ir.res_id IS NULL) \n ' \
                      '                          END::INTEGER AS stock_account_input, \n ' \
                      '                          CASE \n ' \
                      '                            WHEN EXISTS (SELECT ir.value_reference \n ' \
                      '                                           FROM ir_property AS ir \n ' \
                      '                                          WHERE ir.name = \'property_stock_account_output\' \n ' \
                      '                                                AND ir.res_id = \'product.template,\' || sd.product_id::VARCHAR \n ' \
                      '                                                AND ir.value_reference IS NOT NULL) \n ' \
                      '                              THEN (SELECT SUBSTRING(ir.value_reference, POSITION(\',\' IN ir.value_reference) + 1) \n ' \
                      '                                      FROM ir_property AS ir \n ' \
                      '                                     WHERE ir.name = \'property_stock_account_output\' \n ' \
                      '                                           AND ir.res_id = \'product.template,\' || sd.product_id::VARCHAR) \n ' \
                      '                            WHEN EXISTS (SELECT ir.value_reference \n ' \
                      '                                           FROM ir_property AS ir \n ' \
                      '                                          WHERE ir.name = \'property_stock_account_output_categ\' \n ' \
                      '                                                AND ir.res_id = \'product.category,\' || pt.categ_id::VARCHAR \n ' \
                      '                                                AND ir.value_reference IS NOT NULL) \n ' \
                      '                              THEN (SELECT SUBSTRING(ir.value_reference, POSITION(\',\' IN ir.value_reference) + 1) \n ' \
                      '                                      FROM ir_property AS ir \n ' \
                      '                                     WHERE ir.name = \'property_stock_account_output_categ\' \n ' \
                      '                                           AND ir.res_id = \'product.category,\' || pt.categ_id::VARCHAR) \n ' \
                      '                            ELSE (SELECT SUBSTRING(ir.value_reference, POSITION(\',\' IN ir.value_reference) + 1) \n ' \
                      '                                    FROM ir_property AS ir \n ' \
                      '                                   WHERE ir.name = \'property_stock_account_output\' \n ' \
                      '                                         AND ir.res_id IS NULL) \n ' \
                      '                          END::INTEGER AS stock_account_output, \n ' \
                      '                          CASE \n ' \
                      '                            WHEN EXISTS (SELECT ir.value_reference \n ' \
                      '                                           FROM ir_property AS ir \n ' \
                      '                                          WHERE ir.name = \'property_account_expense\' \n ' \
                      '                                                AND ir.res_id = \'product.template,\' || sd.product_id::VARCHAR \n ' \
                      '                                                AND ir.value_reference IS NOT NULL) \n ' \
                      '                              THEN (SELECT SUBSTRING(ir.value_reference, POSITION(\',\' IN ir.value_reference) + 1) \n ' \
                      '                                      FROM ir_property AS ir \n ' \
                      '                                     WHERE ir.name = \'property_account_expense\' \n ' \
                      '                                           AND ir.res_id = \'product.template,\' || sd.product_id::VARCHAR) \n ' \
                      '                            WHEN EXISTS (SELECT ir.value_reference \n ' \
                      '                                           FROM ir_property AS ir \n ' \
                      '                                          WHERE ir.name = \'property_account_expense_categ\' \n ' \
                      '                                                AND ir.res_id = \'product.category,\' || pt.categ_id::VARCHAR \n ' \
                      '                                                AND ir.value_reference IS NOT NULL) \n ' \
                      '                              THEN (SELECT SUBSTRING(ir.value_reference, POSITION(\',\' IN ir.value_reference) + 1) \n ' \
                      '                                      FROM ir_property AS ir \n ' \
                      '                                     WHERE ir.name = \'property_account_expense_categ\' \n ' \
                      '                                           AND ir.res_id = \'product.category,\' || pt.categ_id::VARCHAR) \n ' \
                      '                            ELSE (SELECT SUBSTRING(ir.value_reference, POSITION(\',\' IN ir.value_reference) + 1) \n ' \
                      '                                    FROM ir_property AS ir \n ' \
                      '                                   WHERE ir.name = \'property_account_expense\' \n ' \
                      '                                         AND ir.res_id IS NULL) \n ' \
                      '                          END::INTEGER AS stock_account_expense, \n ' \
                      '                          SUM(sd.stock_start) AS stock_start, \n ' \
                      '                          SUM(sd.stock_in) AS stock_in, \n ' \
                      '                          SUM(sd.stock_end) AS stock_end, \n ' \
                      '                          SUM(sd.stock_start) + SUM(stock_in) - SUM(stock_end) AS cost_quantity, \n ' \
                      '                          ROUND((SUM(sd.stock_start) + SUM(stock_in) - SUM(stock_end)) * ppc.price_unit, 2) AS cost_value \n ' \
                      '                     FROM stock_data AS sd \n ' \
                      '                          INNER JOIN product_product AS pp ON pp.id = sd.product_id \n ' \
                      '                          INNER JOIN product_template AS pt ON pt.id = pp.product_tmpl_id \n ' \
                      '                          INNER JOIN product_period_cost AS ppc ON ppc.product_id = pp.id \n ' \
                      '                                                                   AND ppc.period_id = {period_id} \n ' \
                      '                 GROUP BY sd.product_id, pt.categ_id, ppc.price_unit \n ' \
                      '                   HAVING SUM(sd.stock_start) + SUM(stock_in) - SUM(stock_end) <> 0) \n ' \
                      '  SELECT stock_journal, \n ' \
                      '         {fields} \n ' \
                      '         stock_account_valuation, \n ' \
                      '         stock_account_input, \n ' \
                      '         stock_account_output, \n ' \
                      '         stock_account_expense, \n ' \
                      '         SUM(cost_value) \n ' \
                      '    FROM costs \n ' \
                      'GROUP BY stock_journal, {fields} stock_account_valuation, stock_account_input, stock_account_output, stock_account_expense \n ' \
                      'ORDER BY stock_journal, {fields} stock_account_valuation, stock_account_input, stock_account_output, stock_account_expense;'.format(fields = _fields,
                                                                                                                                                           date_from = _date_from,
                                                                                                                                                           date_to = _date_to,
                                                                                                                                                           period_id = _period_id)
        cr.execute(_sql_string)
        _lines = cr.fetchall()        
        for _line in _lines:
            _output_line = False
            
            _res_line_stock_c = {'date': _date_to,
                                 'period_id': _period_id,
                                 'tax_period_id': _period_id}
            _res_line_output_d = _res_line_stock_c.copy()
            _res_line_output_c = _res_line_stock_c.copy()
            _res_line_expense_d = _res_line_stock_c.copy()

            if not _line[0] in _journal_ids:
                _journal_ids.append(_line[0])

            if _type == '1':
                _product_id = self.pool.get('product.product').browse(cr, uid, _line[1])
                if _product_id:
                    _res_line_stock_c['name'] = _product_id.name
                    _res_line_stock_c['journal_id'] = _line[0]
                    if _line[2]:
                        _res_line_stock_c['account_id'] = _line[2]
                    else:
                        _res_line_stock_c['account_id'] = _line[3]
                    _res_line_stock_c['credit'] = _line[6]
                    _res_line_stock_c['debit'] = 0.0
                    
                    if _line[4]:
                        _output_line = True
                        _res_line_output_d['name'] = _product_id.name
                        _res_line_output_d['journal_id'] = _line[0]
                        _res_line_output_d['account_id'] = _line[4]
                        _res_line_output_d['credit'] = 0.0
                        _res_line_output_d['debit'] = _line[6]
                        _res_line_output_c['name'] = _product_id.name
                        _res_line_output_c['journal_id'] = _line[0]
                        _res_line_output_c['account_id'] = _line[4]
                        _res_line_output_c['credit'] = _line[6]
                        _res_line_output_c['debit'] = 0.0

                    _res_line_expense_d['name'] = _product_id.name
                    _res_line_expense_d['journal_id'] = _line[0]
                    _res_line_expense_d['account_id'] = _line[5]
                    _res_line_expense_d['credit'] = 0.0
                    _res_line_expense_d['debit'] = _line[6]

            elif _type == '2':
                _category_id = self.pool.get('product.category').browse(cr, uid, _line[1])
                if _category_id:
                    _res_line_stock_c['name'] = _product_id.name
                    _res_line_stock_c['journal_id'] = _line[0]
                    if _line[2]:
                        _res_line_stock_c['account_id'] = _line[2]
                    else:
                        _res_line_stock_c['account_id'] = _line[3]
                    _res_line_stock_c['credit'] = _line[6]
                    _res_line_stock_c['debit'] = 0.0

                    if _line[4]:
                        _output_line = True
                        _res_line_output_d['name'] = _product_id.name
                        _res_line_output_d['journal_id'] = _line[0]
                        _res_line_output_d['account_id'] = _line[4]
                        _res_line_output_d['credit'] = 0.0
                        _res_line_output_d['debit'] = _line[6]
                        _res_line_output_c['name'] = _product_id.name
                        _res_line_output_c['journal_id'] = _line[0]
                        _res_line_output_c['account_id'] = _line[4]
                        _res_line_output_c['credit'] = _line[6]
                        _res_line_output_c['debit'] = 0.0

                    _res_line_expense_d['name'] = _product_id.name
                    _res_line_expense_d['journal_id'] = _line[0]
                    _res_line_expense_d['account_id'] = _line[5]
                    _res_line_expense_d['credit'] = 0.0
                    _res_line_expense_d['debit'] = _line[6]

            else:
                _res_line_stock_c['name'] = _('Stock Valuation Move Line')
                _res_line_stock_c['journal_id'] = _line[0]
                if _line[1]:
                    _res_line_stock_c['account_id'] = _line[1]
                else:
                    _res_line_stock_c['account_id'] = _line[2]
                _res_line_stock_c['credit'] = _line[5]
                _res_line_stock_c['debit'] = 0.0

                if _line[3]:
                    _output_line = True
                    _res_line_output_d['name'] = _('Stock Output Debit Move Line')
                    _res_line_output_d['journal_id'] = _line[0]
                    _res_line_output_d['account_id'] = _line[3]
                    _res_line_output_d['credit'] = 0.0
                    _res_line_output_d['debit'] = _line[5]
                    _res_line_output_c['name'] = _('Stock Output Credit Move Line')
                    _res_line_output_c['journal_id'] = _line[0]
                    _res_line_output_c['account_id'] = _line[3]
                    _res_line_output_c['credit'] = _line[5]
                    _res_line_output_c['debit'] = 0.0

                _res_line_expense_d['name'] = _('Stock Expense Move Line')
                _res_line_expense_d['journal_id'] = _line[0]
                _res_line_expense_d['account_id'] = _line[4]
                _res_line_expense_d['credit'] = 0.0
                _res_line_expense_d['debit'] = _line[5]

            _res.append(_res_line_expense_d)
            if _output_line:
                _res.append(_res_line_output_c)
                _res.append(_res_line_output_d)
            _res.append(_res_line_stock_c)

        return [_journal_ids, _res]
    
    def _do_real_time(self, cr, uid, ids, context=None):
        _recalculation_id = self.browse(cr, uid, ids[0], context)
        _dates = {}
        _digits = {}

        # najdem ustrezna obdobja
        if _recalculation_id.period_id:
            _period_id = _recalculation_id.period_id
        else:
            raise osv.except_osv(_('Error!'), _('Cannot find suitable dates for recalculation.'))
        
        _date_from = _period_id.date_start
        _date_to = _period_id.date_stop
            
        # najdem ustrezne izdelke
        _product_ids = []
        
        _location_ids = self.pool.get('stock.location').search(cr, uid, [('usage','=','internal')])
        _sql_string = '  SELECT sm.product_id AS id \n ' \
                      '    FROM stock_move AS sm \n ' \
                      '         INNER JOIN product_product AS pp ON pp.id = sm.product_id \n ' \
                      '                                             AND pp.valuation = \'real_time\' \n ' \
                      '         INNER JOIN product_template AS pt ON pt.id = pp.product_tmpl_id \n ' \
                      '                                              AND pt.cost_method = \'average\' \n ' \
                      '                                              AND pt.type = \'product\' \n ' \
                      '   WHERE sm.date >=  \'{date_from}\' \n' \
                      '         AND sm.date <= \'{date_to}\' \n ' \
                      '         AND sm.state = \'done\' \n ' \
                      '         AND sm.location_id IN {locations} \n ' \
                      '         AND sm.location_dest_id NOT IN {locations} \n ' \
                      'GROUP BY sm.product_id \n ' \
                      'ORDER BY sm.product_id;'.format(date_from = _date_from + ' 00:00:00',
                                                       date_to = _date_to + ' 23:59:59',
                                                       locations = tuple(_location_ids)).replace(',)', ')')
        cr.execute(_sql_string)
        _products_tup = cr.fetchall()
        for _tup in _products_tup:
            _product_ids.append(_tup[0])

        _digits_obj = self.pool.get('decimal.precision')
        _digits_id = _digits_obj.search(cr, uid, [('name','=','Product Price')])
        if len(_digits_id) > 0:
            _digits['price'] = _digits_obj.browse(cr, uid, _digits_id[0])['digits']
        else:
            _digits['price'] = 2
        
        _digits_id = _digits_obj.search(cr, uid, [('name','=','Account')])
        if len(_digits_id) > 0:
            _digits['account'] = _digits_obj.browse(cr, uid, _digits_id[0])['digits']
        else:
            _digits['account'] = 2

        # preračunam posamezen izdelek
        _warning = {}
        _warning_msgs = False
        _products = self.pool.get('product.product').browse(cr, uid, _product_ids, context)
        for _product in _products:            
            _dates['date_from'] = _date_from + ' 00:00:00'
            _dates['date_to'] = _date_to + ' 23:59:59'

            _cost_price_id = self.pool.get('product.period.cost').search(cr, uid, [('product_id','=',_product.id),('period_id','=',_period_id.id)])
            if len(_cost_price_id) <> 0:
                _cost_price = self.pool.get('product.period.cost').browse(cr, uid, _cost_price_id[0], context)
                _product._set_period_cost(_dates, _digits, _cost_price.price_unit)
            else:
                if not _warning_msgs:
                    _warning_msgs = _('Cost price for selected period does not exist! \n') 
                _warning_msgs += _product.name + '\n '

        if _warning_msgs:
            _warning = {'title': _('Recalculation Error!'), 'message' : _warning_msgs}
        return {'warning': _warning}

    def _do_manual(self, cr, uid, ids, context=None):
        _recalculation_id = self.browse(cr, uid, ids[0], context)

        # najdem ustrezna obdobja
        if not _recalculation_id.period_id:
            raise osv.except_osv(_('Error!'), _('Cannot find suitable dates for recalculation.'))
        
        _date_from = _recalculation_id.period_id.date_start + ' 00:00:00'
        _date_to = _recalculation_id.period_id.date_stop + ' 23:59:59'
        
        # najdem ustrezne podatke
        _moves = []
        _journal_ids, _lines = self._get_valuation_data(cr, uid, _recalculation_id.period_id.id, _date_from, _date_to, _recalculation_id.type)
        
        for _journal_id in _journal_ids:
            _move = {'journal_id': _journal_id,
                     'date': _date_to,
                     'period_id': _recalculation_id.period_id.id,
                     'tax_period_id': _recalculation_id.period_id.id,
                     'ref': _('Stock Expense Move - ' + _recalculation_id.period_id.name),
                     'state': 'draft',
                     'line_id': []}

            _moves.append(_move)

        for _line in _lines:
            for i in range(0, len(_moves)):
                if _moves[i]['journal_id'] == _line['journal_id']:
                    _item_num = i
                    break
            _moves[i]['line_id'].append([0, 0, _line])

        _move_ids = []
        for _move in _moves:
            _move_id = self.pool.get('account.move').create(cr, uid, _move, context)
            if _move_id:
                _move_ids.append(_move_id)

        return _move_ids

    def execute(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        _recalculation_id = self.browse(cr, uid, ids[0], context)
        if _recalculation_id.type == '0':
            if self._do_real_time(cr, uid, ids, context):
                return {'type': 'ir.actions.act_window_close'}
            else:
                return False
        else:
            _move_ids = ",".join(str(_move_id) for _move_id in self._do_manual(cr, uid, ids, context))
            if len(_move_ids) != 0:
                return {'domain': "[('id', 'in', [" + _move_ids + "])]",
                        'name': _('Cost Move(s)'),
                        'view_type': 'form',
                        'view_mode': 'tree,form',
                        'res_model': 'account.move',
                        'type': 'ir.actions.act_window',
                        'context': context}
            else:
                return False
