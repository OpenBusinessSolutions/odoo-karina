##############################################################################
#
# Copyright (c) 2009 Albert Cervera i Areny <albert@nan-tic.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
import pooler


class JasperDataParser(object):
    def __init__(self, cr, uid, ids, data, context):
        if not context: 
            context = {}
        self.cr = cr
        self.uid = uid
        self.ids = ids
        self.data = data
        self.context = context
        self.pool = pooler.get_pool(cr.dbname)

#        self.localcontext = {
#            'user': user,
#            'company': user.company_id,
#            'repeatIn': self.repeatIn,
#            'setLang': self.setLang,
#            'setTag': self.setTag,
#            'removeParentNode': self.removeParentNode,
#            'format': self.format,
#            'formatLang': self.formatLang,
#            'logo' : user.company_id.logo,
#            'lang' : user.company_id.partner_id.lang,
#            'translate' : self._translate,
#            'setHtmlImage' : self.set_html_image
#        }

    def get(self, parameter, default_value):
        if parameter == 'ids':
            return hasattr(self, 'generate_ids') and \
                self.generate_ids(self.cr, self.uid, self.ids, self.data, self.context) or default_value
        elif parameter == 'name':
            return hasattr(self, 'generate_name') and \
                 self.generate_name(self.cr, self.uid, self.ids, self.data, self.context) or default_value
        elif parameter == 'model':
            return hasattr(self, 'generate_model') and \
                 self.generate_model(self.cr, self.uid, self.ids, self.data, self.context) or default_value
        elif parameter == 'records':
            return hasattr(self, 'generate_records') and \
                 self.generate_records(self.cr, self.uid, self.ids, self.data, self.context) or default_value
        elif parameter == 'data_source':
            return hasattr(self, 'generate_data_source') and \
                self.generate_data_source(self.cr, self.uid, self.ids, self.data, self.context) or default_value
        elif parameter == 'parameters':
            return hasattr(self, 'generate_parameters') and \
                self.generate_parameters(self.cr, self.uid, self.ids, self.data, self.context) or default_value
        elif parameter == 'properties':
            return hasattr(self, 'generate_properties') and \
                self.generate_properties(self.cr, self.uid, self.ids, self.data, self.context) or default_value
        else:
            return default_value

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
