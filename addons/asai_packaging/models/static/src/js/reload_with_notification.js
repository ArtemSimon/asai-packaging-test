odoo.define('asai.packaging.ReloadWithNotification',[],function (require) {
    'use strict';

    const { registry } = require('@web/core/registry');
    
    // Регистрируем новый action
    registry.category('actions').add('asai.packaging.reload_with_notification', async (env, action) => {

        const notification = env.services.notification;

        // Показываем уведомление
        notification.add(action.params.message, {
            type: 'success',
            title: 'Success',
        });

        // Ждём 1.5 секунды, чтобы уведомление успело появиться
        await new Promise(resolve => setTimeout(resolve, 1500));

        // Перезагружаем страницу
        window.location.reload();
    });
});