from odoo import models, fields, api, _
from odoo.exceptions import UserError
import csv
from io import StringIO
import base64


class PackagingImport(models.TransientModel):
    _name = 'asai.packaging.import.wizard'
    _description = 'Import Packaging Orders'


    csv_file = fields.Binary(string='Csv file',required=True)
    csv_filename = fields.Char(string='Filename')

    def action_import(self):
        """Обработка  Csv + создание/обновление заказов"""

        if not self.csv_file or not self.csv_filename:
            raise UserError("Пожалуйста, загрузите CSV-файл.")
        
        # Проверка расширения файла 
        if not self.csv_filename.endswith('.csv'):
            raise UserError("Поддерживаются только CSV-файлы.")
        
        # Декодируем файл
        try:
            details_order = base64.b64decode(self.csv_file).decode('utf-8')
            file_load = StringIO(details_order)
            reader = csv.DictReader(file_load)
        except Exception as e:
            raise UserError(f"Ошибка чтения CSV-файла {str(e)}")
        
        orders_data = {}
        for row in reader:
            order_num = row.get('order_number')
            if not order_num: 
                continue

            if order_num not in orders_data:
                orders_data[order_num] = []


            orders_data[order_num].append({
                'product_name': row.get('product_name', '').strip(),
                'dimensions': row.get('dimensions', '').strip(),
                'qty_required': float(row.get('qty_required', 1)),
                'qr_code': row.get('qr_code', '').strip(),
                'qty_scan_add': float(row.get('qty_scan_add', 1)),
            })

        created_count = 0
        updated_count = 0
        unchanged_count = 0  

        for order_num, lines in orders_data.items():
            order = self.env['asai.packaging.order'].search([('name', '=', order_num)], limit=1)

            # Формируем новые данные для сравнения
            new_lines_data = sorted([
                (line['product_name'], line['dimensions'], line['qty_required'], line['qr_code'], line['qty_scan_add'])
                for line in lines
            ])

            if order:
                # Получаем старые данные
                old_lines_data = sorted([
                    (line.product_name or '', line.dimensions or '', line.qty_required, line.qr_code or '', line.qty_scan_add)
                    for line in order.detail_ids
                ])

                # Сравниваем
                if old_lines_data == new_lines_data:
                    unchanged_count += 1
                    continue  # Пропускаем

                # Если отличаются — обновляем
                line_commands = [(5, 0, 0)] + [(0, 0, line) for line in lines]
                order.write({
                    'detail_ids': line_commands,
                    'status': 'in_progress',
                })
                updated_count += 1

            else:
                self.env['asai.packaging.order'].create({
                    'name': order_num,
                    'status': 'in_progress',
                    'detail_ids': [(0, 0, line) for line in lines]
                })
                created_count += 1

        # Итоговое сообщение
        message_parts = []
        if created_count:
            message_parts.append(f"{created_count} new")
        if updated_count:
            message_parts.append(f"{updated_count} updated")
        if unchanged_count:
            message_parts.append(f"{unchanged_count} unchanged")

        message = ", ".join(message_parts) if message_parts else "No changes"

        return {
            'type': 'ir.actions.client',
            'tag': 'asai.packaging.reload_with_notification',
            'params': {
                'message': f'Imported: {message}'
            }
        }