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
            this.$modal.find('.modal-dialog').css({'right': '0px', 'position': 'fixed', 'width':'250px'})
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
            if (this.media.style) {
                var position_arg = this.$el.find('#position');
                var background_arg = this.$el.find('#pbackground')
                var pptop_arg = this.$el.find('#pptop');
                var ppleft_arg = this.$el.find('#ppleft');
                var ppbottom_arg = this.$el.find('#ppbottom');
                var ppright_arg = this.$el.find('#ppright');
                var zindex_arg = this.$el.find('#zindex');
                var pborder_arg = this.$el.find('#pborder');
                var pbordersize_arg = this.$el.find('#pbordersize');
                var pbordercolor_arg = this.$el.find('#pbordercolor');
                var pborderadius_arg = this.$el.find('#pborderadius');
                var mtop_arg = this.$el.find('#mtop');
                var mleft_arg = this.$el.find('#mleft');
                var mbottom_arg = this.$el.find('#mbottom');
                var mright_arg = this.$el.find('#mright');
                var ptop_arg = this.$el.find('#ptop');
                var pleft_arg = this.$el.find('#pleft');
                var pbottom_arg = this.$el.find('#pbottom');
                var pright_arg = this.$el.find('#pright');
                var overflow_arg = this.$el.find('#overflow');
                var width_arg = this.$el.find('#width');
                var height_arg = this.$el.find('#height');
                var ptborder_arg = this.$el.find('#ptborder');
                var plborder_arg = this.$el.find('#plborder');
                var pbborder_arg = this.$el.find('#pbborder');
                var prborder_arg = this.$el.find('#prborder');
                var mstyle_arg = this.$el.find('#mstyle');
                var pstyle_arg = this.$el.find('#pstyle');
                var sstyle_arg = this.$el.find('#sstyle');
                var pdstyle_arg = this.$el.find('#pdstyle');
                if (width_arg) {
                    if (this.media.style.width) {
                        var demo = this.media.style.width
                        var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                        var style_top = demo.split(value)
                        width_arg.val(value);
                        sstyle_arg.val(style_top[1]);
                    }
                }
                if (height_arg) {
                    if (this.media.style.height) {
                        var demo = this.media.style.height
                        var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                        var style_top = demo.split(value)
                        height_arg.val(value);
                        sstyle_arg.val(style_top[1]);
                    }
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
                if (pbordersize_arg) {
                    if (this.media.style.borderWidth) {
                        pbordersize_arg.val(this.media.style.borderWidth);
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
                if (mtop_arg) {
                    if (this.media.style.marginTop) {
                        var demo = this.media.style.marginTop
                        var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                        var style_top = demo.split(value)
                        mtop_arg.val(value);
                        mstyle_arg.val(style_top[1]);
                    }
                }
                if (mleft_arg) {
                    if (this.media.style.marginLeft) {
                        var demo = this.media.style.marginLeft
                        var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                        var style_top = demo.split(value)
                        mleft_arg.val(value);
                        mstyle_arg.val(style_top[1]);
                    }
                }
                if (mright_arg) {
                    if (this.media.style.marginRight) {
                        var demo = this.media.style.marginRight
                        var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                        var style_top = demo.split(value)
                        mright_arg.val(value);
                        mstyle_arg.val(style_top[1]);
                    }
                }
                if (mbottom_arg) {
                    if (this.media.style.marginBottom) {
                        var demo = this.media.style.marginBottom
                        var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                        var style_top = demo.split(value)
                        mbottom_arg.val(value);
                        mstyle_arg.val(style_top[1]);
                    }
                }
                if (ptop_arg) {
                    if (this.media.style.paddingTop) {
                        var demo = this.media.style.paddingTop
                        var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                        var style_top = demo.split(value)
                        ptop_arg.val(value);
                        pdstyle_arg.val(style_top[1]);
                    }
                }
                if (pleft_arg) {
                    if (this.media.style.paddingLeft) {
                        var demo = this.media.style.paddingLeft
                        var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                        var style_top = demo.split(value)
                        pleft_arg.val(value);
                        pdstyle_arg.val(style_top[1]);
                    }
                }
                if (pright_arg) {
                    if (this.media.style.paddingRight) {
                        var demo = this.media.style.paddingRight
                        var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                        var style_top = demo.split(value)
                        pright_arg.val(value);
                        pdstyle_arg.val(style_top[1]);
                    }
                }
                if (pbottom_arg) {
                    if (this.media.style.paddingBottom) {
                        var demo = this.media.style.paddingBottom
                        var value = parseInt(demo.replace(/[^0-9\.]/g, ''))
                        var style_top = demo.split(value)
                        pbottom_arg.val(value);
                        pdstyle_arg.val(style_top[1]);
                    }
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
            this.$el.on('change', '#pptop, #pstyle', function (e) {
                if (self.media) {
                    self.change_style(e, self, "pstyle", "pptop", "top")
                }
            });
            this.$el.on('change', '#ppleft, #pstyle', function (e) {
                if (self.media) {
                    self.change_style(e, self, "pstyle", "ppleft", "left")
                }
            });
            this.$el.on('change', '#ppbottom, #pstyle', function (e) {
                if (self.media) {
                    self.change_style(e, self, "pstyle", "ppbottom", "bottom")
                }
            });
            this.$el.on('change', '#ppright, #pstyle', function (e) {
                if (self.media) {
                    self.change_style(e, self, "pstyle", "ppright", "right")
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
            this.$el.on('change', '#ptborder', function (e) {
                if (self.media) {
                    if (self.media.style) {
                        if (e.target.value) {
                            self.media.style.borderTop = e.target.value;
                        }
                        else {
                            self.media.style.borderTop = "";
                        }
                    }
                }
            });
            this.$el.on('change', '#plborder', function (e) {
                if (self.media) {
                    if (self.media.style) {
                        if (e.target.value) {
                            self.media.style.borderLeft = e.target.value;
                        }
                        else {
                            self.media.style.borderLeft = "";
                        }
                    }
                }
            });
            this.$el.on('change', '#prborder', function (e) {
                if (self.media) {
                    if (self.media.style) {
                        if (e.target.value) {
                            self.media.style.borderRight = e.target.value;
                        }
                        else {
                            self.media.style.borderRight = "";
                        }
                    }
                }
            });
            this.$el.on('change', '#pbborder', function (e) {
                if (self.media) {
                    if (self.media.style) {
                        if (e.target.value) {
                            self.media.style.borderBottom = e.target.value;
                        }
                        else {
                            self.media.style.borderBottom = "";
                        }
                    }
                }
            });
            this.$el.on('change', '#pbordersize', function (e) {
                if (self.media) {
                    if (self.media.style) {
                        if (e.target.value) {
                            self.media.style.borderWidth = e.target.value + 'px';
                        }
                        else {
                            self.media.style.borderWidth = "";
                        }
                    }
                }
            });
            this.$el.on('change', '#width, #sstyle', function (e) {
                if (self.media) {
                    self.change_style(e, self, "sstyle", "width", "width")
                }
            });
            this.$el.on('change', '#height, #sstyle', function (e) {
                if (self.media) {
                    self.change_style(e, self, "sstyle", "height", "height")
                }
            });
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
            this.$el.on('change', '#mtop, #mstyle', function (e) {
                if (self.media) {
                    self.change_style(e, self, "mstyle", "mtop", "margin-top")
                }
            });
            this.$el.on('change', '#mleft, #mstyle', function (e) {
                if (self.media) {
                    self.change_style(e, self, "mstyle", "mleft", "margin-left")
                }
            });
            this.$el.on('change', '#mright, #mstyle', function (e) {
                if (self.media) {
                    self.change_style(e, self, "mstyle", "mright", "margin-right")
                }
            });
            this.$el.on('change', '#mbottom, #mstyle', function (e) {
                if (self.media) {
                    self.change_style(e, self, "mstyle", "mbottom", "margin-bottom")
                }
            });
            this.$el.on('change', '#ptop, #pdstyle', function (e) {
                if (self.media) {
                    self.change_style(e, self, "pdstyle", "ptop", "padding-top")
                }
            });
            this.$el.on('change', '#pleft, #pdstyle', function (e) {
                if (self.media) {
                    self.change_style(e, self, "pdstyle", "pleft", "padding-left")
                }
            });
            this.$el.on('change', '#pright, #pdstyle', function (e) {
                if (self.media) {
                    self.change_style(e, self, "pdstyle", "pright", "padding-right")
                }
            });
            this.$el.on('change', '#pbottom, #pdstyle', function (e) {
                if (self.media) {
                    self.change_style(e, self, "pdstyle", "pbottom", "padding-bottom")
                }
            });
            return this
        },
        change_style: function (e, self, style_target, value_target, style_name) {
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
                                self.media.style.setProperty(style_name, e.target.value + self.$el.find('#pstyle').val(), null)
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
                                // else{
                                //     self.media.style.setProperty(style_name, 1 + e.target.value, null)
                                // }
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
