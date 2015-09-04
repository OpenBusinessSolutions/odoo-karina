# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2012-2012 ChriCar Beteiligungs- und Beratungs- GmbH (<http://www.camptocamp.at>)
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

# FIXME remove logger lines or change to debug
 
from openerp.osv import fields, osv
from openerp import netsvc
from openerp.tools.translate import _
import time
import logging


class sale_order(osv.osv):
    _inherit = 'sale.order'

#    def _auto_init(self, cr, context=None):
#           cr.execute("""update wkf_instance
#                         set state = 'active'
#                       where state = 'complete'
#                         and res_type = 'sale.order'
#""")


    def allow_reopen(self, cr, uid, ids, context=None):
        _logger = logging.getLogger(__name__)

        _logger.debug('FGF sale_order reopen %s' % (ids))
        stock_picking_obj = self.pool.get('stock.picking')
        account_invoice_obj = self.pool.get('account.invoice')
        for order in self.browse(cr, uid, ids, context):
            if order.picking_ids:
                for pick in order.picking_ids:
                    stock_picking_obj.allow_reopen(cr, uid, [pick.id])
                    
                    #if pick.state not in ['draft','cancel','confirmed']: # very restrictive
                    #    raise osv.except_osv(_('Error'), _('You cannot reset this Sale Order to draft, because picking [ %s %s ] is not in state draft or cancel ')% (pick.name, pick.state))

            if order.invoice_ids:
                for inv in order.invoice_ids:
                    account_invoice_obj.action_reopen(cr, uid, [inv.id])
                #for inv in order.picking_ids:
                #    if inv.state not in ['draft','cancel']: # very restrictive
                #        raise osv.except_osv(_('Error'), _('You cannot reset this Sale Order to draft, because invoice %s %s is not in state draft or cancel ')% (inv.name, inv.state))

        return True

    

    def action_reopen(self, cr, uid, ids, context=None):
        """ Changes SO from to draft.
        @return: True
        """
        _logger = logging.getLogger(__name__)

        _logger.debug('FGF sale_order action reopen %s' % (ids))
        self.allow_reopen(cr, uid, ids, context=None)
        account_invoice_obj = self.pool.get('account.invoice')
        stock_picking_obj = self.pool.get('stock.picking')
        stock_move_obj = self.pool.get('stock.move')
        report_xml_obj = self.pool.get('ir.actions.report.xml')
        attachment_obj = self.pool.get('ir.attachment')
        order_line_obj = self.pool.get('sale.order.line')

        now = ' ' + _('Invalid') + time.strftime(' [%Y%m%d %H%M%S]')
        for order in self.browse(cr, uid, ids):
            if order.invoice_ids:
                for inv in order.invoice_ids:
                    account_invoice_obj.action_reopen(cr, uid, [inv.id])
                    if inv.journal_id.update_posted: 
                        _logger.debug('FGF sale_order reopen cancel invoice %s' % (ids))
                        account_invoice_obj.action_cancel(cr, uid, [inv.id])
                    else:
                        _logger.debug('FGF sale_order reopen cancel 2 invoice %s' % (ids))
                        account_invoice_obj.write(cr, uid, [inv.id], {'state':'cancel', 'move_id':False})

            if order.picking_ids:
                for pick in order.picking_ids:
                    stock_picking_obj.action_reopen(cr, uid, [pick.id])
                    stock_picking_obj.write(cr, uid, [pick.id], {'state':'cancel'})
                    if pick.move_lines:
                        move_ids = []
                        for m in pick.move_lines:
                            move_ids.append(m.id)
                        stock_move_obj.write(cr, uid, move_ids, {'state':'cancel'})
                    #stock_picking_obj.action_cancel(cr, uid, [pick.id])
                     
            # for some reason datas_fname has .pdf.pdf extension
            report_ids = report_xml_obj.search(cr, uid, [('model','=', 'sale.order'), ('attachment','!=', False)])
            for report in report_xml_obj.browse(cr, uid, report_ids):
                if report.attachment:
                    aname = report.attachment.replace('object','order')
                    if eval(aname):
                        
                        aname = eval(aname)+'.pdf'
                        attachment_ids = attachment_obj.search(cr, uid, [('res_model','=','sale.order'),('datas_fname', '=', aname),('res_id','=',order.id)])
                        for a in attachment_obj.browse(cr, uid, attachment_ids):
                            vals = {
                                'name': a.name.replace('.pdf', now+'.pdf'),
                                'datas_fname': a.datas_fname.replace('.pdf.pdf', now+'.pdf.pdf')
                                   }
                            attachment_obj.write(cr, uid, a.id, vals)

            self.write(cr, uid, order.id, {'state':'draft'})
            line_ids = []
            for line in order.order_line:
                line_ids.append(line.id)
            order_line_obj.write(cr, uid, line_ids, {'state':'draft', 'invoiced': False})

            wf_service = netsvc.LocalService("workflow")

            _logger.debug('FGF sale_order trg del %s' % (order.id))
            wf_service.trg_delete(uid, 'sale.order', order.id, cr)
            _logger.debug('FGF sale_order trg create %s' % (order.id))
            wf_service.trg_create(uid, 'sale.order', order.id, cr)

            #self.log_sale(cr, uid, ids, context=context)  
            
        return True


#    def button_reopen(self, cr, uid, ids, context=None):
#        _logger = logging.getLogger(__name__)   
#        self.allow_reopen(cr, uid, ids, context)
#        _logger.debug('FGF picking allow open  '   )
#        self.write(cr, uid, ids, {'state':'draft'})
#        _logger.debug('FGF picking draft  '   )
#        self.log_picking(cr, uid, ids, context=context)
#        _logger.debug('FGF picking log'   )

        
    
sale_order()
    


