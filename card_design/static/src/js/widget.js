odoo.define('card_design.widget', function (require) {
'use strict';

    var core = require('web.core');
    var ajax = require('web.ajax');
    var widget_editor = require('web_editor.widget');
    var Dialog = require('web.Dialog');
    var Widget = require('web.Widget');
    var base = require('web_editor.base');
    var rte = require('web_editor.rte');
    var QWeb = core.qweb;
    var range = $.summernote.core.range;
    var dom = $.summernote.core.dom;
    var _t = core._t;

    var position_argument = Dialog.extend({
        template: 'card_design.dialog.position',
        init: function (parent, options, $editable, media) {
            this._super(parent, _.extend({}, {
                title: _t("Style"),
            }, options));

            this.$editable = $editable;
            this.media = media;
            var temp = $.parseHTML(
                "<div style='float:letf;'width:380px;'>" + this.$modal[0].outerHTML + "</div>"
            )[0];
            $('#wrapwrap').css({'width': '68%'});
            $('#wrapwrap')[0].after(temp);
            this.alt = ($(this.media).attr('alt') || "").replace(/&quot;/g, '"');
            this.title = ($(this.media).attr('title') || "").replace(/&quot;/g, '"');
            this.$modal.css({'display': 'block'})
            this.$modal.find('.modal-dialog').css({
                'right': '0px',
                'position': 'fixed',
                'width':'380px',
                'height': '100%',
                'overflow-y': 'auto',
                'top': '3px',
            });
            this.$modal.find('.modal-dialog').addClass('o_select_style_dialog');
            this.$modal.find('.modal-header').css({
                'color': 'white'
            });
            this.$modal.find('.modal-content').css({
                'background-color': '#444444',
                'border-radius': '0px'
            });
            this.$modal.find('.modal-footer > button').css({
                'display': 'none'
            });
            var self = this;
            var $win = $(document);
            this.$modal.addClass('note-style-dialog');
            var $box = this.$modal.find(".o_select_style_dialog");
            $win.on("click.Bst", function(event){
                if ($box.has(event.target).length == 0 && !$box.is(event.target)){
                    if (event.target.className == 'modal note-style-dialog in'){
                        self.$modal.modal('hide');
                    }
                }
            });
        },
        save: function () {
            var self = this;
            var style = this.media.attributes.style ? this.media.attributes.style.value : '';
            if (this.media.tagName !== "DIV") {
                var media = document.createElement('div');
                $(media).data($(this.media).data());
                $(this.media).replaceWith(media);
                this.media = media;
                style = style.replace(/\s*width:[^;]+/, '');
            }
            $(this.media).attr("style", style);
            return this.media;
        },
        renderElement: function() {
            this._super();
            var self = this;
            var initialValues = {
                margins: {
                    top: false,
                    left: false,
                    bottom: false,
                    right: false
                },
                paddings: {
                    top: false,
                    left: false,
                    bottom: false,
                    right: false
                },
                borders: {
                    top: false,
                    left: false,
                    bottom: false,
                    right: false
                },
                dimensions: {
                    height: false,
                    width: false,
                } 
            };
            if (this.media.style) {
                var float_arg = this.$el.find('input:radio[name=option]');
                var position_arg = this.$el.find('input:radio[name=position]');
                var overflow_arg = this.$el.find('input[type=radio][name=overflow]');
                var zindex_arg = this.$el.find('#zindex');
                var pptop_arg = this.$el.find('#ptop');
                var ppleft_arg = this.$el.find('#pleft');
                var ppright_arg = this.$el.find('#pright');
                var ppbottom_arg = this.$el.find('#pbottom');
                var ptstyle_arg = this.$el.find('#ptstyle');
                var plstyle_arg = this.$el.find('#plstyle');
                var prstyle_arg = this.$el.find('#prstyle');
                var pbstyle_arg = this.$el.find('#pbstyle');
                var background_arg = this.$el.find('#background-color')
                var pbordercolor_arg = this.$el.find('#border-color');
                var pborder_arg = this.$el.find('#pborder');
                var tlradius_arg = this.$el.find('#tlradius');
                var trradius_arg = this.$el.find('#trradius');
                var brradius_arg = this.$el.find('#brradius');
                var blradius_arg = this.$el.find('#blradius');
                var tlstyle_arg = this.$el.find('#tlstyle');
                var trstyle_arg = this.$el.find('#trstyle');
                var blstyle_arg = this.$el.find('#blstyle');
                var brstyle_arg = this.$el.find('#brstyle');

                if (background_arg) {
                    if (this.media.style.backgroundColor) {
                        background_arg.val(this.media.style.backgroundColor);
                    }
                }
                if (float_arg) {
                    if (this.media.style.float) {
                        this.$el.find('#float-' + this.media.style.float).prop('checked', true);
                    }
                }
                if (position_arg) {
                    if (this.media.style.position) {
                        this.$el.find('#position-' + this.media.style.position).prop('checked', true);
                    }
                }
                if (overflow_arg) {
                    if (this.media.style.overflow) {
                        this.$el.find('#overflow-' + this.media.style.overflow).prop('checked', true);
                    }
                }
                if (zindex_arg) {
                    if (this.media.style.zIndex) {
                        zindex_arg.val(parseInt(this.media.style.zIndex));
                    }
                }
                if (pbordercolor_arg) {
                    if (this.media.style.borderColor) {
                        pbordercolor_arg.val(this.media.style.borderColor);
                    }
                }
                if (this.media.style.width) {
                    var demo = this.media.style.width
                    var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                    var style_top = demo.split(value)
                    initialValues.dimensions.width = value + style_top[1];
                }
                if (this.media.style.height) {
                    var demo = this.media.style.height
                    var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                    var style_top = demo.split(value)
                    initialValues.dimensions.height = value + style_top[1];
                }
                if (this.media.style.top) {
                    var demo = this.media.style.top
                    var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                    var style_top = demo.split(value)
                    pptop_arg.val(value);
                    ptstyle_arg.val(style_top[1]);
                }
                if (this.media.style.left) {
                    var demo = this.media.style.left
                    var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                    var style_top = demo.split(value)
                    ppleft_arg.val(value);
                    plstyle_arg.val(style_top[1]);
                }
                if (this.media.style.bottom) {
                    var demo = this.media.style.bottom
                    var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                    var style_top = demo.split(value)
                    ppbottom_arg.val(value);
                    pbstyle_arg.val(style_top[1]);
                }
                if (this.media.style.right) {
                    var demo = this.media.style.right
                    var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                    var style_top = demo.split(value)
                    ppright_arg.val(value);
                    prstyle_arg.val(style_top[1]);
                }
                if (this.media.style.marginTop) {
                    var demo = this.media.style.marginTop
                    var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                    var style_top = demo.split(value)
                    initialValues.margins.top = value + style_top[1];
                }
                if (this.media.style.marginLeft) {
                    var demo = this.media.style.marginLeft
                    var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                    var style_top = demo.split(value)
                    initialValues.margins.left = value + style_top[1];
                }
                if (this.media.style.marginRight) {
                    var demo = this.media.style.marginRight
                    var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                    var style_top = demo.split(value)
                    initialValues.margins.right = value + style_top[1];
                }
                if (this.media.style.marginBottom) {
                    var demo = this.media.style.marginBottom
                    var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                    var style_top = demo.split(value)
                    initialValues.margins.bottom = value + style_top[1];
                }
                if (this.media.style.paddingTop) {
                    var demo = this.media.style.paddingTop
                    var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                    var style_top = demo.split(value)
                    initialValues.paddings.top = value + style_top[1];
                }
                if (this.media.style.paddingLeft) {
                    var demo = this.media.style.paddingLeft
                    var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                    var style_top = demo.split(value)
                    initialValues.paddings.left = value + style_top[1];
                }
                if (this.media.style.paddingRight) {
                    var demo = this.media.style.paddingRight
                    var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                    var style_top = demo.split(value)
                    initialValues.paddings.right = value + style_top[1];
                }
                if (this.media.style.paddingBottom) {
                    var demo = this.media.style.paddingBottom
                    var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                    var style_top = demo.split(value)
                    initialValues.paddings.bottom = value + style_top[1];
                }
                if (this.media.style.borderBottomWidth) {
                    initialValues.borders.bottom = this.media.style.borderBottomWidth;
                }
                if (this.media.style.borderTopWidth) {
                    initialValues.borders.top = this.media.style.borderTopWidth
                }
                if (this.media.style.borderRightWidth) {
                    initialValues.borders.right = this.media.style.borderRightWidth
                }
                if (this.media.style.borderLeftWidth) {
                    initialValues.borders.left = this.media.style.borderLeftWidth
                }
                if (pborder_arg) {
                    if (this.media.style.borderStyle) {
                        pborder_arg.val(this.media.style.borderStyle);
                    }
                }
                if (this.media.style.borderTopLeftRadius) {
                    var demo = this.media.style.borderTopLeftRadius
                    var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                    var style_top = demo.split(value)
                    tlradius_arg.val(value);
                    tlstyle_arg.val(style_top[1]);
                }
                if (this.media.style.borderTopRightRadius) {
                    var demo = this.media.style.borderTopRightRadius
                    var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                    var style_top = demo.split(value)
                    trradius_arg.val(value);
                    trstyle_arg.val(style_top[1]);
                }
                if (this.media.style.borderBottomLeftRadius) {
                    var demo = this.media.style.borderBottomLeftRadius
                    var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                    var style_top = demo.split(value)
                    blradius_arg.val(value);
                    blstyle_arg.val(style_top[1]);
                }
                if (this.media.style.borderBottomRightRadius) {
                    var demo = this.media.style.borderBottomRightRadius
                    var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                    var style_top = demo.split(value)
                    brradius_arg.val(value);
                    brstyle_arg.val(style_top[1]);
                }
            }
            this.$el.on('change', 'input[type=radio][name=overflow]', function (e) {
                if (self.media) {
                    if (self.media.style) {
                        if (e.target.value) {
                            self.media.style.overflow = e.target.value;
                        }
                        else {
                            self.media.style.overflow = "";
                        }
                    }
                }
            });
            this.$el.on('change', 'input[type=radio][name=position]', function (e) {
                if (self.media) {
                    if (self.media.style) {
                        if (e.target.value) {
                            self.media.style.position = e.target.value;
                        }
                        else {
                            self.media.style.position = "";
                        }
                    }
                }
            });
            this.$el.on('change', 'input[type=radio][name=float]', function (e) {
                if (self.media) {
                    if (self.media.style) {
                        if (e.target.value) {
                            self.media.style.float = e.target.value;
                        }
                        else {
                            self.media.style.float = "";
                        }
                    }
                }
            });
            this.$el.on('change', '#ptop, #ptstyle', function (e) {
                if (self.media) {
                    self.change_style(e, self, "ptstyle", "ptop", "top", '#ptstyle')
                }
            });
            this.$el.on('change', '#pleft, #plstyle', function (e) {
                if (self.media) {
                    self.change_style(e, self, "plstyle", "pleft", "left", '#plstyle')
                }
            });
            this.$el.on('change', '#pright, #prstyle', function (e) {
                if (self.media) {
                    self.change_style(e, self, "prstyle", "pright", "right", '#prstyle')
                }
            });
            this.$el.on('change', '#pbottom, #pbstyle', function (e) {
                if (self.media) {
                    self.change_style(e, self, "pbstyle", "pbottom", "bottom", '#pbstyle')
                }
            });
            this.$el.on('change', '#zindex', function (e) {
                if (self.media) {
                    if (self.media.style) {
                        if (e.target.value) {
                            self.media.style.zIndex = e.target.value;
                        }
                        else {
                            self.media.style.zIndex = "";
                        }
                    }
                }
            });
            this.$el.on('change', '#pborder', function (e) {
                if (self.media) {
                    if (self.media.style) {
                        if (e.target.value) {
                            self.media.style.borderStyle = e.target.value;
                        }
                        else {
                            self.media.style.borderStyle = "";
                        }
                    }
                }
            });
            this.$el.on('change', '#tlradius, #tlstyle', function (e) {
                if (self.media) {
                    self.change_style(e, self, "tlstyle", "tlradius", "border-top-left-radius", '#tlstyle')
                }
            });
            this.$el.on('change', '#trradius, #trstyle', function (e) {
                if (self.media) {
                    self.change_style(e, self, "trstyle", "trradius", "border-top-right-radius", '#trstyle')
                }
            });
            this.$el.on('change', '#blradius, #blstyle', function (e) {
                if (self.media) {
                    self.change_style(e, self, "blstyle", "blradius", "border-bottom-left-radius", '#blstyle')
                }
            });
            this.$el.on('change', '#brradius, #brstyle', function (e) {
                if (self.media) {
                    self.change_style(e, self, "brstyle", "brradius", "border-bottom-right-radius", '#brstyle')
                }
            });
            this.$background_custom = this.$el.find('#background-color');
            this.$el.find('#background-color').colorpicker()
            this.$background_custom.on(
                "changeColor",
                $.proxy(this.set_inline_background_color, this)
            );
            this.$background_custom.on(
                "click keypress keyup keydown",
                $.proxy(this.custom_abort_event_background, this)
            );
            this.$background_custom.on(
                "click", "input",
                $.proxy(this.input_select_background, this)
            );
            this.$el.find(".note-color-reset").on(
                "click",
                $.proxy(this.remove_inline_background_color, this)
            );
            this.$border_custom = this.$el.find('#border-color');
            this.$el.find('#border-color').colorpicker()
            this.$border_custom.on(
                "changeColor",
                $.proxy(this.set_inline_border_color, this)
            );
            this.$border_custom.on(
                "click keypress keyup keydown",
                $.proxy(this.custom_abort_event_border, this)
            );
            this.$border_custom.on(
                "click", "input",
                $.proxy(this.input_select_border, this)
            );
            this.$el.find(".note-color-reset").on(
                "click",
                $.proxy(this.remove_inline_border_color, this)
            );
            this.$el.on('change', '#pborderadius', function (e) {
                if (self.media) {
                    if (self.media.style) {
                        if (e.target.value) {
                            self.media.style.borderRadius = e.target.value + '%';
                        }
                        else {
                            self.media.style.borderRadius = "";
                        }
                    }
                }
            });
            this.$custom = this.$el.find("#boxmodel-ex-3").boxModel({
                'showEnabledUnits': false,
                'showShortcuts': false,
                'values': initialValues,
            });
            this.$custom.on("boxmodel:change", function(element, value, all){
                var style_name = value.context.name.split('boxmodel-ex-3_')[1];
                var sname = '';
                if (style_name == 'top_padding') {
                    sname = 'padding-top';
                }
                else if (style_name == 'bottom_padding') {
                    sname = 'padding-bottom';
                }
                else if (style_name == 'right_padding') {
                    sname = 'padding-right';
                }
                else if (style_name == 'left_padding') {
                    sname = 'padding-left';
                }
                else if (style_name == 'left_margin') {
                    sname = 'margin-left';
                }
                else if (style_name == 'top_margin') {
                    sname = 'margin-top';
                }
                else if (style_name == 'bottom_margin') {
                    sname = 'margin-bottom';
                }
                else if (style_name == 'right_margin') {
                    sname = 'margin-right';
                }
                else if (style_name == 'left_border') {
                    sname = 'border-left-width';
                }
                else if (style_name == 'top_border') {
                    sname = 'border-top-width';
                }
                else if (style_name == 'bottom_border') {
                    sname = 'border-bottom-width';
                }
                else if (style_name == 'right_border') {
                    sname = 'border-right-width';
                }
                else if (style_name == 'width') {
                    sname = 'width';
                }
                else if (style_name == 'height') {
                    sname = 'height';
                }
                self.box_change_style(self, value.context.value, sname)
            });
            return this
        },
        destroy: function(reason) {
            if (this.isDestroyed()) {
                return;
            }
            $('#wrapwrap').css({'width': '100%'});
            this.trigger("closed", reason);

            this._super();

            $('.tooltip').remove(); //remove open tooltip if any to prevent them staying when modal has disappeared
            this.$modal.modal('hide');
            this.$modal.remove();

            setTimeout(function () { // Keep class modal-open (deleted by bootstrap hide fnct) on body to allow scrolling inside the modal
                var modals = $('body > .modal').filter(':visible');
                if(modals.length) {
                    modals.last().focus();
                    $('body').addClass('modal-open');
                }
            }, 0);
        },
        box_change_style: function (self, element_value, style_name) {
            if (self.media && self.media.style) {
                if (element_value == '-') {
                    self.media.style.removeProperty(style_name);
                }
                else if (element_value) {
                    self.media.style.setProperty(style_name, element_value, null)
                }
                else {
                    self.media.style.removeProperty(style_name);
                }
            }
        },
        change_style: function (e, self, style_target, value_target, style_name, current_style) {
            if (self.media && self.media.style) {
                if (e.target.value) {
                    if (e.target.id == value_target) {
                        if (e.target.value) {
                            var value = parseInt(self.media.style.getPropertyValue(style_name))
                            if (value) {
                                var style_top = self.media.style.getPropertyValue(style_name).split(value)
                                self.media.style.setProperty(style_name, e.target.value + style_top[1], null)
                            }
                            else{
                                self.media.style.setProperty(style_name, e.target.value + self.$el.find(current_style).val(), null)
                            }
                        }
                    }
                    else {
                        if (e.target.id == style_target) {
                            if (e.target.value) {
                                var value = parseInt(self.media.style.getPropertyValue(style_name))
                                if (value) {
                                    var style_top = self.media.style.getPropertyValue(style_name).split(value)
                                    self.media.style.setProperty(style_name, value + e.target.value, null)
                                }
                            }
                        }
                    }
                }
                else {
                    self.media.style.removeProperty(style_name);
                }
            }
        },
        custom_abort_event_border: function (event) {
            // HACK Avoid dropdown disappearing when picking colors
            event.stopPropagation();
        },
        input_select_border: function (event) {
            $(event.target).focus().select();
        },
        custom_abort_event_background: function (event) {
            // HACK Avoid dropdown disappearing when picking colors
            event.stopPropagation();
        },
        input_select_background: function (event) {
            $(event.target).focus().select();
        },
        remove_inline_background_color: function (event) {
            this.media.style.backgroundColor = "";
            if (this.change_border) {
                this.media.style.backgroundColor = "";
            }
            this.$background_custom.trigger("background-color-event", event.type);
        },
        set_inline_background_color: function (event) {
            var color = String(event.color);
            this.media.style.backgroundColor = color;
            if (this.change_border) {
                this.media.style.backgroundColor  = color;
            }
            this.$background_custom.trigger("background-color-event", event.type);
        },
        remove_inline_border_color: function (event) {
            this.media.style.borderColor = "";
            if (this.change_border) {
                this.media.style.borderColor = "";
            }
            this.$border_custom.trigger("background-color-event", event.type);
        },
        set_inline_border_color: function (event) {
            var color = String(event.color);
            this.media.style.borderColor = color;
            if (this.change_border) {
                this.media.style.borderColor  = color;
            }
            this.$border_custom.trigger("background-color-event", event.type);
        },
    });

    var click_event = function (el, type) {
        var evt = document.createEvent("MouseEvents");
        evt.initMouseEvent(type, true, true, window, 0, 0, 0, 0, 0, false, false, false, false, 0, el);
        el.dispatchEvent(evt);
    };

    return {
        position_argument: position_argument,
    }

});
