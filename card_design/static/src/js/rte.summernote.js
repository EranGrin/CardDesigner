odoo.define('card_design.rte.summernote', function (require) {
'use strict';

    var core = require('web.core');
    var ajax = require('web.ajax');
    var base = require('web_editor.base');
    var widgets = require('web_editor.widget');
    var rte = require('web_editor.rte');
    var card_widgets = require('card_design.widget');

    var QWeb = core.qweb;
    var _t = core._t;

    ajax.jsonRpc('/web/dataset/call', 'call', {
        'model': 'ir.ui.view',
        'method': 'read_template',
        'args': ['card_design.borderpicker', base.get_context()]
    }).done(function (data) {
        QWeb.add_template(data);
    });

    ajax.jsonRpc('/web/dataset/call', 'call', {
        'model': 'ir.ui.view',
        'method': 'read_template',
        'args': ['card_design.bordercolorpicker', base.get_context()]
    }).done(function (data) {
        QWeb.add_template(data);
    });

    ajax.jsonRpc('/web/dataset/call', 'call', {
        'model': 'ir.ui.view',
        'method': 'read_template',
        'args': ['card_design.bordersizepicker', base.get_context()]
    }).done(function (data) {
        QWeb.add_template(data);
    });

    ajax.jsonRpc('/web/dataset/call', 'call', {
        'model': 'ir.ui.view',
        'method': 'read_template',
        'args': ['card_design.borderradiuspicker', base.get_context()]
    }).done(function (data) {
        QWeb.add_template(data);
    });

    var dom = $.summernote.core.dom;
    var range = $.summernote.core.range;
    var eventHandler = $.summernote.eventHandler;
    var renderer = $.summernote.renderer;

    var tplButton = renderer.getTemplate().button;
    var tplIconButton = renderer.getTemplate().iconButton;
    var tplDropdown = renderer.getTemplate().dropdown;

    var fn_createPalette = renderer.createPalette;
    renderer.createPalette = function ($container, options) {
        fn_createPalette.call(this, $container, options);

        if (!QWeb.has_template('web_editor.colorpicker')) {
            return;
        }

        if (!QWeb.has_template('card_design.borderpicker')) {
            return;
        }

        if (!QWeb.has_template('card_design.bordersizepicker')) {
            return;
        }

        if (!QWeb.has_template('card_design.borderradiuspicker')) {
            return;
        }

        if (!QWeb.has_template('web_editor.bordercolorpicker')) {
            return;
        }

        var $clpicker = $(QWeb.render('web_editor.colorpicker'));
        var $bdpicker = $(QWeb.render('card_design.borderpicker'));
        var $bdspicker = $(QWeb.render('card_design.bordersizepicker'));
        var $bclpicker = $(QWeb.render('web_editor.bordercolorpicker'));
        var $bdrpicker = $(QWeb.render('card_design.borderradiuspicker'));

        var groups;
        if ($clpicker.is("colorpicker")) {
            groups = _.map($clpicker.children(), function (el) {
                return $(el).find("button").empty();
            });
        } else {
            groups = [$clpicker.find("button").empty()];
        }

        var bclgroups;
        if ($bclpicker.is("bordercolorpicker")) {
            bclgroups = _.map($bclpicker.children(), function (el) {
                return $(el).find("button").empty();
            });
        } else {
            bclgroups = [$bclpicker.find("button").empty()];
        }

        var bdgroups;
        if ($bdpicker.is("borderpicker")) {
            bdgroups = _.map($bdpicker.children(), function (el) {
                return $(el).find("button").empty();
            });
        } else {
            bdgroups = [$bdpicker.find("button").empty()];
        }

        var bdsgroups;
        if ($bdspicker.is("bordersizepicker")) {
            bdsgroups = _.map($bdspicker.children(), function (el) {
                return $(el).find("button").empty();
            });
        } else {
            bdsgroups = [$bdspicker.find("button").empty()];
        }

        var bdrgroups;
        if ($bdrpicker.is("borderradiuspicker")) {
            bdrgroups = _.map($bdrpicker.children(), function (el) {
                return $(el).find("button").empty();
            });
        } else {
            bdrgroups = [$bdrpicker.find("button").empty()];
        }

        var html = "<h6>" + _t("Theme colors") + "</h6>" + _.map(groups, function ($group) {
            var $row = $("<div/>", {"class": "note-color-row mb8"}).append($group);
            var $after_breaks = $row.find(".o_small + :not(.o_small)");
            if ($after_breaks.length === 0) {
                $after_breaks = $row.find(":nth-child(8n+9)");
            }
            $after_breaks.addClass("o_clear");
            return $row[0].outerHTML;
        }).join("") + "<h6>" + _t("Common colors") + "</h6>";

        var bclhtml = "<h6>" + _t("Theme colors") + "</h6>" + _.map(bclgroups, function ($group) {
            var $bclrow = $("<div/>", {"class": "note-color-row mb8"}).append($group);
            var $bclafter_breaks = $bclrow.find(".o_small + :not(.o_small)");
            if ($bclafter_breaks.length === 0) {
                $bclafter_breaks = $bclrow.find(":nth-child(8n+9)");
            }
            $bclafter_breaks.addClass("o_clear");
            return $bclrow[0].outerHTML;
        }).join("") + "<h6>" + _t("Common colors") + "</h6>";

        var bdhtml = "<h6>" + _t("Theme Border") + "</h6>" + _.map(bdgroups, function ($bdgroup) {
            var $bdrow = $("<div/>", {"class": "note-border-row mb8"}).append($bdgroup);
            var $bdafter_breaks = $bdrow.find(".o_small + :not(.o_small)");
            if ($bdafter_breaks.length === 0) {
                $bdafter_breaks = $bdrow.find(":nth-child(8n+9)");
            }
            $bdafter_breaks.addClass("o_clear");
            return $bdrow[0].outerHTML;
        }).join("") + "<h6>" + _t("Common Borders") + "</h6>";

        var bdshtml = "<h6>" + _t("Theme Size Class") + "</h6>" + _.map(bdsgroups, function ($bdsgroup) {
            var $bdsrow = $("<div/>", {"class": "note-border-row mb8"}).append($bdsgroup);
            var $bdsafter_breaks = $bdsrow.find(".o_small + :not(.o_small)");
            if ($bdsafter_breaks.length === 0) {
                $bdsafter_breaks = $bdsrow.find(":nth-child(8n+9)");
            }
            $bdsafter_breaks.addClass("o_clear");
            return $bdsrow[0].outerHTML;
        }).join("") + "<h6>" + _t("Common Borders") + "</h6>";

        var bdrhtml = "<h6>" + _t("Theme Radius Class") + "</h6>" + _.map(bdrgroups, function ($bdrgroup) {
            var $bdrrow = $("<div/>", {"class": "note-border-row mb8"}).append($bdrgroup);
            var $bdrafter_breaks = $bdrrow.find(".o_small + :not(.o_small)");
            if ($bdrafter_breaks.length === 0) {
                $bdrafter_breaks = $bdrrow.find(":nth-child(8n+9)");
            }
            $bdrafter_breaks.addClass("o_clear");
            return $bdrrow[0].outerHTML;
        }).join("") + "<h6>" + _t("Common Borders Raidus") + "</h6>";

        var $palettes = $container.find(".note-color .note-color-palette");
        $palettes.prepend(html);

        var $bclpalettes = $container.find(".note-color .note-color-palette");
        $bclpalettes.prepend(html);

        var $bdpalettes = $container.find(".note-border .note-border-palette");
        $bdpalettes.prepend(bdhtml);

        var $bdspalettes = $container.find(".note-border .note-border-palette");
        $bdspalettes.prepend(bdshtml);

        var $bdrpalettes = $container.find(".note-border .note-border-palette");
        $bdrpalettes.prepend(bdrhtml);

        var $bdbg = $bdpalettes.first().find("button:not(.note-border-btn)").addClass("note-border-btn");
        var $bdfore = $bdpalettes.last().find("button:not(.note-border-btn)").addClass("note-border-btn");
        var $bg = $palettes.first().find("button:not(.note-color-btn)").addClass("note-color-btn");
        var $fore = $palettes.last().find("button:not(.note-color-btn)").addClass("note-color-btn");
        var $bdsbg = $bdspalettes.first().find("button:not(.note-border-btn)").addClass("note-border-btn");
        var $bdsfore = $bdspalettes.last().find("button:not(.note-border-btn)").addClass("note-border-btn");
        var $bclbg = $bclpalettes.first().find("button:not(.note-color-btn)").addClass("note-color-btn");
        var $bclfore = $bclpalettes.last().find("button:not(.note-color-btn)").addClass("note-color-btn");
        var $bdrbg = $bdrpalettes.first().find("button:not(.note-border-btn)").addClass("note-border-btn");
        var $bdrfore = $bdrpalettes.last().find("button:not(.note-border-btn)").addClass("note-border-btn");

        $bg.each(function () {
            var $el = $(this);
            var className = 'bg-' + $el.data('color');
            $el.attr('data-event', 'backColor').attr('data-value', className).addClass(className);
        });
        $fore.each(function () {
            var $el = $(this);
            var className = 'text-' + $el.data('color');
            $el.attr('data-event', 'foreColor').attr('data-value', className).addClass('bg-' + $el.data('color'));
        });
        $bclbg.each(function () {
            var $bclel = $(this);
            var bclclassName = 'bg-' + $bclel.data('border-color');
            $bclel.attr('data-event', 'backColor').attr('data-value', bclclassName).addClass(bclclassName);
        });
        $bclfore.each(function () {
            var $bclel = $(this);
            var bclclassName = 'text-' + $el.data('border-color');
            $bclel.attr('data-event', 'foreColor').attr('data-value', bclclassName).addClass('bg-' + $bclel.data('border-color'));
        });
        $bdbg.each(function () {
            var $bdel = $(this);
            var bdclassName = 'bg-' + $bdel.data('border');
            $bdel.attr('data-event', 'backBorder').attr('data-value', bdclassName).addClass(bdclassName);
        });
        $bdfore.each(function () {
            var $bdel = $(this);
            var bdclassName = 'text-' + $bdel.data('border');
            $bdel.attr('data-event', 'foreBorder').attr('data-value', bdclassName).addClass('bg-' + $bdel.data('border'));
        });
        $bdsbg.each(function () {
            var $bdsel = $(this);
            var bdsclassName = 'bg-' + $bdsel.data('border-width');
            $bdsel.attr('data-event', 'backBorder').attr('data-value', bdsclassName).addClass(bdsclassName);
        });
        $bdsfore.each(function () {
            var $bdsel = $(this);
            var bdsclassName = 'text-' + $bdsel.data('border-width');
            $bdsel.attr('data-event', 'foreBorder').attr('data-value', bdsclassName).addClass('bg-' + $bdsel.data('border-width'));
        });
        $bdrbg.each(function () {
            var $bdrel = $(this);
            var bdrclassName = 'bg-' + $bdrel.data('border-radius');
            $bdrel.attr('data-event', 'backBorder').attr('data-value', bdrclassName).addClass(bdrclassName);
        });
        $bdrfore.each(function () {
            var $bdrel = $(this);
            var bdrclassName = 'text-' + $bdrel.data('border-radius');
            $bdrel.attr('data-event', 'foreBorder').attr('data-value', bdrclassName).addClass('bg-' + $bdrel.data('border-radius'));
        });
    };

    var fn_boutton_update = eventHandler.modules.popover.button.update;
    eventHandler.modules.popover.button.update = function ($container, oStyle) {
        var previous = $(".note-control-selection").data('target');
        if (previous) {
            $(previous).css({"-webkit-animation-play-state": "", "animation-play-state": "", "-webkit-transition": "", "transition": "", "-webkit-animation": "", "animation": ""});
        }

        fn_boutton_update.call(this, $container, oStyle);
        $container.find('.note-color').removeClass("hidden");

        if (oStyle.image) {
            $container.find('[data-event]').parent().removeClass("active");
            $container.find('a[data-event="position"][data-value="static"]').parent().toggleClass("active", $(oStyle.image).hasClass("position-static"));
            $container.find('a[data-event="position"][data-value="relative"]').parent().toggleClass("active", $(oStyle.image).hasClass("position-relative"));
            $container.find('a[data-event="position"][data-value="fixed"]').parent().toggleClass("active", $(oStyle.image).hasClass("position-fixed"));
            $container.find('a[data-event="position"][data-value="absolute"]').parent().toggleClass("active", $(oStyle.image).hasClass("position-absolute"));
            $container.find('a[data-event="position"][data-value="static"]').parent().toggleClass("active", !$container.find('.active a[data-event="position"]').length);

            $(oStyle.image).trigger('attributes_change');
        }
    };

    var fn_tplPopovers = renderer.tplPopovers;
    renderer.tplPopovers = function (lang, options) {
        var $popover = $(fn_tplPopovers.call(this, lang, options));
        var $imagePopover = $popover.find('.note-image-popover');
        var $linkPopover = $popover.find('.note-link-popover');
        var $airPopover = $popover.find('.note-air-popover');

        if (window === window.top) {
            $popover.children().addClass("hidden-xs");
        }

        var $position = $('<div class="btn-group"/>');
        $position.insertBefore($imagePopover.find('.btn-group:first'));
        // var dropdown_content = [
        //     '<li><a data-event="position" href="#" data-value="static">'+_t('Static')+'</a></li>',
        //     '<li><a data-event="position" href="#" data-value="relative">'+_t('Relative')+'</a></li>',
        //     '<li><a data-event="position" href="#" data-value="fixed">'+_t('Fixed')+'</a></li>',
        //     '<li><a data-event="position" href="#" data-value="absolute">'+_t('Absolute')+'</a></li>',
        // ];
        // $(tplIconButton('fa fa-square-o', {
        //     title: _t('Position'),
        //     dropdown: tplDropdown(dropdown_content)
        // })).appendTo($position);

        $position.appendTo($imagePopover.find('.btn-group:first'));
        $position.append('<button class="btn btn-default btn-sm btn-small" data-event="position_argument"><strong>' + _t('Style') + ' </strong></button>');

        return $popover;
    };

    function getImgTarget ($editable) {
        var $handle = $editable ? dom.makeLayoutInfo($editable).handle() : undefined;
        return $(".note-control-selection", $handle).data('target');
    }

    eventHandler.modules.editor.position = function ($editable, sValue) {
        var $target = $(getImgTarget($editable));
        var positions = "static relative fixed absolute".split(/\s+/);
        $editable.data('NoteHistory').recordUndo();
        if (sValue !== undefined)
        {
            if (sValue.length) {
                positions.splice(positions.indexOf(sValue),1);
                $target.toggleClass('position-'+sValue);
            }
            $target.removeClass("position-" + positions.join(" position-"));
        }
    };

    $.summernote.pluginEvents.position_argument = function (event, editor, layoutInfo, sorted) {
        var $editable = layoutInfo.editable();
        var $selection = layoutInfo.handle().find('.note-control-selection');
        var media = $selection.data('target');
        var parent_node  = media.parentNode;
        if (parent_node.parentNode.nodeName != 'DIV'){
            var tmp_parent_node = $.parseHTML("<div>" + parent_node.outerHTML + "</div>")[0];
            parent_node.replaceWith(tmp_parent_node)
            parent_node = tmp_parent_node;
        }
        else {
            parent_node = media.parentNode.parentNode;
        }
        new card_widgets.position_argument(null, {}, $editable, parent_node).open();
    };

});
