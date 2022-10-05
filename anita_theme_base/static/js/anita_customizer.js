odoo.define('anita_theme_setting.customizer', function (require) {
    "use strict";

    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');

    var AnitaCustomizer = Widget.extend({
        template: 'anita_theme_base.customizer',
        sequence: 0,

        events: _.extend({}, Widget.prototype.events, {
            "click .customizer-toggle": "_on_toggle_click",
        }),

        _on_toggle_click: function (ev) {
            this.do_action({
                'type': 'ir.actions.act_url',
                'url': 'https://apps.odoo.com/apps/themes/15.0/anita_theme_switcher/',
                'target': 'self'
            })
        }
    });

    SystrayMenu.Items.push(AnitaCustomizer);

    return AnitaCustomizer;
});
