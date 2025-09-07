import base64
import csv
from io import StringIO
from odoo import models, fields, api
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class PackagingOrder(models.Model):
    _name = 'asai.packaging.order'
    _description = 'Packaging Order'

    name = fields.Char('Order Number', required=True)
    packer_name = fields.Char('Packer Name')
    status = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Packed'),
        ('cancelled', 'Cancelled')
    ], default='draft', required=True)

    cancel_cause = fields.Text('Cancel Cause') # для текст для причины отмена заказа 

    scan_code = fields.Char(
        "Scan QR Code",
        help="Сканируйте QR-код детали — система автоматически увеличит счётчик"
    )

    detail_ids = fields.One2many(
        'asai.packaging.detail',
        'order_id',
        string='Packaging Detail'
    )

    # Кнопка: Начать упаковку
    def action_start(self):
        self.write({'status': 'in_progress'})

    # Кнопка: Завершить упаковку (только если всё упаковано)
    def action_done(self):
        if self._is_complete():
            self.write({'status': 'done'})
        else:
            raise ValueError("Cannot complete: not all items are packed!")

    # Кнопка: Сбросить
    def action_reset(self):
        self.write({'status': 'draft'})
        self.detail_ids.write({'qty_packed': 0})

    # Кнопка: Отменить заказ
    def action_cancel(self):
        self.write({'status': 'cancelled'})

    # Проверка: все ли детали упакованы?
    @api.depends('detail_ids.qty_packed', 'detail_ids.qty_required')
    def _compute_is_complete(self):
        for order in self:
            order.is_complete = order._is_complete()

    is_complete = fields.Boolean(compute='_compute_is_complete', store=True)

    def _is_complete(self):
        return all(
            line.qty_packed >= line.qty_required
            for line in self.detail_ids
        )
    
    @api.model
    def action_import_csv(self):
        """Вощращает действие для открытия Wizard"""
        return {
            'name': 'Import Production Order from Csv',
            'type': 'ir.actions.act_window',
            'res_model': 'asai.packaging.import',
            'view_mode': 'form',
            'target': 'new',
            'view_id': False,
        }

    def action_open_cancel(self):
        """Открывает Wizard для отмены заказа"""
        self.ensure_one()
        return {
            'name': 'Cancel Packaging Order',
            'type': 'ir.actions.act_window',
            'res_model': 'asai.packaging.cancel',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_order_id': self.id
            }
        }

    def action_scan_code(self):
        """Обработка скана QR Code"""
        self.ensure_one()

        _logger.info("✅ action_scan_code вызван")  # 🔍
        _logger.info("Scan code: %s", self.scan_code)  # 🔍

        _logger.info("Количество detail_ids: %s", len(self.detail_ids))
        _logger.info("Сами детали: %s", self.detail_ids.ids)

        if not self.scan_code:
            _logger.warning("❌ scan_code пустой")  # 🔍
            return
        
        detail = self.detail_ids.filtered(lambda d:d.qr_code == self.scan_code)

        if not detail:
            raise UserError(f'Деталь с QR-кодом {self.scan_code} не найдена')
        
        available_detail = detail.qty_required - detail.qty_packed
        if available_detail <= 0:
            raise UserError(
                f'Нельзя упаковать {detail.qty_scan_add} шт. Осталось только {available_detail}'
            )
         # Проверяем, не превысит ли добавление лимит
        if detail.qty_scan_add > available_detail:
            raise UserError(
                f'Нельзя упаковать {detail.qty_scan_add} шт. '
                f'Максимум — {available_detail} шт.'
        )

        detail.qty_packed += detail.qty_scan_add
        detail.write({'qty_packed': detail.qty_packed})  # явное сохранение
        
        self.scan_code = False

        # Уведомление о упаковке
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Упаковка',
                'message': f"{detail.product_name}: +{detail.qty_scan_add} шт. упаковано.",
                'type': 'success',
                'sticky': False,
            }
        }
        # }, {
        #     'type': 'ir.actions.client',
        #     'tag': 'refresh'
        # }

    
#     def action_csv_load(self):
#         self.ensure_one()
#         if not self.csv_file or not self.csv_filename:
#             raise UserError("Пожалуйста, загрузите CSV-файл.")
        
#         # Проверка расширения файла 
#         if not self.csv_filename.endswith('.csv'):
#             raise UserError("Поддерживаются только CSV-файлы.")
        
#         # Декодируем файл
#         try:
#             details_order = base64.b64decode(self.csv_file).decode('utf-8')
#             file_load = StringIO(details_order)
#             reader = csv.DictReader(file_load)
#         except Exception as e:
#             raise UserError(f"Ошибка чтения CSV-файла {str(e)}")
        

#         lines = []
#         for row in reader:
#             lines.append((0,0, {
#                 "product_name": row.get('product_name', '').strip(),
#                 "dimensions": row.get('dimensions', '').strip(),
#                 "qty_required": float(row.get('qty_required',1)),
#                 "qr_code": row.get('qr_code', '').strip(),
#                 "qty_scan_add": float(row.get('qty_scan_add', 1)),
#         }))
        
        
#         # Очищаем старые строки и добавляем новые
#         self.detail_ids.unlink()
#         self.write({"detail_ids": lines})

#         # Меняем статус 
#         self.status = "in_progress"


#         return {
#             'type': 'ir.actions.client',
#             'tag': 'display_notification',
#             'params': {
#                 'title': 'Success',
#                 'message': f'Imported {len(lines)} items from CSV.', 
#                 'type': 'success',
#                 'sticky': False,                            
#             }
#         },{
#     'type': 'ir.actions.client',
#     'tag': 'refresh'
# }
