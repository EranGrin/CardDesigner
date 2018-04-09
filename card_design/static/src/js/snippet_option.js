odoo.define('card_design.snippets.options', function (require) {
    'use strict';


    var ajax = require('web.ajax');
    var Class = require('web.Class');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var base = require('web_editor.base');
    var editor = require('web_editor.editor');
    var widget = require('web_editor.widget');

    var qweb = core.qweb;
    var _t = core._t;
    var options = require('web_editor.snippets.options');
    var registry = options.registry;

    registry.borderpicker = options.Class.extend({
        start: function () {
            var self = this;
            var res = this._super.apply(this, arguments);

            if (!this.$el.find('.borderpicker').length) {
                var $pt = $(qweb.render('web_editor.snippet.option.borderpicker'));
                var $bdpicker = $(qweb.render('card_design.borderpicker'));

                // Retrieve excluded palettes list
                var excluded = [];
                if (this.data.paletteExclude) {
                    excluded = this.data.paletteExclude.replace(/ /g, '').split(',');
                }
                // Apply a custom title if specified
                if (this.data.paletteTitle) {
                    $pt.find('.note-palette-title').text(this.data.paletteTitle);
                }

                var $toggles = $pt.find('.o_borderpicker_section_menu');
                var $tabs = $pt.find('.o_borderpicker_section_tabs');

                // Remove excluded palettes
                _.each(excluded, function (exc) {
                    $bdpicker.find('[data-name="' + exc + '"]').remove();
                });

                var $sections = $bdpicker.find('.o_borderpicker_section');

                if ($sections.length > 1) { // Multi-palette layout
                    $sections.each(function () {
                        var $section = $(this);
                        var id = 'o_palette_' + $section.data('name') + _.uniqueId();

                        var $li = $('<li/>')
                                    .append($('<a/>', {href: '#' + id})
                                        .append($('<i/>', {'class': $section.data('iconClass') || '', html: $section.data('iconContent') || ''})));
                        $toggles.append($li);

                        $tabs.append($section.addClass('tab-pane').attr('id', id));
                    });

                    // If a default palette is defined, make it active
                    if (this.data.paletteDefault) {
                        var $palette_def = $tabs.find('div[data-name="' + self.data.paletteDefault + '"]');
                        var pos = $tabs.find('> div').index($palette_def);

                        $toggles.children('li').eq(pos).addClass('active');
                        $palette_def.addClass('active');
                    } else {
                        $toggles.find('li').first().addClass('active');
                        $tabs.find('div').first().addClass('active');
                    }

                    $toggles.on('click mouseover', '> li > a', function (e) {
                        e.preventDefault();
                        e.stopPropagation();
                        $(this).tab('show');
                    });
                } else if ($sections.length === 1) { // Unique palette layout
                    $tabs.addClass('o_unique_palette').append($sections.addClass('tab-pane active'));
                } else {
                    $toggles.parent().empty().append($bdpicker);
                }

                this.$el.find('li').append($pt);
            }
            if (this.$el.data('area')) {
                this.$target = this.$target.find(this.$el.data('area'));
                this.$el.removeData('area').removeAttr('area');
            }

            var classes = [];
            this.$el.find(".borderpicker button").each(function () {
                var $border = $(this);
                if (!$border.data("border")) {
                    return;
                }

                var className = 'bg-' + $border.data('border');
                $border.addClass(className);
                if (self.$target.hasClass(className)) {
                    self.border = className;
                    $border.addClass("selected");
                }
                classes.push(className);
            });
            this.classes = classes.join(" ");

            this.bind_events();
            return res;
        },
        bind_events: function () {
            var self = this;
            var $borders = this.$el.find(".borderpicker button");
            $borders
                .mouseenter(function (e) {
                    self.$target.removeClass(self.classes);
                    var border = $(this).data("border");
                    if (border) {
                        self.$target.addClass('bg-' + border);
                    }
                    self.$target.trigger("background-border-event", e.type);
                })
                .mouseleave(function (e) {
                    self.$target.removeClass(self.classes);
                    var $selected = $borders.filter(".selected");
                    var border = $selected.length && $selected.data("border");
                    if (border) {
                        self.$target.addClass('bg-' + border);
                    }
                    self.$target.trigger("background-border-event", e.type);
                })
                .click(function (e) {
                    $borders.removeClass("selected");
                    $(this).addClass("selected");
                    self.$target.closest(".o_editable").trigger("content_changed");
                    self.$target.trigger("background-border-event", e.type);
                });

            this.$el.find('.note-border-reset').on('click', function () {
                self.$target.removeClass(self.classes);
                $borders.removeClass("selected");
            });
        }
    });

    registry.bordersizepicker = options.Class.extend({
        start: function () {
            var self = this;
            var res = this._super.apply(this, arguments);

            if (!this.$el.find('.bordersizepicker').length) {
                var $pt = $(qweb.render('web_editor.snippet.option.bordersizepicker'));
                var $bdpicker = $(qweb.render('card_design.bordersizepicker'));

                // Retrieve excluded palettes list
                var excluded = [];
                if (this.data.paletteExclude) {
                    excluded = this.data.paletteExclude.replace(/ /g, '').split(',');
                }
                // Apply a custom title if specified
                if (this.data.paletteTitle) {
                    $pt.find('.note-palette-title').text(this.data.paletteTitle);
                }

                var $toggles = $pt.find('.o_borderpicker_section_menu');
                var $tabs = $pt.find('.o_borderpicker_section_tabs');

                // Remove excluded palettes
                _.each(excluded, function (exc) {
                    $bdpicker.find('[data-name="' + exc + '"]').remove();
                });

                var $sections = $bdpicker.find('.o_borderpicker_section');

                if ($sections.length > 1) { // Multi-palette layout
                    $sections.each(function () {
                        var $section = $(this);
                        var id = 'o_palette_' + $section.data('name') + _.uniqueId();

                        var $li = $('<li/>')
                                    .append($('<a/>', {href: '#' + id})
                                        .append($('<i/>', {'class': $section.data('iconClass') || '', html: $section.data('iconContent') || ''})));
                        $toggles.append($li);

                        $tabs.append($section.addClass('tab-pane').attr('id', id));
                    });

                    // If a default palette is defined, make it active
                    if (this.data.paletteDefault) {
                        var $palette_def = $tabs.find('div[data-name="' + self.data.paletteDefault + '"]');
                        var pos = $tabs.find('> div').index($palette_def);

                        $toggles.children('li').eq(pos).addClass('active');
                        $palette_def.addClass('active');
                    } else {
                        $toggles.find('li').first().addClass('active');
                        $tabs.find('div').first().addClass('active');
                    }

                    $toggles.on('click mouseover', '> li > a', function (e) {
                        e.preventDefault();
                        e.stopPropagation();
                        $(this).tab('show');
                    });
                } else if ($sections.length === 1) { // Unique palette layout
                    $tabs.addClass('o_unique_palette').append($sections.addClass('tab-pane active'));
                } else {
                    $toggles.parent().empty().append($bdpicker);
                }

                this.$el.find('li').append($pt);
            }
            if (this.$el.data('area')) {
                this.$target = this.$target.find(this.$el.data('area'));
                this.$el.removeData('area').removeAttr('area');
            }

            var classes = [];
            this.$el.find(".bordersizepicker button").each(function () {
                var $border = $(this);
                if (!$border.data("border-width")) {
                    return;
                }

                var className = 'bg-' + $border.data('border-width');
                $border.addClass(className);
                if (self.$target.hasClass(className)) {
                    self.border = className;
                    $border.addClass("selected");
                }
                classes.push(className);
            });
            this.classes = classes.join(" ");

            this.bind_events();
            return res;
        },
        bind_events: function () {
            var self = this;
            var $borders = this.$el.find(".bordersizepicker button");
            $borders
                .mouseenter(function (e) {
                    self.$target.removeClass(self.classes);
                    var border = $(this).data("border-width");
                    if (border) {
                        self.$target.addClass('bg-' + border);
                    }
                    self.$target.trigger("background-border-event", e.type);
                })
                .mouseleave(function (e) {
                    self.$target.removeClass(self.classes);
                    var $selected = $borders.filter(".selected");
                    var border = $selected.length && $selected.data("border-width");
                    if (border) {
                        self.$target.addClass('bg-' + border);
                    }
                    self.$target.trigger("background-border-event", e.type);
                })
                .click(function (e) {
                    $borders.removeClass("selected");
                    $(this).addClass("selected");
                    self.$target.closest(".o_editable").trigger("content_changed");
                    self.$target.trigger("background-border-event", e.type);
                });

            this.$el.find('.note-border-reset').on('click', function () {
                self.$target.removeClass(self.classes);
                $borders.removeClass("selected");
            });
        }
    });

    registry.bordercolorpicker = options.Class.extend({
        start: function () {
            var self = this;
            var res = this._super.apply(this, arguments);

            if (!this.$el.find('.bordercolorpicker').length) {
                var $pt = $(qweb.render('web_editor.snippet.option.bordercolorpicker'));
                var $clpicker = $(qweb.render('card_design.bordercolorpicker'));

                // Retrieve excluded palettes list
                var excluded = [];
                if (this.data.paletteExclude) {
                    excluded = this.data.paletteExclude.replace(/ /g, '').split(',');
                }
                // Apply a custom title if specified
                if (this.data.paletteTitle) {
                    $pt.find('.note-palette-title').text(this.data.paletteTitle);
                }

                var $toggles = $pt.find('.o_colorpicker_section_menu');
                var $tabs = $pt.find('.o_colorpicker_section_tabs');

                // Remove excluded palettes
                _.each(excluded, function (exc) {
                    $clpicker.find('[data-name="' + exc + '"]').remove();
                });

                var $sections = $clpicker.find('.o_colorpicker_section');

                if ($sections.length > 1) { // Multi-palette layout
                    $sections.each(function () {
                        var $section = $(this);
                        var id = 'o_palette_' + $section.data('name') + _.uniqueId();

                        var $li = $('<li/>')
                                    .append($('<a/>', {href: '#' + id})
                                        .append($('<i/>', {'class': $section.data('iconClass') || '', html: $section.data('iconContent') || ''})));
                        $toggles.append($li);

                        $tabs.append($section.addClass('tab-pane').attr('id', id));
                    });

                    // If a default palette is defined, make it active
                    if (this.data.paletteDefault) {
                        var $palette_def = $tabs.find('div[data-name="' + self.data.paletteDefault + '"]');
                        var pos = $tabs.find('> div').index($palette_def);

                        $toggles.children('li').eq(pos).addClass('active');
                        $palette_def.addClass('active');
                    } else {
                        $toggles.find('li').first().addClass('active');
                        $tabs.find('div').first().addClass('active');
                    }

                    $toggles.on('click mouseover', '> li > a', function (e) {
                        e.preventDefault();
                        e.stopPropagation();
                        $(this).tab('show');
                    });
                } else if ($sections.length === 1) { // Unique palette layout
                    $tabs.addClass('o_unique_palette').append($sections.addClass('tab-pane active'));
                } else {
                    $toggles.parent().empty().append($clpicker);
                }

                this.$el.find('li').append($pt);
            }
            if (this.$el.data('area')) {
                this.$target = this.$target.find(this.$el.data('area'));
                this.$el.removeData('area').removeAttr('area');
            }

            var classes = [];
            this.$el.find(".colorpicker button").each(function () {
                var $color = $(this);
                if (!$color.data("border-color")) {
                    return;
                }

                var className = 'bg-' + $color.data('border-color');
                $color.addClass(className);
                if (self.$target.hasClass(className)) {
                    self.color = className;
                    $color.addClass("selected");
                }
                classes.push(className);
            });
            this.classes = classes.join(" ");

            this.bind_events();
            return res;
        },
        bind_events: function () {
            var self = this;
            var $colors = this.$el.find(".colorpicker button");
            $colors
                .mouseenter(function (e) {
                    self.$target.removeClass(self.classes);
                    var color = $(this).data("border-color");
                    if (color) {
                        self.$target.addClass('bg-' + color);
                    }
                    self.$target.trigger("background-color-event", e.type);
                })
                .mouseleave(function (e) {
                    self.$target.removeClass(self.classes);
                    var $selected = $colors.filter(".selected");
                    var color = $selected.length && $selected.data("border-color");
                    if (color) {
                        self.$target.addClass('bg-' + color);
                    }
                    self.$target.trigger("background-color-event", e.type);
                })
                .click(function (e) {
                    $colors.removeClass("selected");
                    $(this).addClass("selected");
                    self.$target.closest(".o_editable").trigger("content_changed");
                    self.$target.trigger("background-color-event", e.type);
                });

            this.$el.find('.note-color-reset').on('click', function () {
                self.$target.removeClass(self.classes);
                $colors.removeClass("selected");
            });
            // Remove inline background-color for normal class-based buttons
            this.$el.find(".o_colorpicker_section button[data-border-color]").on(
                "click",
                $.proxy(this.remove_inline_background_color, this)
            );
            // Enable custom color picker
            this.$custom = this.$el.find('[data-name="custom_color"]');
            this.$custom.colorpicker({
                color: this.$target.css("background-color"),
                container: true,
                inline: true,
                sliders: {
                    saturation: {
                        maxLeft: 118,
                        maxTop: 118,
                    },
                    hue: {
                        maxTop: 118,
                    },
                    alpha: {
                        maxTop: 118,
                    },
                },
            });
            this.$custom.on(
                "changeColor",
                $.proxy(this.set_inline_background_color, this));
            this.$custom.on(
                "click keypress keyup keydown",
                $.proxy(this.custom_abort_event, this));
            this.$custom.on(
                "click", "input",
                $.proxy(this.input_select, this));
            this.$el.find(".note-color-reset").on(
                "click",
                $.proxy(this.remove_inline_background_color, this));
            // Activate border color changes if it matches background's
            var style = this.$target.prop("style");
            this.change_border =
                style["border-color"] &&
                style["background-color"] === style["border-color"];
        },
        custom_abort_event: function (event) {
            // HACK Avoid dropdown disappearing when picking colors
            event.stopPropagation();
        },
        input_select: function (event) {
            $(event.target).focus().select();
        },
        remove_inline_background_color: function (event) {
            this.$target.css("border-color", "");
            if (this.change_border) {
                this.$target.css("border-color", "");
            }
            this.$target.trigger("background-color-event", event.type);
        },
        set_inline_background_color: function (event) {
            var color = String(event.color);
            this.$target.css("border-color", color);
            if (this.change_border) {
                this.$target.css("border-color", color);
            }
            this.$target.trigger("background-color-event", event.type);
        },
    });

    return {
        registry: registry,
    };

});