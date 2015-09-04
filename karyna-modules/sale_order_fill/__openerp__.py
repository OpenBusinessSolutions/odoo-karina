{
    'name': 'Sale Order Auto Fill',
    'author': 'Open Business Solutions SRL',
    'category': 'Sales',
    'version': '0.1',
    'description':
    """Autogenerate sales order lines based on product categories.
    The generated order lines also add all available salesagents.""",
    'installable': True,
    'data': [
		'wizards/sale_line_fill_view.xml',
		'sale_order_view.xml',
		'order_line_view.xml',
		'salesagent_order_line_view.xml',
		'mrp_view.xml',
		'mrp_bom_view.xml',
		'stock_picking_view.xml'
    ],
    'auto': False,
    'depends': [
		'base',
		'sale',
		'stock',
		'mrp',
		'sale_stock',
		'salesagent_commissions'
    ]
}
