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

                if (width_arg) {
                    if (this.media.style.width) {
                        width_arg.val(this.media.style.width);
                    }
                }
                if (height_arg) {
                    if (this.media.style.height) {
                        height_arg.val(this.media.style.height);
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
                        pptop_arg.val(parseInt(this.media.style.top.split('px')[0]));
                    }
                }
                if (ppleft_arg) {
                    if (this.media.style.left) {
                        ppleft_arg.val(parseInt(this.media.style.left.split('px')[0]));
                    }
                }
                if (ppbottom_arg) {
                    if (this.media.style.bottom) {
                        ppbottom_arg.val(parseInt(this.media.style.bottom.split('px')[0]));
                    }
                }
                if (ppright_arg) {
                    if (this.media.style.right) {
                        ppright_arg.val(parseInt(this.media.style.right.split('px')[0]));
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
                        pbordersize_arg.val(parseInt(this.media.style.borderWidth.split('px')[0]));
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
                        mtop_arg.val(parseInt(this.media.style.marginTop.split('px')[0]));
                    }
                }
                if (mleft_arg) {
                    if (this.media.style.marginLeft) {
                        mleft_arg.val(parseInt(this.media.style.marginLeft.split('px')[0]));
                    }
                }
                if (mright_arg) {
                    if (this.media.style.marginRight) {
                        mright_arg.val(parseInt(this.media.style.marginRight.split('px')[0]));
                    }
                }
                if (mbottom_arg) {
                    if (this.media.style.marginBottom) {
                        mbottom_arg.val(parseInt(this.media.style.marginBottom.split('px')[0]));
                    }
                }
                if (ptop_arg) {
                    if (this.media.style.paddingTop) {
                        ptop_arg.val(parseInt(this.media.style.paddingTop.split('px')[0]));
                    }
                }
                if (pleft_arg) {
                    if (this.media.style.paddingLeft) {
                        pleft_arg.val(parseInt(this.media.style.paddingLeft.split('px')[0]));
                    }
                }
                if (pright_arg) {
                    if (this.media.style.paddingRight) {
                        pright_arg.val(parseInt(this.media.style.paddingRight.split('px')[0]));
                    }
                }
                if (pbottom_arg) {
                    if (this.media.style.paddingBottom) {
                        pbottom_arg.val(parseInt(this.media.style.paddingBottom.split('px')[0]));
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
            this.$el.on('change', '#pptop', function (e) {
                if (self.media) {
                    if (self.media.style) {
                        if (e.target.value) {
                            self.media.style.top = e.target.value + 'px';
                        }
                        else {
                            self.media.style.top = "";
                        }
                    }
                }
            });
            this.$el.on('change', '#ppleft', function (e) {
                if (self.media) {
                    if (self.media.style) {
                        if (e.target.value) {
                            self.media.style.left = e.target.value + 'px';
                        }
                        else {
                            self.media.style.left = "";
                        }
                    }
                }
            });
            this.$el.on('change', '#ppbottom', function (e) {
                if (self.media) {
                    if (self.media.style) {
                        if (e.target.value) {
                            self.media.style.bottom = e.target.value + 'px';
                        }
                        else {
                            self.media.style.bottom = "";
                        }
                    }
                }
            });
            this.$el.on('change', '#ppright', function (e) {
                if (self.media) {
                    if (self.media.style) {
                        if (e.target.value) {
                            self.media.style.right = e.target.value + 'px';
                        }
                        else {
                            self.media.style.right = "";
                        }
                    }
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
            this.$el.on('change', '#width', function (e) {
                if (self.media) {
                    if (self.media.style) {
                        if (e.target.value) {
                            self.media.style.width = e.target.value + 'px';
                        }
                        else {
                            self.media.style.width = "";
                        }
                    }
                }
            });
            this.$el.on('change', '#height', function (e) {
                if (self.media) {
                    if (self.media.style) {
                        if (e.target.value) {
                            self.media.style.height = e.target.value + 'px';
                        }
                        else {
                            self.media.style.height = "";
                        }
                    }
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
            this.$el.on('change', '#mtop', function (e) {
                if (self.media) {
                    if (self.media.style) {
                        if (e.target.value) {
                            self.media.style.marginTop = e.target.value + 'px';
                        }
                        else {
                            self.media.style.marginTop = "";
                        }
                    }
                }
            });
            this.$el.on('change', '#mleft', function (e) {
                if (self.media) {
                    if (self.media.style) {
                        if (e.target.value) {
                            self.media.style.marginLeft = e.target.value + 'px';
                        }
                        else {
                            self.media.style.marginLeft = "";
                        }
                    }
                }
            });
            this.$el.on('change', '#mright', function (e) {
                if (self.media) {
                    if (self.media.style) {
                        if (e.target.value) {
                            self.media.style.marginRight = e.target.value + 'px';
                        }
                        else {
                            self.media.style.marginRight = "";
                        }
                    }
                }
            });
            this.$el.on('change', '#mbottom', function (e) {
                if (self.media) {
                    if (self.media.style) {
                        if (e.target.value) {
                            self.media.style.marginBottom = e.target.value + 'px';
                        }
                        else {
                            self.media.style.marginBottom = "";
                        }
                    }
                }
            });
            this.$el.on('change', '#ptop', function (e) {
                if (self.media) {
                    if (self.media.style) {
                        if (e.target.value) {
                            self.media.style.paddingTop = e.target.value + 'px';
                        }
                        else {
                            self.media.style.paddingTop = "";
                        }
                    }
                }
            });
            this.$el.on('change', '#pleft', function (e) {
                if (self.media) {
                    if (self.media.style) {
                        if (e.target.value) {
                            self.media.style.paddingLeft = e.target.value + 'px';
                        }
                        else {
                            self.media.style.paddingLeft = "";
                        }
                    }
                }
            });
            this.$el.on('change', '#pright', function (e) {
                if (self.media) {
                    if (self.media.style) {
                        if (e.target.value) {
                            self.media.style.paddingRight = e.target.value + 'px';
                        }
                        else {
                            self.media.style.paddingRight = "";
                        }
                    }
                }
            });
            this.$el.on('change', '#pbottom', function (e) {
                if (self.media) {
                    if (self.media.style) {
                        if (e.target.value) {
                            self.media.style.paddingBottom = e.target.value + 'px';
                        }
                        else {
                            self.media.style.paddingBottom = "";
                        }
                    }
                }
            });
            return this
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
