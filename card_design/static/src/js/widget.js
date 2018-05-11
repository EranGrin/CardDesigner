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
            this.alt = ($(this.media).attr('alt') || "").replace(/&quot;/g, '"');
            this.title = ($(this.media).attr('title') || "").replace(/&quot;/g, '"');
            this.$modal.css({'display': 'block'})
            this.$modal.find('.modal-dialog').css({
                'right': '0px',
                'position': 'fixed',
                'width':'380px',
                'height': '100%',
                'overflow-y': 'auto'
            })
            this.$modal.find('.modal-footer > button').css({'display': 'none'});
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
                var position_arg = this.$el.find('#position');
                var background_arg = this.$el.find('#pbackground')
                var zindex_arg = this.$el.find('#zindex');
                var pborder_arg = this.$el.find('#pborder');
                var pbordersize_arg = this.$el.find('#pbordersize');
                var pbordercolor_arg = this.$el.find('#pbordercolor');
                var pborderadius_arg = this.$el.find('#pborderadius');
                var overflow_arg = this.$el.find('#overflow');
                var pptop_arg = this.$el.find('#top');
                var ppleft_arg = this.$el.find('#left');
                var ppright_arg = this.$el.find('#right');
                var ppbottom_arg = this.$el.find('#bottom');
                var pstyle_arg = this.$el.find('#pstyle');
                var ptborder_arg = this.$el.find('#ptborder');
                var plborder_arg = this.$el.find('#plborder');
                var pbborder_arg = this.$el.find('#pbborder');
                var prborder_arg = this.$el.find('#prborder');
                if (pptop_arg) {
                    if (this.media.style.top) {
                        var demo = this.media.style.top
                        var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                        var style_top = demo.split(value)
                        pptop_arg.val(value);
                        pstyle_arg.val(style_top[1]);
                    }
                }
                if (ppleft_arg) {
                    if (this.media.style.left) {
                        var demo = this.media.style.left
                        var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                        var style_top = demo.split(value)
                        ppleft_arg.val(value);
                        pstyle_arg.val(style_top[1]);
                    }
                }
                if (ppbottom_arg) {
                    if (this.media.style.bottom) {
                        var demo = this.media.style.bottom
                        var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                        var style_top = demo.split(value)
                        ppbottom_arg.val(value);
                        pstyle_arg.val(style_top[1]);
                    }
                }
                if (ppright_arg) {
                    if (this.media.style.right) {
                        var demo = this.media.style.right
                        var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                        var style_top = demo.split(value)
                        ppright_arg.val(value);
                        pstyle_arg.val(style_top[1]);
                    }
                }
                if (this.media.style.borderBottomWidth) {
                    var demo = this.media.style.borderBottomWidth
                    var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                    var style_top = demo.split(value)
                    initialValues.borders.borderBottomWidth = value + style_top[1];
                }
                if (this.media.style.borderTopWidth) {
                    var demo = this.media.style.borderTopWidth
                    var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                    var style_top = demo.split(value)
                    initialValues.borders.borderTopWidth = value + style_top[1];
                }
                if (this.media.style.borderRightWidth) {
                    var demo = this.media.style.borderRightWidth
                    var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                    var style_top = demo.split(value)
                    initialValues.borders.borderRightWidth = value + style_top[1];
                }
                if (this.media.style.borderLeftWidth) {
                    var demo = this.media.style.borderLeftWidth
                    var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                    var style_top = demo.split(value)
                    initialValues.borders.borderLeftWidth = value + style_top[1];
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
                if (background_arg) {
                    if (this.media.style.backgroundColor) {
                        background_arg.val(this.media.style.backgroundColor);
                    }
                }
                if (overflow_arg) {
                    if (this.media.style.overflow) {
                        overflow_arg.val(this.media.style.overflow);
                    }
                }
                if (position_arg) {
                    if (this.media.style.position) {
                        position_arg.val(this.media.style.position);
                    }
                }
                if (this.media.style.top) {
                    var demo = this.media.style.top
                    var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                    var style_top = demo.split(value)
                    pptop_arg.val(value);
                    pstyle_arg.val(style_top[1]);
                }
                if (this.media.style.left) {
                    var demo = this.media.style.left
                    var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                    var style_top = demo.split(value)
                    ppleft_arg.val(value);
                    pstyle_arg.val(style_top[1]);
                }
                if (this.media.style.bottom) {
                    var demo = this.media.style.bottom
                    var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                    var style_top = demo.split(value)
                    ppbottom_arg.val(value);
                    pstyle_arg.val(style_top[1]);
                }
                if (this.media.style.right) {
                    var demo = this.media.style.right
                    var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                    var style_top = demo.split(value)
                    ppright_arg.val(value);
                    pstyle_arg.val(style_top[1]);
                }
                if (zindex_arg) {
                    if (this.media.style.zIndex) {
                        zindex_arg.val(parseInt(this.media.style.zIndex));
                    }
                }
                if (pborder_arg) {
                    if (this.media.style.borderStyle) {
                        pborder_arg.val(this.media.style.borderStyle);
                    }
                }
                if (ptborder_arg) {
                    if (this.media.style.borderTop) {
                        ptborder_arg.val(this.media.style.borderTop);
                    }
                }
                if (plborder_arg) {
                    if (this.media.style.borderLeft) {
                        plborder_arg.val(this.media.style.borderLeft);
                    }
                }
                if (pbborder_arg) {
                    if (this.media.style.borderBottom) {
                        pbborder_arg.val(this.media.style.borderBottom);
                    }
                }
                if (prborder_arg) {
                    if (this.media.style.borderRight) {
                        prborder_arg.val(this.media.style.borderRight);
                    }
                }
                if (pbordercolor_arg) {
                    if (this.media.style.borderColor) {
                        pbordercolor_arg.val(this.media.style.borderColor);
                    }
                }
                if (pborderadius_arg) {
                    if (this.media.style.borderRadius) {
                        pborderadius_arg.val(parseInt(this.media.style.borderRadius.split('px')[0]));
                    }
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
            }
            this.$el.on('change', '#overflow', function (e) {
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
            this.$el.on('change', '#position', function (e) {
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
            this.$el.on('change', '#top, #pstyle', function (e) {
                if (self.media) {
                    self.change_style(e, self, "pstyle", "top", "top", '#pstyle')
                }
            });
            this.$el.on('change', '#left, #pstyle', function (e) {
                if (self.media) {
                    self.change_style(e, self, "pstyle", "left", "left", '#pstyle')
                }
            });
            this.$el.on('change', '#right, #pstyle', function (e) {
                if (self.media) {
                    self.change_style(e, self, "pstyle", "right", "right", '#pstyle')
                }
            });
            this.$el.on('change', '#bottom, #pstyle', function (e) {
                if (self.media) {
                    self.change_style(e, self, "pstyle", "bottom", "bottom", '#pstyle')
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
            // this.$el.on('change', '#width, #sstyle', function (e) {
            //     if (self.media) {
            //         self.change_style(e, self, "sstyle", "width", "width", '#sstyle')
            //     }
            // });
            // this.$el.on('change', '#height, #sstyle', function (e) {
            //     if (self.media) {
            //         self.change_style(e, self, "sstyle", "height", "height", '#sstyle')
            //     }
            // });
            this.$background_custom = this.$el.find('#pbackground');
            this.$el.find('#pbackground').colorpicker()
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
            this.$border_custom = this.$el.find('#pbordercolor');
            this.$el.find('#pbordercolor').colorpicker()
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
