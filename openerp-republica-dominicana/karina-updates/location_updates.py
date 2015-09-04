#-*- coding: utf-8 -*-
from openerp.osv import orm, fields


class Location(orm.Model):

    _inherit = 'stock.location'
    _columns = {
        'is_vehicle': fields.boolean('Is Vehicle', help="Mark this box if this location is a moving vehicle."),
        'vehicle_id': fields.many2one('fleet.vehicle', 'Vehicle', delete="on_cascade")
    }

Location()
