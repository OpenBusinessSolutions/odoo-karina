{ 'sequence': 500,
"name"         : "Partner Participations"
, "version"      : "0.7"
, "author"       : "ChriCar Beteiligungs- und Beratungs- GmbH"
, "website"      : "http://www.chricar.at/ChriCar"
, "description"  : """This module allows to define owners of a partner.
The owner has to be defined in OpenERP as partner.
Currently no check is made if max 100% of the capital is defined here

Contract date+number

legal and fiscal relevant periods

Added Participation tab to partners to show Parent and Participations"""
, "category"     : "Generic Modules/Others"
, "depends"      : ["one2many_sorted"]
, "init_xml"     : []
, "demo"         : ["partner_parent_companies_demo.xml"]
, "data"   :
[ "partner_parent_companies_view.xml"
, "security/ir.model.access.csv"
, "report_participation.xml"
]
, "auto_install" : False
, 'installable': False
, 'application'  : False
}
