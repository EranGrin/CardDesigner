odoo.define('gift_card_design_double_side_printer.action', function(require) {
    'use strict';

    var WebActionManager = require('web.ActionManager');
    var WebModel = require("web.Model");

    WebActionManager.include({
        ir_actions_multi_nonbulk: function(action, options) { 
            var self = this;
            var model = new WebModel(action.res_model);
            if (action.printer_config_dict.keypair) {
                // set the certificate used for privileged calls
                qz.security.setCertificatePromise(function(resolve, reject) {
                    if (action.printer_config_dict.keypair.keys) {
                        // use supplied certificate
                        resolve(action.printer_config_dict.keypair.keys);
                    }
                });

                // set the signing function for privileged calls
                qz.security.setSignaturePromise(function(toSign) {
                    //LOG: Authorizing
                    return function(resolve, reject) {
                        // POST to the signing route. CSRF token is passed automatically by Odoo's ajax.post()
                        resolve();
                    }
                });
            }

            if (qz.websocket.isActive()) {
                var config = qz.configs.create(
                    action.printer_name, action.printer_option
                );
                var chain = [];
                for(var i = 0; i <= action.print_data_len; i++) {
                    (function(i_) {
                        //setup this chain link
                        var link = function() {
                            return qz.printers.find(action.printer_name).then(function(found) {
                                return qz.print(qz.configs.create(found, action.printer_option), action.print_data[i_]);
                            });
                        };

                        chain.push(link);
                    })(i);
                }
                //can be .connect or `Promise.resolve()`, etc
                var firstLink = new RSVP.Promise(function(r, e) { r(); });

                var lastLink = null;
                chain.reduce(function(sequence, link) {
                    lastLink = sequence.then(link);
                    return lastLink;
                }, firstLink);

                //this will be the very last link in the chain
                lastLink.catch(function(error) {
                    var res_action = {
                        type: 'ir.actions.act_window',
                        res_model: 'card.print.error.wizard',
                        view_mode: 'form',
                        view_type: 'form',
                        views: [[false, 'form']],
                        target: 'new',
                        context: {
                            'default_name': error.toString(),
                        },
                    }
                    return  self.do_action(res_action);
                });
            }
            else {
                var connected = qz.websocket.connect({
                    host: action.printer_config_dict.hostname,
                    port: action.printer_config_dict.port,
                    usingSecure: action.printer_config_dict.use_secure,
                    keepAlive: action.printer_config_dict.keep_alive,
                    retries: action.printer_config_dict.retries,
                    delay: action.printer_config_dict.delay,
                });
                connected.then(function() {
                    var config = qz.configs.create(
                        action.printer_name, action.printer_option
                    );
                    var chain = [];
                    for(var i = 0; i <= action.print_data_len; i++) {
                        (function(i_) {
                            //setup this chain link
                            var link = function() {
                                return qz.printers.find(action.printer_name).then(function(found) {
                                    return qz.print(qz.configs.create(found, action.printer_option), action.print_data[i_]);
                                });
                            };

                            chain.push(link);
                        })(i);
                    }
                    //can be .connect or `Promise.resolve()`, etc
                    var firstLink = new RSVP.Promise(function(r, e) { r(); });

                    var lastLink = null;
                    chain.reduce(function(sequence, link) {
                        lastLink = sequence.then(link);
                        return lastLink;
                    }, firstLink);

                    //this will be the very last link in the chain
                    lastLink.catch(function(error) {
                        var res_action = {
                            type: 'ir.actions.act_window',
                            res_model: 'card.print.error.wizard',
                            view_mode: 'form',
                            view_type: 'form',
                            views: [[false, 'form']],
                            target: 'new',
                            context: {
                                'default_name': error.toString(),
                            },
                        }
                        return  self.do_action(res_action);
                    });
                }).catch(function(error) {
                    var res_action = {
                        type: 'ir.actions.act_window',
                        res_model: 'card.print.error.wizard',
                        view_mode: 'form',
                        view_type: 'form',
                        views: [[false, 'form']],
                        target: 'new',
                        context: {
                            'default_name': error.toString(),
                        },
                    }
                    return  self.do_action(res_action);
                });
            }
            if (!action.context.next_ids.length > 0){
                return self.do_action({'type': 'ir.actions.act_window_close'}) 
            }
            var res_action = {
                type: 'ir.actions.act_window',
                res_model: 'wizard.non.duplex.print',
                view_mode: 'form',
                view_type: 'form',
                views: [[false, 'form']],
                target: 'new',
                context: {
                    'default_template_id': action.context.template_id,
                    'default_is_front_side': !action.context.is_front_side,
                    'next_ids': action.context.next_ids,
                    'default_coupon_id': action.context.coupon_id,
                    'default_printer_id': action.context.printer_id,
                    'next_ids': action.context.next_ids,
                    'current_id': action.context.current_id
                },
            }
            return  self.do_action(res_action);
        },

        ir_actions_multibulk_printduplex: function(action, options) { 
            var self = this;
            var model = new WebModel(action.res_model);
            if (action.printer_config_dict.keypair) {
                // set the certificate used for privileged calls
                qz.security.setCertificatePromise(function(resolve, reject) {
                    if (action.printer_config_dict.keypair.keys) {
                        // use supplied certificate
                        resolve(action.printer_config_dict.keypair.keys);
                    }
                });

                // set the signing function for privileged calls
                qz.security.setSignaturePromise(function(toSign) {
                    //LOG: Authorizing
                    return function(resolve, reject) {
                        // POST to the signing route. CSRF token is passed automatically by Odoo's ajax.post()
                        resolve();
                    }
                });
            }

            if (qz.websocket.isActive()) {
                var config = qz.configs.create(
                    action.printer_name, action.printer_option
                );
                var chain = [];
                for(var i = 0; i <= action.print_data_len; i++) {
                    (function(i_) {
                        //setup this chain link
                        var link = function() {
                            return qz.printers.find(action.printer_name).then(function(found) {
                                return qz.print(qz.configs.create(found), action.print_data[i_]);
                            });
                        };

                        chain.push(link);
                    })(i);
                }
                //can be .connect or `Promise.resolve()`, etc
                var firstLink = new RSVP.Promise(function(r, e) { r(); });

                var lastLink = null;
                chain.reduce(function(sequence, link) {
                    lastLink = sequence.then(link);
                    return lastLink;
                }, firstLink);

                //this will be the very last link in the chain
                lastLink.catch(function(error) {
                    var res_action = {
                        type: 'ir.actions.act_window',
                        res_model: 'card.print.error.wizard',
                        view_mode: 'form',
                        view_type: 'form',
                        views: [[false, 'form']],
                        target: 'new',
                        context: {
                            'default_name': error.toString(),
                        },
                    }
                    return  self.do_action(res_action);
                });
            }
            else {
                var connected = qz.websocket.connect({
                    host: action.printer_config_dict.hostname,
                    port: action.printer_config_dict.port,
                    usingSecure: action.printer_config_dict.use_secure,
                    keepAlive: action.printer_config_dict.keep_alive,
                    retries: action.printer_config_dict.retries,
                    delay: action.printer_config_dict.delay,
                });
                connected.then(function() {
                    var config = qz.configs.create(
                        action.printer_name, action.printer_option
                    );
                    var chain = [];
                    for(var i = 0; i <= action.print_data_len; i++) {
                        (function(i_) {
                            //setup this chain link
                            var link = function() {
                                return qz.printers.find(action.printer_name).then(function(found) {
                                    return qz.print(qz.configs.create(found), action.print_data[i_]);
                                });
                            };

                            chain.push(link);
                        })(i);
                    }
                    //can be .connect or `Promise.resolve()`, etc
                    var firstLink = new RSVP.Promise(function(r, e) { r(); });

                    var lastLink = null;
                    chain.reduce(function(sequence, link) {
                        lastLink = sequence.then(link);
                        return lastLink;
                    }, firstLink);

                    //this will be the very last link in the chain
                    lastLink.catch(function(error) {
                        var res_action = {
                            type: 'ir.actions.act_window',
                            res_model: 'card.print.error.wizard',
                            view_mode: 'form',
                            view_type: 'form',
                            views: [[false, 'form']],
                            target: 'new',
                            context: {
                                'default_name': error.toString(),
                            },
                        }
                        return  self.do_action(res_action);
                    });

                }).catch(function(error) {
                    var res_action = {
                        type: 'ir.actions.act_window',
                        res_model: 'card.print.error.wizard',
                        view_mode: 'form',
                        view_type: 'form',
                        views: [[false, 'form']],
                        target: 'new',
                        context: {
                            'default_name': error.toString(),
                        },
                    }
                    return  self.do_action(res_action);
                });
            }
            self.inner_widget.active_view.controller.reload();
            return $.when();
        },
    });

});
