from odoo import models, fields, api

class PackagingDetail(models.Model):
    _name = 'asai.packaging.detail'
    _description = 'Detail in Packaging Order'

    order_id = fields.Many2one('asai.packaging.order', ondelete='cascade', required=True)
    product_name = fields.Char('Product Name', required=True)
    dimensions = fields.Char('Dimensions (mm)')
    qty_required = fields.Integer('Required', required=True)
    qty_packed = fields.Integer('Packed', default=0)

    qty_scan_add = fields.Integer(
        "Count detail for scan",
        default=1,
        required=True,
        help="Сколько деталей считается упакованными при одном сканировании QR-кода"
    )

    qr_code = fields.Char(
        "QR code",
        help="Уникальный или групповой QR-код, который будет сканироваться через ТСД"
    )

    # Кнопка: +1 упаковано
    def action_add_packed(self):
        self.ensure_one()
        if self.qty_packed < self.qty_required:
            self.qty_packed += 1

    # Кнопка: -1 упаковано
    def action_remove_packed(self):
        self.ensure_one()
        if self.qty_packed > 0:
            self.qty_packed -= 1


