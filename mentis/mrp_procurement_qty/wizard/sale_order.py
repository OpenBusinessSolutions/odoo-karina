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
from openerp import netsvc
import time
import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools.safe_eval import safe_eval
from openerp import pooler

class sale_order_confirm_wizard(osv.osv_memory):
    _name = "sale.order.confirm.wizard"
    _description = "Batch Sales Order confirmation"
    
    def _get_status(self, cr, uid, context):
        return self.pool.get('bakery.process').process_running(cr, uid, '10', context=None)
    
    _columns = {
        'date': fields.date('Quotation date'),
        'date_label': fields.date('Datum ponudbe'),
        'status': fields.char('Status', size=128, readonly=True),
        'override': fields.boolean('Override running process', help='Run the process, even if there is another one running'),
    }
    _defaults = {
        'date': lambda *a: (datetime.date.today() + datetime.timedelta(1)).strftime('%Y-%m-%d'),
        'date_label': lambda *a: (datetime.date.today() + datetime.timedelta(1)).strftime('%Y-%m-%d'),
        'status': _get_status,
    }
        
    def execute(self, cr, uid, ids, context=None):

        if context is None:
            context = {}
        
        confirmation_date = self.browse(cr,uid,ids)[0].date
        sale_override = self.browse(cr,uid,ids)[0].override
        sale_order_obj = self.pool.get('sale.order')
            
        #1. Preverimo ali je ura med enajsto zvecer in sesto zjutraj
        dateTime = datetime.datetime.now()
        if (dateTime.hour in range (22,24) or dateTime.hour in range (0,4)):
        #if (dateTime.hour in range (22,24)):
            raise osv.except_osv('Opozorilo!', u'Potrjevanje naročil ni možno med enajsto uro zvečer in šesto zjutraj!')
        
        
        #2. Preverimo ali je bila proizvodnja ze lansirana in ce je ali je bila istega dne
#        proc_jour_obj = self.pool.get('procurement.order.journal')
#        proc_jour_ids = proc_jour_obj.search(cr, uid, [('state', '=' , True)])
#        
#        if proc_jour_ids: 
#            for proc_jour_line in proc_jour_obj.browse(cr, uid, proc_jour_ids):
#                if (proc_jour_line.date_start != time.strftime('%Y-%m-%d')):
#                    raise osv.except_osv('Opozorilo!', u'Proizvodnja je že bila lansirana dne: %s.' % (proc_jour_line.date_start,))
        
        
        #3. Preverimo ali kaksna ponudba za izbrani datum ni v statusu priprave (v statusu draft ali sent je napaka)
        sale_order_ids = sale_order_obj.search(cr, uid, [('state', 'in', ['draft', 'sent']),
                                                         ('date_order', '=', confirmation_date),
                                                         ('shop_id.warehouse_id.lot_stock_id','=',12)], order='id', limit=1)

        for sale_line in sale_order_obj.browse(cr, uid, sale_order_ids):
            raise osv.except_osv(_('Napaka!'),  _('Prodajni nalog %s ni v statusu Pripravljeno!') % sale_line.name)
        
        
        #4. Preverimo status produkcije in ali je ze kdo zagnal ta proces in se ni zakljucen ---------------------------------
        production_id, production_status = self.pool.get('bakery.production').production_running(cr, uid, '10')
        if production_status: #obstaja, pa ne smemo ponovno potrditi SO
            raise osv.except_osv(_('Warning!'),production_status)
        if production_id == []: #se ne obstaja aktiven zapis
            production_id = self.pool.get('bakery.production').production_start(cr, uid)
        else:
            production_id = production_id[0]
        
        process_status = self.pool.get('bakery.process').process_running(cr, uid, '10')
        if not sale_override and process_status:
            raise osv.except_osv(_('Warning!'),process_status)
        else:
            process_id = self.pool.get('bakery.process').process_start(cr, uid, '10')
        cr.commit()
        
        #5. Ustvarimo nov kurzor za zapis statusa v bazo ---------------------------------------------------------------------
        new_cr = pooler.get_db(cr.dbname).cursor()
        
        #6. Potrdimo samo naloge za danasnji dan s statusom "prepared"
        sale_order_ids = sale_order_obj.search(cr, uid, [('state', '=', 'prepared'),
                                                         ('date_order', '=', confirmation_date)], order='id')
        
        err_count = 0
        wf_service = netsvc.LocalService('workflow')
        for sale_order_id in sale_order_ids:
            try:
                wf_service.trg_validate(uid, 'sale.order', sale_order_id, 'order_confirm', new_cr)
                new_cr.commit()
            except Exception:
                new_cr.rollback()
                err_count = err_count + 1
            
        try:
            stock_move_obj = self.pool.get('stock.move')
            stock_move_obj.get_qty_delivery_available(new_cr, uid)
            new_cr.commit()
        except Exception:
            new_cr.rollback()
            err_count = err_count + 1
        finally:
            new_cr.close()
        
        if err_count > 0:
            raise osv.except_osv('Opozorilo!', u'S potrjevanjem poskusite ponovno. Neuspelo potrjenih ponudb: %s' %(str(err_count)))
        
        self.pool.get('bakery.process').process_end(cr, uid, '10', process_id, production_id)
        return {
                'type': 'ir.actions.act_window_close',
        }
    
sale_order_confirm_wizard()

