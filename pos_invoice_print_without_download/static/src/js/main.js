/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_invoice_print_without_download.main', function (require) {
    'use strict';

    var  Registries = require('point_of_sale.Registries');
    var  ReceiptScreen = require('point_of_sale.ReceiptScreen');

    var NewReceiptScreen = (ReceiptScreen) => 
        class NewReceiptScreen extends ReceiptScreen 
        {
            constructor() 
            {
                super(...arguments);
            }
            printInvoicePdf()
            { 
                var self =this;
                const order = this.env.pos.get_order();
                this.rpc({
                    model: 'pos.order',
                    method: 'action_invoice_pdf',
                    args: [[],order.invoice_id],
                }).then(function(base){
                    printJS({printable:base, type:'pdf',base64:true})
                }).catch(function(error){
                    self.showPopup('ErrorPopup', {
                        title:'Connection Error',
                        body: 
                            'Please check connection and try again.'
                        ,
                    });
                });        
            }
        }
    Registries.Component.extend(ReceiptScreen,NewReceiptScreen);
});
