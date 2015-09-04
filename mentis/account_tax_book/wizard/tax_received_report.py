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

import base64
import cStringIO
import csv
#import encodings.cp1250

from osv import fields, osv
from tools.translate import _
import time


class tax_received_report(osv.osv_memory):
    def _get_selection(self, cr, uid, context=None):
        
        cr.execute("""
            SELECT DISTINCT AML.period_id, AP.name
            FROM account_move_line AML, account_period AP
            WHERE AML.period_id = AP.id
            ORDER BY AML.period_id
         """)
        
        return [(x[0], x[1]) for x in cr.fetchall()] 
#        return (
#                ('1','First Item'),
#                ('2','Second Item'))
     
    _name = "tax.received.report"
    _description = "Create Report"
    _columns = {
                'start_date': fields.date('Start Date', required=True),
                'end_date': fields.date('End Date', required=True),
                'period': fields.selection(_get_selection, 'Period'),
                'data': fields.binary('File', readonly=True),
                'name': fields.char('Filename', size=32, readonly=True),
                'state': fields.selection([('choose', 'choose'), ('get', 'get')])
                }
    _defaults = {
                 'state': 'choose',
                 'start_date' : lambda *a: time.strftime('%Y-%m-%d'),
                 'end_date' : lambda *a: time.strftime('%Y-%m-%d'),
                }
   
    def create_report(self,cr,uid,ids,context={}):
        this = self.browse(cr, uid, ids)[0]
        period = int(this.period)
        
        buffer = cStringIO.StringIO()
        #writer = csv.writer(buffer, delimiter=';', quoting=csv.QUOTE_NONE, lineterminator='\r\n')
        writer = csv.writer(buffer, delimiter=';', quoting=csv.QUOTE_NONE)
        buffer_row = []

        cr.execute("""
                SELECT
                    min(AML.id) as id,
                    AP.code as period_id,
                    AM.date as date,
                    AM.name as document_name,
                    P.name as partner_name,
                    P.vat as vat,
                    
                    sum(
                    case
                    when ATB.position = '8.a' 
                            then debit
                            else 0
                    end) as col_8a,
                    sum(
                    case
                    when ATB.position = '8.b' 
                            then debit
                            else 0
                    end) as col_8b,
                    sum(
                    case
                    when ATB.position = '9' 
                            then debit
                            else 0
                    end) as col_9,
                    sum(
                    case
                    when ATB.position = '10' 
                            then debit
                            else 0
                    end) as col_10,
                    sum(
                    case
                    when ATB.position = '11' 
                            then debit
                            else 0
                    end) as col_11,
                    sum(
                    case
                    when ATB.position = '12'
                            then debit
                            else 0
                    end) as col_12,
                    sum(
                    case
                    when ATB.position = '13' 
                            then debit
                            else 0
                    end) as col_13,
                    sum(
                    case
                    when ATB.position = '14' 
                            then debit
                            else 0
                    end) as col_14,
                    sum(
                    case
                    when ATB.position = '15'
                            then debit
                            else 0
                    end) as col_15,
                    sum(
                    case
                    when ATB.position = '16'
                            then debit
                            else 0
                    end) as col_16,
                    sum(
                    case
                    when ATB.position = '17'
                            then debit
                            else 0
                    end) as col_17,
                    sum(
                    case
                    when ATB.position = '18'
                            then debit
                            else 0
                    end) as col_18,
                    sum(
                    case
                    when ATB.position = '19'
                            then debit
                            else 0
                    end) as col_19
                FROM 
                        account_move_line AML,
                        account_move AM,
                        account_tax_book_fields_received_tax_code_rel REL,
                        account_tax_book_fields ATB,
                        res_partner P,
                        account_period AP
                WHERE 
                        AML.tax_code_id = REL.tax_code_id and 
                        REL.tax_book_fields_id = ATB.id and 
                        AML.tax_code_id != 0 and
                        AML.partner_id = P.id and
                        AML.move_id = AM.id and
                        AM.tax_period_id = AP.id and
                        AM.tax_period_id = %s
                
                GROUP BY AM.name, AM.date, AP.code, P.name, P.vat
                ORDER BY AM.name
            """ % period)
        
        for rec in cr.fetchall():
            buffer_row = []
            
            period = rec[1].partition('/')[0]
            buffer_row.append(period + period)
            
            buffer_row.append(rec[2])
            buffer_row.append(rec[3])
            buffer_row.append(rec[4])
            buffer_row.append(rec[5])
            buffer_row.append(rec[6]) #vat
            
            tmp_8a = rec[7]
            tmp_8b = rec[8]
            
            buffer_row.append(rec[7])
            buffer_row.append(rec[8])
            buffer_row.append(rec[9])
            buffer_row.append(rec[10])
            buffer_row.append(rec[11])
            buffer_row.append(rec[12])
            buffer_row.append(rec[13])
            buffer_row.append(rec[14])
            buffer_row.append(rec[15])
            buffer_row.append(rec[16])
            buffer_row.append(rec[17])
            buffer_row.append(rec[18])
            
            writer.writerow(buffer_row)
        
        
#        all_ids = self.pool.get('tax.records.received').search(cr, uid, [])
#        for line in self.pool.get('tax.records.received').browse(cr, uid, all_ids):
#            buffer_row = []
#            period = line.period_id.code.partition('/')[0]
#            buffer_row.append(period + period)
#            
#            buffer_row.append(line.date)
#            buffer_row.append(line.document_name)
#            buffer_row.append(line.partner_name)
#            buffer_row.append(line.vat)
#            
#            writer.writerow(buffer_row)
        
        
        out=base64.encodestring(buffer.getvalue())
        buffer.close()
        self.write(cr, uid, ids, {'state':'get',
                                  'data':out,
                                  'name':'tax_records_received.csv'}, context=context)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'tax.received.report',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
       
    
tax_received_report()

