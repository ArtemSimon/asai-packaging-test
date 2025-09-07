// import { rpc } from "@web/core/network/rpc";/

odoo.define('asai_packaging.QRScannerWidget', [], function (require) {
    'use strict';

    const { registry } = require('@web/core/registry');
    const { Component } = owl;
    // const { ormService } = require('@web/core/orm_service');

    const { useService } = require('@web/core/utils/hooks'); 

    class QRScannerWidget extends Component {
        setup() {
            this.inputRef = owl.useRef('input');
            this.orm = useService('orm'); 
        }

        // Вызывается при изменении поля
        async onChange() {
            const value = this.inputRef.el.value;
            if (!value) return;
                    
            console.log("onChange вызван", value); // 🔍
            console.log("Record ID:", this.props.record.data.id); // 🔍
            // Получаем ID текущей записи
            // const recordId = this.props.record.data.id;

            console.log("До update:", this.props.record.data.scan_code);
            this.props.record.update({ scan_code: value });
            console.log("После update:", this.props.record.data.scan_code);
            
            try {
                // Вызываем метод модели через ormService
                const result = await this.orm.call(
                    'asai.packaging.order',   // модель
                    'action_scan_code',       // метод
                    [
                        [this.props.record.data.id],
                        value
                    
                    ],             // args
                    {}                        // kwargs
                );
                console.log("Результат с сервера:", result); // 🔍
            // // Отправляем RPC-запрос на сервер
            // const result = await rpc({
            //     model: 'asai.packaging.order',
            //     method: 'action_scan_code',
            //     args: [],
            //     // args: [this.props.record.data.id],
            //     // kwargs: { scan_code: value },
            // });

            
                // Показываем уведомление
                if (result && result.type === 'ir.actions.client') {
                        this.env.services.notification.add(
                            result.params.message,
                            { type: result.params.type }
                        );
                    }

                    // Обновляем форму
                    // this.props.record.model.root.reload();
                await this.props.record.model.load();

            } catch (error) {
                // Покажем ошибку (например, UserError)
                console.error("Ошибка RPC:", error); // 🔍
                this.env.services.notification.add(
                    error.message,
                    { type: 'danger' }
                );
            }
            // Очищаем поле на клиенте
            this.inputRef.el.value = '';
        }
    }

    QRScannerWidget.template = 'asai_packaging.QRScannerWidget';
    QRScannerWidget.props = ['record', 'field', 'widget'];

    registry.category('fields').add('qr_scanner',{
        component: QRScannerWidget
    });

    return QRScannerWidget; 

});