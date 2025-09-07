from odoo import models, fields, tools


class CancelledReport(models.Model):
    _name = 'asai.cancelled.report'
    _description = 'Cancelled Orders Report'
    _auto = False
    _order = 'order_number_sort'


    order_name = fields.Char(string='Order Number', readonly=True)
    order_number_sort = fields.Integer("Sort Key", readonly=True) 
    packer_name = fields.Char(string='Packer', readonly=True)
    cancel_cause = fields.Text(string='Cancel Cause',readonly=True)
    product_name = fields.Char(string='Product', readonly=True)
    dimensions = fields.Char(string='Dimensions',readonly=True)
    qty_required = fields.Integer(string='Required detail', readonly=True)
    qty_packed = fields.Integer(string='Packed detail',readonly=True)
    qty_missing = fields.Integer(string='Missing detail',readonly=True)

    def init(self):
        """Создаем SQL view"""

        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE VIEW %s AS (
                SELECT
                    ROW_NUMBER() OVER () AS id,
                    po.name AS order_name,
                    COALESCE(NULLIF(po.name, '')::INTEGER, 0) AS order_number_sort,
                    po.packer_name,
                    po.cancel_cause,
                    d.product_name,
                    d.dimensions,
                    d.qty_required,
                    d.qty_packed,
                    (d.qty_required - d.qty_packed) AS qty_missing
                FROM asai_packaging_order po
                JOIN asai_packaging_detail d ON d.order_id = po.id
                WHERE po.status = 'cancelled'
                    AND d.qty_packed < d.qty_required
            )
        """ % self._table)