odoo.define('web_snippet_mass_mail.editor', function (require) {
"use strict";

var ajax = require("web.ajax");
var core = require("web.core");
var rte = require('web_editor.rte');
var web_editor = require('web_editor.editor');
var options = require('web_editor.snippets.options');
var snippets_editor = require('web_editor.snippet.editor');
var $editable_area = $("#editable_area");
var odoo_top = window.top.odoo;


snippets_editor.Class.include({
    compute_snippet_templates: function (html) {
        var self = this;
        var ret = this._super.apply(this, arguments);
        /**
         * Initialize theme parameters.
         */
        var all_classes = "";
        var $body = $(document.body);
        var $snippets = this.$(".oe_snippet");
        var $snippets_menu = this.$el.find("#snippets_menu");
        var selected_theme = false;
        var theme_params = {
            'className': "o_default_theme",
            'img': "/card_design/static/src/img/theme_imgs/default_thumb",
            'name': "default",
            'template': ""
        };

        var first_choice;

        if ($('.o_designer_wrapper_td').length){
            first_choice = false;
        }
        switch_theme(theme_params);
        $body.removeClass("o_force_mail_theme_choice");
        switch_images(theme_params, $snippets);
        selected_theme = theme_params;
        // Notify form view
        odoo_top[window.callback+"_downup"]($editable_area.addClass("o_dirty").html());
        
        var $snippets_change_size = this.$el.find("#input_snippets_template_size");
        $snippets_change_size.on('change', function (e) {
            e.preventDefault();
            var value = '';
            var width = 0;
            var height = 0;
            if ($('.o_designer_wrapper_td').length) {
                if (this.value){
                    value = this.value.replace('(', '').replace(')', '').split(", ");
                    width = parseInt(value[0]);
                    height = parseInt(value[1]);
                    $('.o_designer_wrapper_td').css({
                        "width": width, "height": height,
                        "overflow": "hidden",
                        "margin-left": "auto",
                        "margin-right": "auto"  
                    });
                } else{
                    $('.o_designer_wrapper_td').css({
                        "height": "500px",
                        "overflow": "hidden",
                        "margin-left": "auto",
                        "margin-right": "auto",
                        "width": ""
                    });
                }
            }
        });
        $body.addClass(selected_theme.className);
        switch_images(selected_theme, $snippets);
        return ret;

        function check_if_must_force_theme_choice() {
            first_choice = editable_area_is_empty();
            $body.toggleClass("o_force_mail_theme_choice", first_choice);
        }

        function editable_area_is_empty($layout) {
            $layout = $layout || $editable_area.find(".o_layout");
            var $mail_wrapper = $layout.children(".o_designer_wrapper");
            var $mail_wrapper_content = $mail_wrapper.find('.o_designer_wrapper_td');
            if (!$mail_wrapper_content.length) { // compatibility
                $mail_wrapper_content = $mail_wrapper;
            }
            return (
                $editable_area.html().trim() === ""
                || ($layout.length > 0 && ($layout.html().trim() === "" || $mail_wrapper_content.length > 0 && $mail_wrapper_content.html().trim() === ""))
            );
        }

        function check_selected_theme() {
            var $layout = $editable_area.find(".o_layout");
            if ($layout.length === 0) {
                selected_theme = false;
            } else {
                _.each(themes_params, function (theme_params) {
                    if ($layout.hasClass(theme_params.className)) {
                        selected_theme = theme_params;
                    }
                });
            }
        }

        function switch_images(theme_params, $container) {
            return
        }

        function switch_theme(theme_params) {
            if (!theme_params || switch_theme.last === theme_params) return;
            switch_theme.last = theme_params;

            $body.removeClass(all_classes).addClass(theme_params.className);
            switch_images(theme_params, $editable_area);

            var $old_layout = $editable_area.find(".o_layout");
            // This wrapper structure is the only way to have a responsive and
            // centered fixed-width content column on all mail clients
            var $new_wrapper = $('<div/>', {class: 'o_designer_wrapper'});
            var $new_wrapper_content = $("<div/>", {class: 'o_mail_no_resize o_designer_wrapper_td oe_structure fixed_heightx',
            style:'height:400px; overflow: hidden; margin-left: auto;margin-right: auto;width:400px;background:white;'});
            $new_wrapper.append($('<div/>', {class:'fixed_height'}).append(
                $new_wrapper_content,
            ));
            var $new_layout = $("<div/>", {"class": "o_layout " + theme_params.className}).append($new_wrapper);

            var $contents;
            if (first_choice) {
                $contents = theme_params.template;
            } else if ($old_layout.length) {
                $contents = ($old_layout.hasClass("oe_structure") ? $old_layout : $old_layout.find(".oe_structure").first()).contents();
            } else {
                $contents = $editable_area.contents();
            }

            $editable_area.empty().append($new_layout);
            $new_wrapper_content.append($contents);

            if (first_choice) {
                self.add_default_snippet_text_classes($new_wrapper_content);
            }
            self.show_blocks();
        }
    },
});

});
