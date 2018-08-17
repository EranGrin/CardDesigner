odoo.define('card_design_printer.action', function(require) {
    'use strict';

    var WebActionManager = require('web.ActionManager');
    var WebModel = require("web.Model");

    WebActionManager.include({
        ir_actions_printer_connect: function(action, options) { 
            var self = this;
            var model = new WebModel(action.res_model);
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
                model.call("write", [
                    action.res_id, 
                    {
                        "error": error.toString(),
                        "is_error": true
                    }
                ]);
            })

            self.inner_widget.active_view.controller.reload();
            return $.when();
        },

        ir_actions_printer_list: function(action, options) {
            var self = this;
            var model = new WebModel(action.res_model);
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
                model.call("write", [
                    action.res_id, 
                    {
                        "error": error.toString(),
                        "is_error": true
                    }
                ]);
            })

            self.inner_widget.active_view.controller.reload();
            return $.when();
        },

        ir_actions_print_data: function(action, options) {
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
    });
});