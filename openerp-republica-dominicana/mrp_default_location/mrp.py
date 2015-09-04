# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2012 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info@vauxoo.com
############################################################################
#    Coded by: julio (julio@vauxoo.com)
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

import time
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp.tools import config
import base64
import csv
import cStringIO
import tools
import netsvc
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

class mrp_production(osv.osv):
    _inherit='mrp.production'
    def product_id_change(self, cr, uid, ids, product_id, context=None):
        res = super(mrp_production, self).product_id_change(cr,uid,ids,product_id,context=context)
        if product_id:
            product = self.pool.get('product.product').browse(cr,uid,product_id,context=context)
            res['value'].update({'location_src_id' : product.categ_id and product.categ_id.location_src_id.id or False,
                        'location_dest_id' : product.categ_id and product.categ_id.location_dest_id.id or False})
        else:
            res['value'].update({'location_src_id' : False,
                        'location_dest_id' : False})
        return res
        
mrp_production()

class procurement_order(osv.osv):
  
  _inherit = 'procurement.order'
  def make_mo(self, cr, uid, ids, context=None):
        """ Make Manufacturing(production) order from procurement
        @return: New created Production Orders procurement wise 
        """
        res = {}
        company = self.pool.get('res.users').browse(cr, uid, uid, context).company_id
        production_obj = self.pool.get('mrp.production')
        move_obj = self.pool.get('stock.move')
        wf_service = netsvc.LocalService("workflow")
        procurement_obj = self.pool.get('procurement.order')
        for procurement in procurement_obj.browse(cr, uid, ids, context=context):
            res_id = procurement.move_id.id
            newdate = datetime.strptime(procurement.date_planned, '%Y-%m-%d %H:%M:%S') - relativedelta(days=procurement.product_id.product_tmpl_id.produce_delay or 0.0)
            newdate = newdate - relativedelta(days=company.manufacturing_lead)
            produce_id = production_obj.create(cr, uid, {
                'origin': procurement.origin,
                'product_id': procurement.product_id.id,
                'product_qty': procurement.product_qty,
                'product_uom': procurement.product_uom.id,
                'product_uos_qty': procurement.product_uos and procurement.product_uos_qty or False,
                'product_uos': procurement.product_uos and procurement.product_uos.id or False,
                'location_src_id': procurement.product_id.categ_id and procurement.product_id.categ_id.location_src_id.id or procurement.location_id.id or False,
		'location_dest_id': procurement.product_id.categ_id and procurement.product_id.categ_id.location_dest_id.id or procurement.location_id.id or False,
                'bom_id': procurement.bom_id and procurement.bom_id.id or False,
                'date_planned': newdate.strftime('%Y-%m-%d %H:%M:%S'),
                'move_prod_id': res_id,
                'company_id': procurement.company_id.id,
            })
            res[procurement.id] = produce_id
            self.write(cr, uid, [procurement.id], {'state': 'running'})
            bom_result = production_obj.action_compute(cr, uid,
                    [produce_id], properties=[x.id for x in procurement.property_ids])
            wf_service.trg_validate(uid, 'mrp.production', produce_id, 'button_confirm', cr)
            if res_id:
                move_obj.write(cr, uid, [res_id],
                        {'location_id': procurement.location_id.id})
        return res
procurement_order()
