odoo.define('pw_pos_salesperson_emp.SalespersonPopup', function(require){
    'use strict';

    const Popup = require('point_of_sale.ConfirmPopup');
    const Registries = require('point_of_sale.Registries');
    const PosComponent = require('point_of_sale.PosComponent');
    var core = require('web.core');
    var _t = core._t;

    class SalespersonPopup extends Popup {
        constructor() {
            super(...arguments);
            var selectedEmp = false;
        }
        async onChangeSalesperson() {
            var self = this;
            var empid = $("#empID").val();
            var emp_id;
            $('#emp_list > option').each(function(){
                if($(this).attr("value") == empid ){
                   emp_id = $(this).attr("id");
                }
            });
            if (emp_id) {
                this.selectedEmp = this.env.pos.employee_by_id[emp_id];
            }
        }
        async confirm() {
            var self = this;
            var empid = $("#empID").val();
            if (self.selectedEmp) {
                self.env.posbus.trigger('close-popup', {popupId: self.props.id });
                var order = self.env.pos.get_order();
                var orderlines = order.get_orderlines();
                if (self.props.type == 'order') {
                    for(var i = 0; i < orderlines.length; i++){
                        if(orderlines[i] != undefined){
                            orderlines[i].set_line_user(self.selectedEmp);
                        }
                    }
                }
                if (self.props.type == 'line' && self.props.selectedLine) {
                    self.props.selectedLine.set_line_user(self.selectedEmp);
                }
                self.env.posbus.trigger('close-popup', {
                    popupId: self.props.id
                });
            }
        }
    };
    
    SalespersonPopup.template = 'SalespersonPopup';

    Registries.Component.add(SalespersonPopup);

    return SalespersonPopup;

});
