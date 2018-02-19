# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# See LICENSE file for copyright and licensing details.

from odoo.tools.safe_eval import safe_eval

import babel
import copy
import datetime
import dateutil.relativedelta as relativedelta
import logging

from urllib import urlencode, quote as quote

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


def format_date(env, date, pattern=False):
    if not date:
        return ''
    date = datetime.datetime.strptime(date[:10], tools.DEFAULT_SERVER_DATE_FORMAT)
    lang_code = env.context.get('lang') or 'en_US'
    if not pattern:
        lang = env['res.lang']._lang_get(lang_code)
        pattern = lang.date_format
    try:
        locale = babel.Locale.parse(lang_code)
        pattern = tools.posix_to_ldml(pattern, locale=locale)
        return babel.dates.format_date(date, format=pattern, locale=locale)
    except babel.core.UnknownLocaleError:
        return date.strftime(pattern)


try:
    # We use a jinja2 sandboxed environment to render mako templates.
    # Note that the rendering does not cover all the mako syntax, in particular
    # arbitrary Python statements are not accepted, and not all expressions are
    # allowed: only "public" attributes (not starting with '_') of objects may
    # be accessed.
    # This is done on purpose: it prevents incidental or malicious execution of
    # Python code that may break the security of the server.
    from jinja2.sandbox import SandboxedEnvironment
    mako_template_env = SandboxedEnvironment(
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="${",
        variable_end_string="}",
        comment_start_string="<%doc>",
        comment_end_string="</%doc>",
        line_statement_prefix="%",
        line_comment_prefix="##",
        trim_blocks=True,               # do not output newline after blocks
        autoescape=True,                # XML/HTML automatic escaping
    )
    mako_template_env.globals.update({
        'str': str,
        'quote': quote,
        'urlencode': urlencode,
        'datetime': datetime,
        'len': len,
        'abs': abs,
        'min': min,
        'max': max,
        'sum': sum,
        'filter': filter,
        'reduce': reduce,
        'map': map,
        'round': round,
        'cmp': cmp,

        # dateutil.relativedelta is an old-style class and cannot be directly
        # instanciated wihtin a jinja2 expression, so a lambda "proxy" is
        # is needed, apparently.
        'relativedelta': lambda *a, **kw: relativedelta.relativedelta(*a, **kw),
    })
    mako_safe_template_env = copy.copy(mako_template_env)
    mako_safe_template_env.autoescape = False
except ImportError:
    _logger.warning("jinja2 not available, templating features will not work!")


