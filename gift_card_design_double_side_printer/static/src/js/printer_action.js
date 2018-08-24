odoo.define('gift_card_design_double_side_printer.action', function(require) {
    'use strict';

    var WebActionManager = require('web.ActionManager');
    var WebModel = require("web.Model");

    WebActionManager.include({
        ir_actions_multi_nonbulk: function(action, options) { 
            var self = this;
            var model = new WebModel(action.res_model);
            if (qz.websocket.isActive()) {
                var config = qz.configs.create(
                    action.printer_name
                );
                for(var i = 0; i < action.print_data_len; i++) {
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
                    for(var i = 0; i < action.print_data_len; i++) {
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
    });

});
