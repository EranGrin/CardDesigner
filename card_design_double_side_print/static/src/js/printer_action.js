odoo.define('card_design_double_side_print.action', function(require) {
    'use strict';

    var WebActionManager = require('web.ActionManager');
    var WebModel = require("web.Model");

    WebActionManager.include({
        ir_actions_multi_printduplex: function(action, options) { 
            var self = this;
            var model = new WebModel(action.res_model);
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
        ir_actions_print_multiduplex: function(action, options) { 
            var self = this;
            var model = new WebModel(action.res_model);
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
        ir_actions_multi_printmultinonduplex: function(action, options) { 
            var self = this;
            var model = new WebModel(action.res_model);
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
            var res_action = {
                type: 'ir.actions.act_window',
                res_model: 'wizard.double.side.print',
                view_mode: 'form',
                view_type: 'form',
                views: [[false, 'form']],
                target: 'new',
                context: {
                    'is_gift_card': action.context.is_gift_card,
                    'gift_card_ids': action.context.gift_card_ids,
                    'default_res_model': 'wizard.double.side.print',
                    'default_template_id': action.res_id,
                },
            }
            return  self.do_action(res_action);
        },
        ir_actions_multi_printnonduplex: function(action, options) { 
            var self = this;
            var model = new WebModel(action.res_model);
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
            var res_action = {
                type: 'ir.actions.act_window',
                res_model: 'wizard.double.side.print',
                view_mode: 'form',
                view_type: 'form',
                views: [[false, 'form']],
                target: 'new',
                context: {
                    'is_gift_card': action.context.is_gift_card,
                    'gift_card_ids': action.context.gift_card_ids,
                    'default_res_model': 'wizard.double.side.print',
                    'default_template_id': action.res_id,
                },
            }
            return  self.do_action(res_action);
        },
        ir_actions_multi_backnonduplex: function(action, options) { 
            var self = this;
            var model = new WebModel(action.res_model);
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
            return self.do_action({'type': 'ir.actions.act_window_close'})
        },
    });

});