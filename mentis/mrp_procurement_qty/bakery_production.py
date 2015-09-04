# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Mentis d.o.o.
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
import time
from datetime import datetime, timedelta
from tools.translate import _

class bakery_process(osv.osv):
    _name = "bakery.process"
    _columns = {
        'date_start': fields.datetime('Start Date', readonly=True),
        'date_end': fields.datetime('End Date', readonly=True),
        'duration': fields.char('Duration', size=8, readonly=True),
		'user_id': fields.many2one('res.users', 'User', readonly=True),
		'running': fields.boolean('Running'),
        'misc': fields.char('Misc.', size=128, readonly=True),
		'process': fields.selection([
                                          ('10','Confirm sale orders'),
                                          ('20','Procurement'),
                                          ('30','Procurement with OP'),
                                          ('40','Deliver delivery orders'),
                                          ('50','Produce manufacturing orders'),
                                          ('60','Stock moved')], 'Process', readonly=True),
        'error': fields.text('Error'),
    }
    _defaults = {
        'date_start': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'running': 1,
    }
    _order = 'id desc'
    
    def process_start(self, cr, uid, process, context=None):
        res = self.create(cr, uid,
                          {'user_id': uid,
                           'process':process,
                           })
        return res
    
    def process_end(self, cr, uid, process, process_id, production_id, context=None):
        
        date_start = self.browse(cr, uid, [process_id])[0]['date_start']
        stock_moved = self.pool.get('bakery.production').browse(cr, uid, [production_id])[0]['stock_moved']
        
        d_diff = datetime.now()-datetime.strptime(date_start, ('%Y-%m-%d %H:%M:%S'))
        total_secs = d_diff.seconds
        secs = total_secs % 60
        total_mins = total_secs / 60
        mins = total_mins % 60
        hours = total_mins / 60
        
        d_char = str(hours)+':'
        if mins < 10:
            d_char = d_char + '0'+str(mins)+':'
        else:
            d_char = d_char +str(mins)+':'
        if secs < 10:
            d_char = d_char + '0'+str(secs)
        else:
            d_char = d_char +str(secs)
        
        
        res = self.write(cr, uid, [process_id],
                          {'running': 0,
                           'date_end': time.strftime('%Y-%m-%d %H:%M:%S'),
                           'duration': d_char,
                           })
        if process == '10':
            self.pool.get('bakery.production').write(cr, uid, [production_id], {'sale_done':True, 'procurement_done':False})
        elif process == '20':
            self.pool.get('bakery.production').write(cr, uid, [production_id], {'procurement_done':True})
        elif process == '30':
            self.pool.get('bakery.production').write(cr, uid, [production_id], {'op_procurement_done':True})
        elif process == '40':
            self.pool.get('bakery.production').write(cr, uid, [production_id], {'delivery_done':True})
        elif process == '50':
            self.pool.get('bakery.production').write(cr, uid, [production_id], {'manufactury_done':True,
                                                                                'running':False,
                                                                                'date_end':time.strftime('%Y-%m-%d %H:%M:%S')})
        elif process == '60':
            self.pool.get('bakery.production').write(cr, uid, [production_id], {'stock_moved':not stock_moved})
            
        return {}
    
    def process_running(self, cr, uid, process, context=None):
        res = ''
        if context is None:
            context = {'active_test':False}
            
        running_id = self.search(cr, uid, [('process','=',process)], order='id desc', limit=1, context=context)
        for line in self.browse(cr, uid, running_id):
            if line.running:
                #Preverimo ali je bil tekoci proces zagnan vceraj
                d_start = datetime.strptime(line.date_start, ('%Y-%m-%d %H:%M:%S')).date()
                d_now = datetime.now().date()
                if d_start == d_now:
                    d_date = datetime.strptime(line.date_start, ('%Y-%m-%d %H:%M:%S'))
                    d_date = d_date + timedelta(hours=1)
                
                    res = 'Process started by %s, on %s' %(line.user_id.name, d_date)
        return res
    
    def unlink(self, cr, uid, ids, context=None):
        raise osv.except_osv(_('Error!'), _("You can not remove Process record!"))
    
bakery_process()


class bakery_production(osv.osv):
    _name = "bakery.production"
    _columns = {
        'date_start': fields.datetime('Start Date', readonly=True),
        'date_end': fields.datetime('End Date', readonly=True),
        'running': fields.boolean('Running'),
        'sale_done': fields.boolean('Sale confirmed'),
        'procurement_done': fields.boolean('Procurement done'),
        'op_procurement_done': fields.boolean('OP procurement done'),
        'delivery_done': fields.boolean('Delivery done'),
        'stock_moved': fields.boolean('Stock moved'),
        'manufactury_done': fields.boolean('Manufactury done'),
    }
    _defaults = {
        'date_start': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'running': 1,
    }
    _order = 'id desc'
    
    def production_start(self, cr, uid, context=None):
        res = self.create(cr, uid, {})
        return res
    
    def production_running(self, cr, uid, process, context=None):
        res = ''
        if context is None:
            context = {'active_test':False}
            
        running_id = self.search(cr, uid, [], order='id desc', limit=1, context=context)
        for line in self.browse(cr, uid, running_id):
            if line.running and line.stock_moved and process != '60' and process != '20':
                res = _('Cannot run process. Stocks are moved!')
                
            elif line.running:
                if process == '10'and line.delivery_done:
                    res = _('Cannot confirm Sale orders, since Delivery orders are already delivered!')
                elif process == '20'and line.delivery_done:
                    res = _('Cannot run Scheduler, since Delivery orders are already delivered!')
                elif process == '20'and not line.stock_moved:
                    res = _('Cannot run Schedulers. You must first move the stock and orderpoints!')
                elif process == '30' and not line.procurement_done:
                    res = _('Cannot run Scheduler from Orderpoint, since normal Scheduler has not been run yet!')
                elif process == '40':
                    d_start = datetime.strptime(line.date_start, ('%Y-%m-%d %H:%M:%S')).date()
                    d_now = datetime.now().date()
                    if not d_start < d_now:
                        res = _('Cannot deliver Delivery orders since production start date (%s) is not older than today!') %(d_start)
                elif process == '50'and not line.delivery_done:
                    res = _('Cannot finnish production, since Delivery orders have not been delivered yet!')
                elif process == '60':
                    if not line.sale_done:
                        res = _('Sale not confirmed!')
                    elif line.delivery_done:
                        res = _('Delivery orders are delivered!')
                    
            else:
                running_id = []
                    
        return running_id, res
    
    def is_stock_moved(self, cr, uid, process, context=None):
        res = False
        if context is None:
            context = {'active_test':False}
            
        running_id = self.search(cr, uid, [], order='id desc', limit=1, context=context)
        for line in self.browse(cr, uid, running_id):
            if line.running and line.stock_moved:
                res = True
        return res
    
    def unlink(self, cr, uid, ids, context=None):
        raise osv.except_osv(_('Error!'), _("You can not remove Production record!"))
    
bakery_production()
