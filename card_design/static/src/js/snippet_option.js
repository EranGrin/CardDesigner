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
    

    /**
     * The borderpicker option is designed to change the border class of a snippet. This class change the
     * default border of the snippet content.
     */
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

    return {
        registry: registry,
    };

});