class CardTemplate(models.Model):
    _name = 'card.template'

    @api.depends('card_ids')
    def _get_cards(self):
        self.card_count = len(self.card_ids)

    def _get_card_designer_model(self):
        res = []
        for model_name in self.env:
            model = self.env[model_name]
            if hasattr(model, '_card_designer') and getattr(model, '_card_designer'):
                res.append((model._name, model._card_designer))
        return res

    @api.model
    def _get_default_model(self):
        desiner_models = self._get_card_designer_model()
        if desiner_models and desiner_models[0]:
            return desiner_models[0][0]

    name = fields.Char("Name", required=1)
    body_html = fields.Html(string='Body', sanitize_attributes=False)
    active = fields.Boolean('Active', default=True)
    card_model = fields.Selection(
        selection=_get_card_designer_model, string='Model', required=True,
        default=_get_default_model
    )
    model_id = fields.Many2one('ir.model', string='Model', compute="get_card_model_id")
    state = fields.Selection([('draft', 'Draft'), ('approved', 'Approved')], 'State', default='draft')
    card_ids = fields.One2many('card.card', 'template_id', "Cards")
    card_count = fields.Integer('Count', compute="_get_cards")
    position = fields.Selection([('f', 'Front'), ('b', 'Back')], "Position", default='f')
    default = fields.Boolean('Default')
    ref_ir_act_window_id = fields.Many2one(
        'ir.actions.act_window',
        'Sidebar action',
        readonly=True,
        help="Action to make this "
        "template available on "
        "records of the related "
        "document model."
    )
    ref_ir_value_id = fields.Many2one(
        'ir.values', 'Sidebar button',
        readonly=True,
        help="Sidebar button to open "
        "the sidebar action."
    )

    @api.depends('card_model')
    def get_card_model_id(self):
        self.model_id = self.env['ir.model'].search([('model', '=', self.card_model)], limit=1)

    @api.multi
    def open_cards(self):
        for rec in self:
            domain = [('template_id', '=', rec.id)]
            return {
                'name': "Cards for %s" % (rec.name),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'card.card',
                'domain': domain
            }

    @api.multi
    def open_giftcards(self):
        domain = [('product_id', '=', self.id)]
        view_id = False
        name = False
        if self._context.get('type') == 'gc':
            name = _('Giftcards')
            domain += [('type', 'in', ['f', 'd'])]
            view_id = self.env.ref('ies_sale_coupon.ies_product_coupon_tree_fix').id
        elif self._context.get('type') == 'p':
            name = _('Coupons')
            domain += [('type', '=', 'p')]
            view_id = self.env.ref('ies_sale_coupon.ies_product_coupon_tree_percentage').id

        form_view_id = self.env.ref('ies_sale_coupon.ies_product_coupon_form').id
        return {
            'name': name,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'product.coupon',
            'domain': domain,
            'views': [(view_id, 'tree'), (form_view_id, 'form')]
        }

    @api.multi
    def generate_cards(self):
        for rec in self:
            card_vals = []
            if self.record_domain:
                domain = safe_eval(rec.record_domain)
                model_record_ids = self.env[rec.card_model].search(domain).ids
                for model_record in model_record_ids:
                    model = self.env['ir.model'].search([('model', '=', rec.card_model)])
                    vals = {
                        'model_id': model.id,
                        'record_id': model_record,
                    }
                    card_vals.append((0, 0, vals))
                rec.card_ids = card_vals

    @api.multi
    def create_action(self):
        self.ensure_one()
        vals = {}
        action_obj = self.env['ir.actions.act_window']
        src_obj = self.card_model
        select_name = dict(self._fields['card_model'].selection(self)).get(self.card_model)
        button_name = _('Print Card for %s') % select_name
        action = action_obj.search([('src_model', '=', src_obj), ('name', '=', button_name)], limit=1)
        if len(action):  # if action found than it will not create new action for model
            return True
        vals['ref_ir_act_window_id'] = action_obj.create({
            'name': button_name,
            'type': 'ir.actions.act_window',
            'res_model': 'card.print.wizard',
            'src_model': src_obj,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }).id
        vals['ref_ir_value_id'] = self.env['ir.values'].sudo().create({
            'name': button_name,
            'model': src_obj,
            'key2': 'client_action_multi',
            'value': "ir.actions.act_window," +
                     str(vals['ref_ir_act_window_id']),
        }).id
        self.write(vals)
        return True

    @api.model
    def create(self, vals):
        res = super(CardTemplate, self).create(vals)
        res.create_action()
        return res

    @api.multi
    def unlink_action(self):
        self.mapped('ref_ir_act_window_id').sudo().unlink()
        self.mapped('ref_ir_value_id').sudo().unlink()
        return True

    @api.multi
    def unlink(self):
        self.unlink_action()
        return super(CardTemplate, self).unlink()

    @api.model
    def render_template(self, template_txt, model, res_ids, post_process=False):
        """ Render the given template text, replace mako expressions ``${expr}``
        with the result of evaluating these expressions with an evaluation
        context containing:

         - ``user``: browse_record of the current user
         - ``object``: record of the document record this mail is related to
         - ``context``: the context passed to the mail composition wizard

        :param str template_txt: the template text to render
        :param str model: model name of the document record this mail is related to.
        :param int res_ids: list of ids of document records those mails are related to.
        """
        multi_mode = True
        if isinstance(res_ids, (int, long)):
            multi_mode = False
            res_ids = [res_ids]

        results = dict.fromkeys(res_ids, u"")

        # try to load the template
        try:
            mako_env = mako_safe_template_env if self.env.context.get('safe') else mako_template_env
            template = mako_env.from_string(tools.ustr(template_txt))
        except Exception:
            _logger.info("Failed to load template %r", template_txt, exc_info=True)
            return multi_mode and results or results[res_ids[0]]

        # prepare template variables
        records = self.env[model].browse(filter(None, res_ids))  # filter to avoid browsing [None]
        res_to_rec = dict.fromkeys(res_ids, None)
        for record in records:
            res_to_rec[record.id] = record
        variables = {
            'format_date': lambda date, format=False, context=self._context: format_date(self.env, date, format),
            'user': self.env.user,
            'ctx': self._context,  # context kw would clash with mako internals
        }
        for res_id, record in res_to_rec.iteritems():
            variables['object'] = record
            try:
                render_result = template.render(variables)
            except Exception:
                _logger.info("Failed to render template %r using values %r" % (template, variables), exc_info=True)
                raise UserError(_("Failed to render template %r using values %r") % (template, variables))
            if render_result == u"False":
                render_result = u""
            results[res_id] = render_result

        if post_process:
            for res_id, result in results.iteritems():
                results[res_id] = self.render_post_process(result)

        return multi_mode and results or results[res_ids[0]]


class Card(models.Model):
    _name = 'card.card'

    @api.model
    def _get_sequence(self):
        return self.env['ir.sequence'].next_by_code('card.sequence') or _('New')

    name = fields.Char("Name", required=1, default=_get_sequence)
    model_id = fields.Many2one('ir.model', "Model")
    record_id = fields.Integer('Model Record')
    data = fields.Binary("Card")
    state = fields.Selection([('d', 'Draft'), ('p', 'Printed'), ('rp', 'Reprinted')], 'State', default='d')
    template_id = fields.Many2one('card.template', "Card Template")


class Employee(models.Model):
    _inherit = 'hr.employee'
    _card_designer = _('Employee')
