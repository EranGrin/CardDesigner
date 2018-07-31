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
            var base64 = action.print_data;

            if (action.language == 'EPL') {
                // EPL
                var print_data = []
                var headerarray = action.header_data.split(',');

                for(var i = 0; i < headerarray.length; i++)
                {
                    var headerarraydata =  "\n"+headerarray[i]+"\n";
                    print_data.push(headerarraydata);
                }
                print_data.push({
                    type: action.data_type, format: action.data_format,
                    data: base64,
                    options: { language: action.language, x: action.epl_x, y: action.epl_y}
                });
                var footerarray = action.footer_data.split(',');
                for(var i = 0; i < footerarray.length; i++)
                {
                    var footerarraydata = "\n"+footerarray[i]+"\n";
                    print_data.push(footerarraydata);
                }
            }

            if (action.language == 'ZPL') {
                // ZPL
                var print_data = []
                var headerarray = action.header_data.split(',');

                for(var i = 0; i < headerarray.length; i++)
                {
                    var headerarraydata =  headerarray[i]+"\n";
                    print_data.push(headerarraydata);
                }
                print_data.push({
                    type: action.data_type, format: action.data_format,
                    data: base64,
                    options: { language: action.language}
                });
                var footerarray = action.footer_data.split(',');
                for(var i = 0; i < footerarray.length; i++)
                {
                    var footerarraydata = footerarray[i]+"\n";
                    print_data.push(footerarraydata);
                }
            }

            if (action.language == 'EVOLIS') {
                // EVOLIS
                var print_data = []
                var headerarray = action.header_data.split(',');

                for(var i = 0; i < headerarray.length; i++)
                {
                    var headerarraydata = '\x1B' + headerarray[i] + "\x0D";
                    print_data.push(headerarraydata);
                }
                print_data.push({
                    type: action.data_type,
                    format: action.data_format,
                    data: base64,
                    options: {
                        language: action.language,
                        precision: action.precision,
                        overlay: action.overlay
                    }
                });
                var footerarray = action.footer_data.split(',');
                for(var i = 0; i < footerarray.length; i++)
                {
                    var footerarraydata = '\x1B' + footerarray[i] + "\x0D";
                    print_data.push(footerarraydata);
                }
            }

            var printers_dict = {
                size: {width: 2, height: 1},
                units: 'in',
                colorType: 'grayscale',
                interpolation: "nearest-neighbor",
                margins: { top: 1.25, right: 1.25, bottom: 1.25, left: 1.25 },
                density: 25,
                jobName: action.jobName
            }

            if (qz.websocket.isActive()) {
                var config = qz.configs.create(
                    action.printer_name, printers_dict
                );
                qz.print(config, print_data).catch(function(e) { 
                   model.call("write", [
                        action.res_id, 
                        {
                            "error": error.toString(),
                            "is_error": true
                        }
                    ]);
                });
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
                var config = qz.configs.create(
                    action.printer_name, printers_dict
                );
                qz.print(config, print_data).catch(function(e) { 
                    model.call("write", [
                        action.res_id, 
                        {
                            "error": error.toString(),
                            "is_error": true
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
    });
});