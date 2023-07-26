odoo.define('pw_pos_salesperson_emp.SalespersonButton', function(require) {
    'use strict';

    const PosComponent = require('point_of_sale.PosComponent');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const { useListener } = require("@web/core/utils/hooks");
    const Registries = require('point_of_sale.Registries');

    class SalespersonButton extends PosComponent {
        setup() {
           super.setup();
           useListener('click', this.onClick);
        }
        async onClick() {
            this.showPopup('SalespersonPopup', {
                title: this.env._t('Select Salesperson'),
                type: 'order',
            });
        }
    }
    SalespersonButton.template = 'SalespersonButton';
    ProductScreen.addControlButton({
        component: SalespersonButton,
        condition: function() {
            return this.env.pos.config.allow_salesperson;;
        },
    });
    Registries.Component.add(SalespersonButton);
    return SalespersonButton;
});
