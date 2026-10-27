from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _reset_parent_purchase_approval(self):
        orders = self.mapped('order_id')

        for order in orders:
            if order.state not in ('draft', 'sent'):
                continue

            status = (
                'pending'
                if order.approval_required
                else 'not_required'
            )

            order.with_context(
                purchase_approval_action='reset'
            ).write({
                'manager_approved': False,
                'approval_status': status,
            })

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)

        commercial_fields = {
            'product_id',
            'product_qty',
            'price_unit',
            'taxes_id',
            'discount',
        }

        if any(
            commercial_fields.intersection(vals)
            for vals in vals_list
        ):
            lines._reset_parent_purchase_approval()

        return lines

    def write(self, vals):
        result = super().write(vals)

        commercial_fields = {
            'product_id',
            'product_qty',
            'price_unit',
            'taxes_id',
            'discount',
        }

        if commercial_fields.intersection(vals):
            self._reset_parent_purchase_approval()

        return result

    def unlink(self):
        orders = self.mapped('order_id')
        result = super().unlink()

        for order in orders:
            if order.state not in ('draft', 'sent'):
                continue

            status = (
                'pending'
                if order.approval_required
                else 'not_required'
            )

            order.with_context(
                purchase_approval_action='reset'
            ).write({
                'manager_approved': False,
                'approval_status': status,
            })

        return result