odoo.define('card_design_printer.action', function(require) {
    'use strict';

    var WebActionManager = require('web.ActionManager');
    var WebModel = require("web.Model");
    var ajax = require("web.ajax");


    WebActionManager.include({
        ir_actions_printer_connect: function(action, options) { 
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
                 model.call("write", [
                    action.res_id, 
                    {
                        "active_msg": "An open connection with QZ Tray already exists",
                        "is_active": true,
                        "state": "done"
                    }
                ]);
                self.inner_widget.active_view.controller.reload();
                return $.when();
            }
            
            var connected = qz.websocket.connect({
                host: action.printer_config_dict.hostname,
                port: action.printer_config_dict.port,
                usingSecure: action.printer_config_dict.use_secure,
                keepAlive: action.printer_config_dict.keep_alive,
                retries: action.printer_config_dict.retries,
                delay: action.printer_config_dict.delay,
            });

            connected.then(function() {
                model.call("write", [
                    action.res_id, 
                    {
                        "state": "done"
                    }
                ]);
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
            })

            self.inner_widget.active_view.controller.reload();
            return $.when();
        },

        ir_actions_printer_list: function(action, options) {
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
                var found = qz.printers.find();
                found.then(function(printer_names) {
                    found.then(function(printer_names) {
                        model.call("update_printer_list",[
                            action.res_id,
                            {
                                'printer_names': printer_names
                            }
                        ]);
                    });
                });
                self.inner_widget.active_view.controller.reload();
                return $.when();
            }

            var connected = qz.websocket.connect({
                host: action.printer_config_dict.hostname,
                port: action.printer_config_dict.port,
                usingSecure: action.printer_config_dict.use_secure,
                keepAlive: action.printer_config_dict.keep_alive,
                retries: action.printer_config_dict.retries,
                delay: action.printer_config_dict.delay,
            });

            connected.then(function() {
                var found = qz.printers.find();
                found.then(function(printer_names) {
                    model.call("update_printer_list",[
                        action.res_id,
                        {
                            'printer_names': printer_names
                        }
                    ]);
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
            })

            self.inner_widget.active_view.controller.reload();
            return $.when();
        },

        ir_actions_print_data: function(action, options) {
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
                for(var i = 0; i <= action.print_data_len; i++) {
                    var print_data = action.print_data[i];
                    qz.print(config, print_data).catch(function(error) {
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
                    for(var i = 0; i <= action.print_data_len; i++) {
                        var print_data = action.print_data[i];
                        qz.print(config, print_data).catch(function(error) {
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

        ir_actions_print_multidata: function(action, options) { 
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