#-*- coding: utf-8 -*-
{
    'name': 'MRP Sales',
    'author': 'Open Business Solutions SRL',
    'category': 'sales',
    'version': '0.1',
    'description': """
    Add elements for controlling the production and picking process directly from
    the sales order views.
    """,
    'depends': ['base', 'sale', 'mrp', 'stock', 'procurement_jit'],
    'data': ['sale_order_view.xml',
    'mrp_production_view.xml',
    'stock_picking_view.xml'],
    'installable': True,
    'auto': False,
}
