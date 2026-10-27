from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    supplier_approval_status = fields.Selection(
        selection=[
            ('pending', 'Pending Approval'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        string='Supplier Approval Status',
        default='pending',
        copy=False,
        tracking=True,
    )

    supplier_lead_time = fields.Integer(
        string='Supplier Lead Time (Days)',
        help='Expected number of days the supplier takes to deliver products.',
    )
