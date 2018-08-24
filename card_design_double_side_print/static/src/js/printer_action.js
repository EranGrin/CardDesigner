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
                    action.printer_name
                );
                for(var i = 0; i <= action.print_data_len; i++) {
                    var print_data = action.print_data[i];
                    qz.print(config, print_data).catch(function(e) {
                        model.call("write", [
                            action.res_id,
                            {
                                "error": error.toString(),
                                "is_error": true
                            }
                        ]);
                        self.inner_widget.active_view.controller.reload();
                        return $.when();
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
                        action.printer_name
                    );
                    for(var i = 0; i <= action.print_data_len; i++) {
                        var print_data = action.print_data[i];
                        qz.print(config, print_data).catch(function(e) {
                            model.call("write", [
                                action.res_id,
                                {
                                    "error": error.toString(),
                                    "is_error": true
                                }
                            ]);
                            self.inner_widget.active_view.controller.reload();
                            return $.when();
                        });
                    }
                }).catch(function(error) {
                    model.call("write", [
                        action.res_id, 
                        {
                            "error": error.toString(),
                            "is_error": true
                        }
                    ]);
                    self.inner_widget.active_view.controller.reload();
                    return $.when();
                });
            }
            self.inner_widget.active_view.controller.reload();
            return $.when();
        },
        ir_actions_multi_printnonduplex: function(action, options) { 
            var self = this;
            var model = new WebModel(action.res_model);
            if (qz.websocket.isActive()) {
                var config = qz.configs.create(
                    action.printer_name
                );
                for(var i = 0; i <= action.print_data_len; i++) {
                    var print_data = action.print_data[i];
                    qz.print(config, print_data).catch(function(e) {
                        model.call("write", [
                            action.res_id,
                            {
                                "error": error.toString(),
                                "is_error": true
                            }
                        ]);
                        self.inner_widget.active_view.controller.reload();
                        return $.when();
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
                        action.printer_name
                    );
                    for(var i = 0; i <= action.print_data_len; i++) {
                        var print_data = action.print_data[i];
                        qz.print(config, print_data).catch(function(e) {
                            model.call("write", [
                                action.res_id,
                                {
                                    "error": error.toString(),
                                    "is_error": true
                                }
                            ]);
                            self.inner_widget.active_view.controller.reload();
                            return $.when();
                        });
                    }
                }).catch(function(error) {
                    model.call("write", [
                        action.res_id, 
                        {
                            "error": error.toString(),
                            "is_error": true
                        }
                    ]);
                    self.inner_widget.active_view.controller.reload();
                    return $.when();
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
                    action.printer_name
                );
                for(var i = 0; i <= action.print_data_len; i++) {
                    var print_data = action.print_data[i];
                    qz.print(config, print_data).catch(function(e) {
                        model.call("write", [
                            action.res_id,
                            {
                                "error": error.toString(),
                                "is_error": true
                            }
                        ]);
                        self.inner_widget.active_view.controller.reload();
                        return $.when();
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
                        action.printer_name
                    );
                    var print_data = action.print_data;
                    for(var i = 0; i <= action.print_data_len; i++) {
                        var print_data = action.print_data[i];
                        qz.print(config, print_data).catch(function(e) {
                            model.call("write", [
                                action.res_id,
                                {
                                    "error": error.toString(),
                                    "is_error": true
                                }
                            ]);
                            self.inner_widget.active_view.controller.reload();
                            return $.when();
                        });
                    }
                }).catch(function(error) {
                    model.call("write", [
                        action.res_id, 
                        {
                            "error": error.toString(),
                            "is_error": true
                        }
                    ]);
                    self.inner_widget.active_view.controller.reload();
                    return $.when();
                });
            }
            return self.do_action({'type': 'ir.actions.act_window_close'})
        },
    });

});