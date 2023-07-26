odoo.define('pw_pos_salesperson_emp.Orderline', function (require) {
    'use strict';

    const Orderline = require('point_of_sale.Orderline');
    const Registries = require('point_of_sale.Registries');

    const ResetSalesperson = (Orderline) =>
        class extends Orderline {
            removeEmployee() {
                this.props.line.remove_sale_person()
            }
            setEmployee() {
                this.updateSalesperson(this.props.line);
            }
            async updateSalesperson(line) {
                this.showPopup('SalespersonPopup', {
                    title: this.env._t('Select Salesperson'),
                    type: 'line',
                    selectedLine: line
                });
            }
        };

    Registries.Component.extend(Orderline, ResetSalesperson);
    return ResetSalesperson;
});
