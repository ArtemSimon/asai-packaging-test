from odoo import models, fields, tools
from odoo.tools import sql



class PackerReport(models.Model):
    _name = 'asai.packer.report'
    _decsription = 'packer statistics'
    _auto = False
    _order = 'qty_packed_total desc'

    packer_name = fields.Char(string='Packer Name',readonly=True)
    qty_packed_total = fields.Integer(string='Total Packed',readonly=True)

    def init(self):
        """Создаем SQL view"""

        # Удаляем старую view, если есть
        tools.drop_view_if_exists(self.env.cr, self._table)

        # Создаём новую SQL view
        self.env.cr.execute("""
            CREATE VIEW %s AS (
                SELECT
                    ROW_NUMBER() OVER () AS id,
                    COALESCE(po.packer_name, 'Unknown') AS packer_name,
                    SUM(pol.qty_packed) AS qty_packed_total
                FROM asai_packaging_detail pol
                JOIN asai_packaging_order po ON pol.order_id = po.id
                WHERE po.status = 'done'  
                GROUP BY po.packer_name
            )
        """ % self._table)