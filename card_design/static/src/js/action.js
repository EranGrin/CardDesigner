odoo.define('card_design.action', function (require) {
"use strict";

    var actionManager = require('web.ActionManager');

    actionManager.include({
        execute_ir_actions_multi_print: function(actions, options, index) {
            var self = this;
            for(var i=0;i<actions.length;i++) {
                self.ir_actions_act_url(
                    actions[i],
                    options
                )
            }
            return true;
        },

        ir_actions_multi_print: function(action, options) {
            return this.execute_ir_actions_multi_print(
                action.actions,
                options,
                0
            );
        },
    });
});
