# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Mentis d.o.o. (<http://www.mentis.si/openerp>).
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

from osv import osv, fields
from tools.sql import drop_view_if_exists
from decimal_precision import decimal_precision as dp
import time

def _default_transaction_type_id(self, cr, uid, context=None):
    tt_obj = self.pool.get('intrastat.transaction.type')
    tt_ids = tt_obj.search(cr, uid, [('code', '=', 11)])
        
    if tt_ids:
        return tt_ids[0]
    else:
        return False

class res_country(osv.osv):
    _name = 'res.country'
    _inherit = 'res.country'
    _columns = {
        'intrastat': fields.boolean('Intrastat member'),
    }
    _defaults = {
        'intrastat': lambda *a: False,
    }

res_country()


class intrastat_code(osv.osv):
    _name = "intrastat.code"
    _description = "Intrastat code"
    _columns = {
        'name': fields.char('Intrastat Code', size=16),
        'description': fields.text('Description'),
    }

intrastat_code()


class product_template(osv.osv):
    _name = "product.template"
    _inherit = "product.template"
    _columns = {
        'intrastat_id': fields.many2one('intrastat.code', 'Intrastat code'),
    }

product_template()

class purchase_order(osv.osv):
    _name = "purchase.order"
    _inherit = "purchase.order"
    _columns = {
        'transaction_type_id': fields.many2one('intrastat.transaction.type', 'Transaction type'),
    }
    _defaults = {
        'transaction_type_id': _default_transaction_type_id,
    }
    
    def _prepare_order_picking(self, cr, uid, order, context=None):
        res = super(purchase_order,self)._prepare_order_picking( cr, uid, order, context)
        res['transaction_type_id'] = order.transaction_type_id.id
        return res
    
    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, context=None):
        res = super(purchase_order, self)._prepare_order_line_move(cr, uid, order, order_line, picking_id)
        res['country_origin_id'] = order_line.country_origin_id.id
        res['customer_id'] = order_line.customer_id.id
        return res

purchase_order()

class purchase_order_line(osv.osv):
    _name = "purchase.order.line"
    _inherit = "purchase.order.line"
    _columns = {
        'country_origin_id': fields.many2one('res.country','Country of origin'),
    }

purchase_order_line()


class stock_picking(osv.osv):
    _name = "stock.picking"
    _inherit = "stock.picking"
    _columns = {
        'transaction_type_id': fields.many2one('intrastat.transaction.type', 'Transaction type'),
    }
    _defaults = {
        'transaction_type_id': _default_transaction_type_id
    }
    
stock_picking()

class stock_move(osv.osv):
    _name = "stock.move"
    _inherit = "stock.move"
    _columns = {
        'country_origin_id': fields.many2one('res.country','Country of origin'),
        'customer_id': fields.many2one('res.partner', 'Customer'),
    }

stock_move()


class intrastat(osv.osv):
    _name = "intrastat"
    _description = "Intrastat report"
    _auto = False
    _columns = {
        'intrastat_id': fields.many2one('intrastat.code', 'Intrastat code', readonly=True),
        'intrastat_name': fields.related('intrastat_id', 'description', type='char', string='Intrastat name'),
        
        'country_supplier': fields.many2one('res.country', 'Country of supplier', readonly=True),
        'country_supplier_code': fields.related('country_supplier', 'code', type='char', string='Country of suppl.code'),
        
        'transaction_type_id': fields.many2one('intrastat.transaction.type', 'Transaction type', readonly=True),
        'transaction_type_code': fields.related('transaction_type_id', 'code', type='char', string='Trans. type'),
        
        'country_origin': fields.many2one('res.country', 'Country of origin', readonly=True),
        'country_origin_code': fields.related('country_origin', 'code', type='char', string='Country of origin'),
        
        'weight': fields.float('Weight', readonly=True),
        'value': fields.float('Value', readonly=True, digits_compute=dp.get_precision('Account')),
        'date': fields.char('Date done',size=64,required=False, readonly=True),
        'month':fields.selection([('01','January'), ('02','February'), ('03','March'), ('04','April'), ('05','May'), ('06','June'),
            ('07','July'), ('08','August'), ('09','September'), ('10','October'), ('11','November'), ('12','December')],'Month',readonly=True),
        'year': fields.char('Year',size=64,required=False, readonly=True),
    }
    def init(self, cr):
        drop_view_if_exists(cr, 'intrastat')
        cr.execute("""
            create or replace view intrastat as (
                select
                    MIN (SM.id) AS id,
                    to_char(SP.date_done, 'YYYY') || '-' || to_char(SP.date_done, 'MM') as date,
                    to_char(SP.date_done, 'MM') as month,
                    to_char(SP.date_done, 'YYYY') as year,
                    SP.transaction_type_id as transaction_type_id,
                    PT.intrastat_id AS intrastat_id,
                    SUM (SM.product_qty * PT.weight_net) AS weight,
                    SUM (SM.product_qty * SM.price_unit) AS value,
                    SM.country_origin_id AS country_origin,
                    PA.country_id AS country_supplier
                from
                    stock_picking SP
                    left join stock_move SM on SM.picking_id=SP.id
                    left join (product_template PT
                        left join product_product PP on (PP.product_tmpl_id = PT.id))
                        on (SM.product_id = PP.id)
                    left join res_partner PA on PA.id = SP.partner_id
                    left join res_country C on C.id = PA.country_id
                where
                    SP.state = 'done' AND PA.country_id != 201 AND SP.type = 'in' AND C.intrastat = true
                group by to_char(SP.date_done, 'YYYY') || '-' || to_char(SP.date_done, 'MM'), to_char(SP.date_done, 'MM'), to_char(SP.date_done, 'YYYY'),
                    SP.transaction_type_id, PT.intrastat_id, SM.country_origin_id, PA.country_id
            )""")

intrastat()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
