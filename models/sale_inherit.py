from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    outstanding_credit = fields.Float(
        string='Outstanding Amount',
        compute='_compute_credit_status',
        help='Total unpaid amount already owed by this customer.',
    )
    credit_status = fields.Selection(
        selection=[
            ('ok', 'Within Limit'),
            ('over', 'Over Limit'),
        ],
        string='Credit Status',
        compute='_compute_credit_status',
    )
    return_count = fields.Integer(
        string='Returns',
        compute='_compute_return_count',
    )

    @api.depends('partner_id', 'partner_id.credit', 'partner_id.credit_limit')
    def _compute_credit_status(self):
        for order in self:
            partner = order.partner_id
            outstanding = partner.credit or 0.0
            limit = partner.credit_limit or 0.0
            order.outstanding_credit = outstanding
            order.credit_status = 'over' if limit and outstanding > limit else 'ok'

    def _compute_return_count(self):
        for order in self:
            order.return_count = self.env['stock.picking'].search_count([
                ('picking_type_id.code', '=', 'incoming'),
                ('partner_id', '=', order.partner_id.id),
                ('origin', 'ilike', order.name),
            ])

    def action_confirm(self):
        for order in self:
            if order.credit_status == 'over':
                raise UserError(_(
                    "Cannot confirm %(order)s: customer %(partner)s is over the "
                    "credit limit. Outstanding: %(outstanding).2f / Limit: %(limit).2f.",
                    order=order.name,
                    partner=order.partner_id.name,
                    outstanding=order.outstanding_credit,
                    limit=order.partner_id.credit_limit,
                ))
        return super().action_confirm()

    def action_view_returns(self):
        self.ensure_one()
        returns = self.env['stock.picking'].search([
            ('picking_type_id.code', '=', 'incoming'),
            ('partner_id', '=', self.partner_id.id),
            ('origin', 'ilike', self.name),
        ])
        return {
            'type': 'ir.actions.act_window',
            'name': _('Returns - %s', self.name),
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', returns.ids)],
            'context': {'default_partner_id': self.partner_id.id},
        }
