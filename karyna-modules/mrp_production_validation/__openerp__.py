#-*- coding: utf-8 -*-
{
    'name': 'Mrp Production Validation',
    'author': 'Open Business Solutions SRL',
    'category': 'production',
    'version': '1.0',
    'description':
    """
    Module that validates the production order and ensures
    that the quantity of the final product is a compatible with
    the packagin measure of the bom list.
    """,
    'depends': ['base', 'mrp'],
    'data': ['mrp_production_view.xml',
    'product_view.xml'],
    'installable': True,
    'auto': False
}