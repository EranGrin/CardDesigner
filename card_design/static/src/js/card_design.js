odoo.define('card_design.card_design', function (require) {

    var FieldTextHtml = require('web_editor.backend').FieldTextHtml;
    var KanbanColumn = require("web_kanban.Column");
    var KanbanView = require('web_kanban.KanbanView');

    KanbanColumn.include({
        init: function () {
            this._super.apply(this, arguments);
            if (this.dataset.model === 'card.template') {
                this.draggable = false;
            }
        },
    });

    KanbanView.include({
        on_groups_started: function() {
            this._super.apply(this, arguments);
            if (this.dataset.model === 'card.template') {
                this.$el.find('.oe_kanban_draghandle').removeClass('oe_kanban_draghandle');
            }
        },
    });

    FieldTextHtml.include({
        get_datarecord: function() {
            /* Avoid extremely long URIs by whitelisting fields in the datarecord
            that get set as a get parameter */
            var datarecord = this._super();
            if (this.view.model === 'card.template') {
                delete datarecord[this.name];
            }
            return datarecord;
        },
    });

});
