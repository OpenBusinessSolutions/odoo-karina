import time
import os
import platform
from openerp.report import report_sxw


class ReportWebkitVariationGroup(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(ReportWebkitVariationGroup, self).__init__(
            cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr': cr,
            'uid': uid,
            'os': os,
            'platform': platform,
            'this_self': self,
            'this_context': context
        })

report_sxw.report_sxw('report.webkitmrp.production_variation_group',
                      'mrp.production',
                      'addons/mrp_report_webkit_wizard/report/report_webkit_variation_group.mako',
                      parser=ReportWebkitVariationGroup)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
