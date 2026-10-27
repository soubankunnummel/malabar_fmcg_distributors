from odoo import api, fields, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    approval_required = fields.Boolean(
        string='Manager Approval Required',
        compute='_compute_approval_required',
        store=True,
    )

    manager_approved = fields.Boolean(
        string='Manager Approved',
        default=False,
        copy=False,
        readonly=True,
    )

    approval_status = fields.Selection(
        selection=[
            ('not_required', 'Not Required'),
            ('pending', 'Pending Approval'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        string='Approval Status',
        default='not_required',
        copy=False,
        tracking=True,
        readonly=True,
    )

    @api.depends(
        'amount_total',
        'currency_id',
        'company_id',
        'date_order',
    )
    def _compute_approval_required(self):
        for order in self:
            company_currency = order.company_id.currency_id

            if order.currency_id and company_currency:
                order_amount = order.currency_id._convert(
                    order.amount_total,
                    company_currency,
                    order.company_id,
                    order.date_order.date()
                    if order.date_order
                    else fields.Date.today(),
                )
                order.approval_required = order_amount >= 10000
            else:
                order.approval_required = False
                
    @api.onchange(
        'amount_total',
        'currency_id',
        'company_id',
        'date_order',
    )
    def _onchange_approval_required(self):
        for order in self:
            if order.approval_required:
                if order.approval_status != 'approved':
                    order.approval_status = 'pending'
            else:
                order.approval_status = 'not_required'
                order.manager_approved = False

    def _check_purchase_approval_manager(self):
        if not self.env.user.has_group(
            'malabar_fmcg_distributors.group_purchase_manager_approval'
        ):
            raise UserError(
                "Only Purchase Approval Managers can approve "
                "or reject purchase orders."
            )

    def write(self, vals):
        protected_fields = {
            'approval_status',
            'manager_approved',
        }

        # Prevent ordinary writes from changing approval fields.
        # Only trusted server-side code using sudo() can do so.
        if (
            protected_fields.intersection(vals)
            and not self.env.su
        ):
            raise UserError(
                "Approval fields can only be changed through "
                "authorized purchase approval operations."
            )

        approval_affecting_fields = {
            'partner_id',
            'order_line',
            'currency_id',
            'company_id',
            'date_order',
        }

        reset_approval = bool(
            approval_affecting_fields.intersection(vals)
        )

        result = super().write(vals)

        # Changes to important purchase details invalidate
        # previous approval for draft RFQs.
        if reset_approval:
            for order in self:
                if order.state not in ('draft', 'sent'):
                    continue

                new_status = (
                    'pending'
                    if order.approval_required
                    else 'not_required'
                )

                order.sudo().write({
                    'manager_approved': False,
                    'approval_status': new_status,
                })

        return result
    
    def action_approve_purchase(self):
        self._check_purchase_approval_manager()

        for order in self:
            if order.state not in ('draft', 'sent'):
                raise UserError(
                    "Only RFQs can be approved through this workflow."
                )

            if not order.approval_required:
                raise UserError(
                    "Manager approval is not required for this order."
                )

            if order.partner_id.supplier_approval_status != 'approved':
                raise UserError(
                    "Approve the supplier before approving this order."
                )

            order.sudo().write({
                'approval_status': 'approved',
                'manager_approved': True,
            })

        return True

    def action_reject_purchase(self):
        self._check_purchase_approval_manager()

        for order in self:
            if order.state not in ('draft', 'sent'):
                raise UserError(
                    "Only RFQs can be rejected through this workflow."
                )

            if not order.approval_required:
                raise UserError(
                    "Manager approval is not required for this order."
                )

            order.sudo().write({
                'approval_status': 'rejected',
                'manager_approved': False,
            })
        return True

    def button_confirm(self):
        for order in self:
                # The supplier must be approved first.
                if order.partner_id.supplier_approval_status != 'approved':
                    raise UserError(
                        "You cannot confirm this purchase order because "
                        "the supplier has not been approved."
                )

                 # High-value purchases require manager approval.
                if order.approval_required:
                    if order.approval_status != 'approved':
                         raise UserError(
                            "Manager approval is required for purchase "
                            "orders of ₹10,000 or more."
                        )

                if not order.manager_approved:
                    raise UserError(
                        "This purchase order has not been approved "
                        "by a manager."
                    )

        return super().button_confirm()