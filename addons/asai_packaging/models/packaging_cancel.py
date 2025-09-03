from odoo import models, fields, api


class PackagingCancel(models.TransientModel):
    _name = 'asai.packaging.cancel'
    _description = 'Wizard for Canceling Packaging Order'

    order_id = fields.Many2one('asai.packaging.order', readonly=True)
    cancel_cause = fields.Text('Cause for Cancellation', required=True)

    def action_confirm_cancel(self):
        self.ensure_one()
        self.order_id.write({
            'status':'cancelled',
            'cancel_cause': self.cancel_cause
        })
        return {'type': 'ir.actions.act_window_close'}
    
    def action_cancel(self):
        """Закрывает окно без сохранения"""
        return {'type': 'ir.actions.act_window_close'}