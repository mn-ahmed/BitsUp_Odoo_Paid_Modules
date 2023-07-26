/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */
odoo.define('pos_invoice_print_without_download.model', function (require) {
    'use strict';

    var  PaymentScreen = require('point_of_sale.PaymentScreen');
    var  Registries = require('point_of_sale.Registries');
  
    var NewPaymentScreen = (PaymentScreen) => 
    class NewPaymentScreen extends PaymentScreen {

        async _finalizeValidation() {
            console.log("insiddee--_finalizeValidation--")
            if ((this.currentOrder.is_paid_with_cash() || this.currentOrder.get_change()) && this.env.pos.config.iface_cashdrawer) {
                this.env.proxy.printer.open_cashbox();
            }
            this.currentOrder.initialize_validation_date();
            this.currentOrder.finalized = true;
            let syncOrderResult, hasError;
            try {
                syncOrderResult = await this.env.pos.push_single_order(this.currentOrder);
                this.currentOrder.invoice_id = syncOrderResult[0].account_move;
                if (this.currentOrder.is_to_invoice() && !this.env.pos.config.invoice_print) {
                    if (syncOrderResult.length) {
                        await this.env.legacyActionManager.do_action('account.account_invoices', {
                            additional_context: {
                                active_ids: [syncOrderResult[0].account_move],
                            },
                        });
                    } else {
                        throw { code: 401, message: 'Backend Invoice', data: { order: this.currentOrder } };
                    }
                }
                if (syncOrderResult.length && this.currentOrder.wait_for_push_order()) {
                    const postPushResult = await this._postPushOrderResolve(
                        this.currentOrder,
                        syncOrderResult.map((res) => res.id)
                    );
                    if (!postPushResult) {
                        this.showPopup('ErrorPopup', {
                            title: this.env._t('Error: no internet connection.'),
                            body: this.env._t('Some, if not all, post-processing after syncing order failed.'),
                        });
                    }
                }
            } catch (error) {
                hasError = true;
                if (error.code == 700)
                    this.error = true;

                if ('code' in error) {
                    await this._handlePushOrderError(error);
                } else {
                    if (isConnectionError(error)) {
                        this.showPopup('OfflineErrorPopup', {
                            title: this.env._t('Connection Error'),
                            body: this.env._t('Order is not synced. Check your internet connection'),
                        });
                    } else {
                        throw error;
                    }
                }
            } finally {
                this.showScreen(this.nextScreen);
                if (!hasError && syncOrderResult && this.env.pos.db.get_orders().length) {
                    const { confirmed } = await this.showPopup('ConfirmPopup', {
                        title: this.env._t('Remaining unsynced orders'),
                        body: this.env._t(
                            'There are unsynced orders. Do you want to sync these orders?'
                        ),
                    });

                    if (confirmed) {
                        this.env.pos.push_orders();
                    }
                }
            }
        }
    }

    Registries.Component.extend(PaymentScreen,NewPaymentScreen);
});
