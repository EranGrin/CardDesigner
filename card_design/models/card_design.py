# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# See LICENSE file for copyright and licensing details.
import babel
import copy
import datetime
import dateutil.relativedelta as relativedelta
from urllib import urlencode, quote as quote
from odoo.tools.safe_eval import safe_eval
from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError
from BeautifulSoup import BeautifulSoup
import os
from os.path import basename
import cssutils
import logging
import base64
from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
_logger = logging.getLogger(__name__)
import re
import cStringIO
from PIL import Image
import zipfile
from base64 import b64encode
from reportlab.lib import units
from reportlab.graphics import renderPM
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.graphics.shapes import Drawing


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


class Irttachment(models.Model):
    _inherit = 'ir.attachment'

    is_select = fields.Boolean("Select For Email")
    card_temp_path = fields.Char("path")

    @api.multi
    def action_send_email(self):
        attachment_list = []
        for rec in self:
            attachment_list.append(rec.id)
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference(
                'card_design', 'email_template_card_design'
            )[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(
                'mail', 'email_compose_message_wizard_form'
            )[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        template = self.env['mail.template'].browse(template_id)
        URL = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        body_html = template.body_html
        soup = BeautifulSoup(body_html)
        for tag in soup.findAll("table", {'id': 'attachment_link'}):
            tag.replaceWith('')
        body_html = str(soup)
        current_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__))
        ).replace('/models', '/static/src/export_files/')
        zip_file_name = 'card_design_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.zip'
        current_path = current_path + 'zip_files/'
        if not os.path.exists(current_path):
            os.makedirs(current_path)
        zip_file = current_path + zip_file_name
        attachment_zipfile = zipfile.ZipFile(zip_file, 'w')
        for attachment in attachment_list:
            attachment = self.env['ir.attachment'].browse(attachment)
            temp_file_name = current_path.split('/card_design')[0] + attachment.card_temp_path
            attachment_zipfile.write(temp_file_name, basename(temp_file_name))
        attachment_zipfile.close()
        base64_datas = open(current_path + zip_file_name, 'rb').read().encode('base64')
        attachment = self.env['ir.attachment'].create({
            'name': zip_file_name,
            'type': 'binary',
            'mimetype': 'application/zip',
            'datas': base64_datas,
            'res_model': 'card.template',
            'res_id': self.ids[0],
            'datas_fname': zip_file_name,
            'card_temp_path': current_path.split('/card_design')[1] + zip_file_name,
            'public': True
        })
        render_html = """ <table id='attachment_link'>
                <tr>
                    <td>
                        <a href='%s/web/content/%s?download=true' data-original-title='%s' title='%s'>%s</a>
                    </td>
                </tr>
                </table>
        """  % (URL, attachment.id, attachment.name, attachment.name, attachment.name)
        body_html += render_html
        template.body_html = body_html
        template.attachment_ids = [(6, 0, [attachment.id])]
        ctx.update({
            'default_model': 'card.template',
            'default_res_id': self.res_id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


class CardTemplate(models.Model):
    _name = 'card.template'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

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

    code = fields.Char("Code")
    name = fields.Char("Name", required=1)
    body_html = fields.Html(string='Body', sanitize_attributes=False)
    back_body_html = fields.Html(string='Back Body', sanitize_attributes=False)
    active = fields.Boolean('Active', default=True)
    card_model = fields.Selection(
        selection=_get_card_designer_model, string='Model', required=True,
        default=_get_default_model
    )
    record_domain = fields.Char(string='Domain', default="[]")
    model_id = fields.Many2one('ir.model', string='Model', compute="get_card_model_id")
    state = fields.Selection([('draft', 'Draft'), ('approved', 'Approved')], 'State', default='draft')
    card_ids = fields.One2many('card.card', 'template_id', "Cards")
    card_count = fields.Integer('Count', compute="_get_cards")
    front_side = fields.Boolean('Front Side', default=True)
    back_side = fields.Boolean('Back Side')
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
    attachment_ids = fields.One2many(
        'ir.attachment', 'res_id', domain=[('res_model', '=', 'card.template'), ('mimetype', '=', 'application/x-pdf')],
        string='Attachments',
        help='Attachments are linked to a document through model / res_id and to the message '
             'through this field.'
    )
    image_attachment_ids = fields.One2many(
        'ir.attachment', 'res_id', domain=[('res_model', '=', 'card.template'), ('mimetype', '=', 'image/png')],
        string='Attachments',
        help='Attachments are linked to a document through model / res_id and to the message '
             'through this field.'
    )
    user_id = fields.Many2one(
        'res.users', string='Responsible',
        default=lambda self: self.env.user
    )
    template_size = fields.Many2one('template.size', 'Template Size')

    @api.multi
    def change_template_size(self):
        for rec in self:
            if rec.body_html and rec.template_size:
                soup = BeautifulSoup(rec.body_html)
                for div in soup.findAll("div", {'class': 'o_mail_no_resize o_designer_wrapper_td oe_structure fixed_heightx'}):
                    if div.get('style', False):
                        style = div.get('style').split(';')
                        style_dict = {}
                        for attr in style:
                            if len(attr.split(":")) > 1:
                                attr_list = attr.split(":")
                                style_dict.update({
                                    attr_list[0].strip(): attr_list[1].strip()
                                })
                        style_dict.update({
                            'height': str(rec.template_size.height) + rec.template_size.size_unit,
                            'width': str(rec.template_size.width) + rec.template_size.size_unit,
                        })
                        div['style'] = " ".join(("{}:{};".format(*i) for i in style_dict.items()))
                    break
                rec.body_html = str(soup)

            if rec.back_body_html and rec.template_size:
                soup = BeautifulSoup(rec.back_body_html)
                for div in soup.findAll("div", {'class': 'o_mail_no_resize o_designer_wrapper_td oe_structure fixed_heightx'}):
                    if div.get('style', False):
                        style = div.get('style').split(';')
                        style_dict = {}
                        for attr in style:
                            if len(attr.split(":")) > 1:
                                attr_list = attr.split(":")
                                style_dict.update({
                                    attr_list[0].strip(): attr_list[1].strip()
                                })
                        style_dict.update({
                            'height': str(rec.template_size.height) + rec.template_size.size_unit,
                            'width': str(rec.template_size.width) + rec.template_size.size_unit,
                        })
                        div['style'] = " ".join(("{}:{};".format(*i) for i in style_dict.items()))
                    break
                rec.back_body_html = str(soup)
        return True

    @api.multi
    def action_selected_card_send_email(self):
        import pdb
        pdb.set_trace()
        context = dict(self.env.context or {})
        if context.get('image', False):
            attachment_ids = self.image_attachment_ids
        else:
            attachment_ids = self.attachment_ids
        attachment_list = []
        if attachment_ids and attachment_ids.filtered(lambda r: r.is_select):
            for rec in attachment_ids.filtered(lambda r: r.is_select):
                attachment_list.append(rec.id)
            ir_model_data = self.env['ir.model.data']
            try:
                template_id = ir_model_data.get_object_reference(
                    'card_design', 'email_template_card_design'
                )[1]
            except ValueError:
                template_id = False
            try:
                compose_form_id = ir_model_data.get_object_reference(
                    'mail', 'email_compose_message_wizard_form'
                )[1]
            except ValueError:
                compose_form_id = False
            ctx = dict()
            template = self.env['mail.template'].browse(template_id)
            URL = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            body_html = template.body_html
            soup = BeautifulSoup(body_html)
            for tag in soup.findAll("table", {'id': 'attachment_link'}):
                tag.replaceWith('')
            body_html = str(soup)
            current_path = os.path.join(os.path.dirname(
                os.path.abspath(__file__))
            ).replace('/models', '/static/src/export_files/')
            current_obj_name = self.name.replace(' ', '_').replace('.', '_').lower() + '_'
            zip_file_name = current_obj_name + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.zip'
            current_path = current_path + 'zip_files/'
            if not os.path.exists(current_path):
                os.makedirs(current_path)
            zip_file = current_path + zip_file_name
            attachment_zipfile = zipfile.ZipFile(zip_file, 'w')
            for attachment in attachment_list:
                attachment = self.env['ir.attachment'].browse(attachment)
                temp_file_name = current_path.split('/card_design')[0] + attachment.card_temp_path
                attachment_zipfile.write(temp_file_name, basename(temp_file_name))
            attachment_zipfile.close()
            base64_datas = open(current_path + zip_file_name, 'rb').read().encode('base64')
            attachment = self.env['ir.attachment'].create({
                'name': zip_file_name,
                'type': 'binary',
                'mimetype': 'application/zip',
                'datas': base64_datas,
                'res_model': 'card.template',
                'res_id': self.ids[0],
                'datas_fname': zip_file_name,
                'card_temp_path': current_path.split('/card_design')[1] + zip_file_name,
                'public': True
            })
            render_html = """ <table id='attachment_link'>
                    <tr>
                        <td>
                            <a href='%s/web/content/%s?download=true' data-original-title='%s' title='%s'>%s</a>
                        </td>
                    </tr>
                    </table>
            """  % (URL, attachment.id, attachment.name, attachment.name, attachment.name)
            body_html += render_html
            template.body_html = body_html
            template.attachment_ids = [(6, 0, [attachment.id])]
            ctx.update({
                'default_model': 'card.template',
                'default_res_id': self.ids[0],
                'default_use_template': bool(template_id),
                'default_template_id': template_id,
                'default_composition_mode': 'comment',
                'mark_so_as_sent': True,
            })
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'views': [(compose_form_id, 'form')],
                'view_id': compose_form_id,
                'target': 'new',
                'context': ctx,
            }
        else:
            raise UserError(_("Please select attachment "))

    @api.multi
    def action_send_email(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference(
                'card_design', 'email_template_card_design'
            )[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(
                'mail', 'email_compose_message_wizard_form'
            )[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        attachment_list = []
        attachment = self.pdf_generate(self.body_html, 'front_side')
        attachment_list.append(attachment.id)
        if self.back_side:
            attachment = self.pdf_generate(self.back_body_html, 'back_side')
            attachment_list.append(attachment.id)
        template = self.env['mail.template'].browse(template_id)
        URL = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        body_html = template.body_html
        soup = BeautifulSoup(body_html)
        for tag in soup.findAll("table", {'id': 'attachment_link'}):
            tag.replaceWith('')
        body_html = str(soup)
        current_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__))
        ).replace('/models', '/static/src/export_files/')
        current_obj_name = self.name.replace(' ', '_').replace('.', '_').lower() + '_'
        zip_file_name = current_obj_name + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + '.zip'
        current_path = current_path + 'zip_files/'
        if not os.path.exists(current_path):
            os.makedirs(current_path)
        zip_file = current_path + zip_file_name
        attachment_zipfile = zipfile.ZipFile(zip_file, 'w')
        for attachment in attachment_list:
            attachment = self.env['ir.attachment'].browse(attachment)
            temp_file_name = current_path.split('/card_design')[0] + attachment.card_temp_path
            attachment_zipfile.write(temp_file_name, basename(temp_file_name))
        attachment_zipfile.close()
        base64_datas = open(current_path + zip_file_name, 'rb').read().encode('base64')
        attachment = self.env['ir.attachment'].create({
            'name': zip_file_name,
            'type': 'binary',
            'mimetype': 'application/zip',
            'datas': base64_datas,
            'res_model': 'card.template',
            'res_id': self.ids[0],
            'datas_fname': zip_file_name,
            'card_temp_path': '/card_design' + current_path.split('/card_design')[1] + zip_file_name,
            'public': True
        })
        render_html = """ <table id='attachment_link'>
                <tr>
                    <td>
                        <a href='%s/web/content/%s?download=true' data-original-title='%s' title='%s'>%s</a>
                    </td>
                </tr>
                </table>
        """  % (URL, attachment.id, attachment.name, attachment.name, attachment.name)
        body_html += render_html

        template.body_html = body_html
        template.attachment_ids = [(6, 0, [attachment.id])]
        ctx.update({
            'default_model': 'card.template',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context':  ctx,
        }

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
    def default_get(self, fields):
        res = super(CardTemplate, self).default_get(fields)
        res['code'] = self.env['ir.sequence'].next_by_code('card.template') or _('New')
        return res

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

    def get_barcode(self, value, width, barWidth=0.05 * units.inch, fontSize=20, humanReadable=True):
        barcode = createBarcodeDrawing(
            'EAN13',
            value=value,
            barWidth=barWidth,
            fontSize=fontSize,
            humanReadable=humanReadable
        )
        drawing_width = width
        barcode_scale = drawing_width / barcode.width
        drawing_height = barcode.height * barcode_scale

        drawing = Drawing(drawing_width, drawing_height)
        drawing.scale(barcode_scale, barcode_scale)
        drawing.add(barcode, name='barcode')
        return drawing

    def get_image(self, value, width, height):
        barcode = self.get_barcode(value=value, width=width)
        data = b64encode(renderPM.drawToString(barcode, fmt='PNG'))
        return "data:image/png;base64,{0}".format(data)

    def get_name(self, value, extension):
        name = value + '_' + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + extension
        return name

    def render_pdf(self, svg_file_name, data, side_name):
        resolution = self.template_size and self.template_size.dpi or 300
        soup = BeautifulSoup(data)
        count = 0
        width = '0px'
        height = '0px'
        path = self.env.ref('card_design.svg_to_pdf').value
        if not path:
            path = '/tmp'
        for div in soup.findAll("div", {'class': 'fixed_height'}):
            count = count + 1
            if count == 1:
                div.attrs = None
            soup = div.extract()
        attr_div = soup.findAll("div")
        if len(attr_div) > 0 and attr_div[0].get('style', False):
            div_style = cssutils.parseStyle(attr_div[0].get('style'))
            del div_style["transform"]
            attr_div[0]['style'] = div_style.cssText
            style = attr_div[0].get('style').split(';')
            style_dict = {}
            for attr in style:
                if len(attr.split(":")) > 1:
                    attr_list = attr.split(":")
                    style_dict.update({
                        attr_list[0].strip(): attr_list[1].strip()
                    })
            if style_dict.get('height', False):
                height = style_dict.get('height').strip()
            if style_dict.get('width', False):
                width = style_dict.get('width').strip()
            if style_dict.get('transform', False):
                del style_dict['transform']
            attr_div[0]['style'] = " ".join(("{}:{};".format(*i) for i in style_dict.items()))
        current_obj_name = self.name.replace(' ', '_').replace('.', '_').lower() + '_'
        for img in soup.findAll('img'):
            is_svg = False
            if 'font_to_img' in img['src']:
                img.attrs = None
            elif '/web/image/' in img['src']:
                attach_id = img['src'].split('/')[-1]
                brow_obj = self.env['ir.attachment'].browse(int(attach_id))
                if 'svg' in brow_obj.mimetype:
                    is_svg = True
                img['src'] = 'data:'+brow_obj.mimetype+';base64,' + brow_obj.datas
            elif 'http' in img['src'] or 'https' in img['src']:
                img['src'] = img['src']
            elif 'report' in img['src']:
                img['src'] = self.get_image(self.code, int(img['width']), int(img['height']))
                is_svg = True
            else:
                current_path = os.path.dirname((os.path.abspath(__file__))).split('/card_design/')[0]
                image_path = os.path.abspath(img['src'])
                full_path = current_path + image_path
                image_file = open(full_path, "rb")
                encoded_string = base64.b64encode(image_file.read())
                img['src'] = 'data:image/png;base64,' + encoded_string
            if not is_svg:
                image_data = re.sub('^data:image/.+;base64,', '', img['src']).decode('base64')
                im = Image.open(cStringIO.StringIO(image_data))
                im.save(path + '/' + current_obj_name + "t.png", dpi=(resolution, resolution))
                with open(path + '/' + current_obj_name + "t.png", "rb") as imageFile:
                    img['src'] = 'data:image/png;base64,' + base64.b64encode(imageFile.read())

        data = str(soup)
        html = HTML(string=data)
        font_config = FontConfiguration()
        style = '''
            @page { size: %s %s ; margin: -6px; overflow: hidden !important;}
            div { overflow: hidden !important; margin-top:-2px;margin-left:-1px;}
        ''' % (width, height)
        css = CSS(string=style, font_config=font_config)
        current_obj_name = self.name.replace(' ', '_').replace('.', '_').lower()
        current_path = os.path.join(os.path.dirname(os.path.abspath(__file__))).replace('/models', '/static/src/export_files/')
        current_date = fields.date.today().strftime('%Y_%m_%d')
        current_path = current_path + current_obj_name + '/' + current_date + '/'
        if not os.path.exists(current_path):
            os.makedirs(current_path)
        html.write_pdf(current_path + svg_file_name, stylesheets=[css], font_config=font_config)
        pages_to_keep = [0]
        infile = PdfFileReader(current_path + svg_file_name, 'rb')
        output = PdfFileWriter()

        for i in range(infile.getNumPages()):
            if i in pages_to_keep:
                p = infile.getPage(i)
                output.addPage(p)

        with open(current_path + svg_file_name, 'wb') as f:
            output.write(f)
        data_file = open(current_path + svg_file_name, 'r')
        temp_file_name = current_path + svg_file_name
        date_file_name = '/card_design' + temp_file_name.split('/card_design')[1]
        datas = data_file.read()
        base64_datas = base64.encodestring(datas)
        return date_file_name, data_file, base64_datas

    def render_png(self, svg_file_name, data, side_name):
        resolution = self.template_size and self.template_size.dpi or 300
        path = self.env.ref('card_design.svg_to_pdf').value
        soup = BeautifulSoup(data)
        count = 0
        width = '0px'
        height = '0px'
        if not path:
            path = '/tmp'
        for div in soup.findAll("div", {'class': 'fixed_height'}):
            count = count + 1
            if count == 1:
                div.attrs = None
            soup = div.extract()
        attr_div = soup.findAll("div")
        if len(attr_div) > 0 and attr_div[0].get('style', False):
            div_style = cssutils.parseStyle(attr_div[0].get('style'))
            del div_style["transform"]
            attr_div[0]['style'] = div_style.cssText
            style = attr_div[0].get('style').split(';')
            style_dict = {}
            for attr in style:
                if len(attr.split(":")) > 1:
                    attr_list = attr.split(":")
                    style_dict.update({
                        attr_list[0].strip(): attr_list[1].strip()
                    })
            if style_dict.get('height', False):
                height = style_dict.get('height').strip()
            if style_dict.get('width', False):
                width = style_dict.get('width').strip()
            if style_dict.get('transform', False):
                del style_dict['transform']
            attr_div[0]['style'] = " ".join(("{}:{};".format(*i) for i in style_dict.items()))
        current_obj_name = self.name.replace(' ', '_').replace('.', '_').lower() + '_'
        for img in soup.findAll('img'):
            is_svg = False
            if 'font_to_img' in img['src']:
                img.attrs = None
            elif '/web/image/' in img['src']:
                attach_id = img['src'].split('/')[-1]
                brow_obj = self.env['ir.attachment'].browse(int(attach_id))
                if 'svg' in brow_obj.mimetype:
                    is_svg = True
                img['src'] = 'data:'+brow_obj.mimetype+';base64,' + brow_obj.datas
            elif 'http' in img['src'] or 'https' in img['src']:
                img['src'] = img['src']
            elif 'report' in img['src']:
                img['src'] = self.get_image(self.code, int(img['width']), int(img['height']))
                is_svg = True
            else:
                current_path = os.path.dirname((os.path.abspath(__file__))).split('/card_design/')[0]
                image_path = os.path.abspath(img['src'])
                full_path = current_path + image_path
                image_file = open(full_path, "rb")
                encoded_string = base64.b64encode(image_file.read())
                img['src'] = 'data:image/png;base64,' + encoded_string
            if not is_svg:
                image_data = re.sub('^data:image/.+;base64,', '', img['src']).decode('base64')
                im = Image.open(cStringIO.StringIO(image_data))
                im.save(path + '/' + current_obj_name + "t.png", dpi=(resolution, resolution))
                with open(path + '/' + current_obj_name + "t.png", "rb") as imageFile:
                    img['src'] = 'data:image/png;base64,' + base64.b64encode(imageFile.read())

        data = str(soup)
        html = HTML(string=data)
        font_config = FontConfiguration()
        style = '''
            @page { size: %s %s ; margin: -8px; overflow: hidden !important;}
            div { overflow: hidden !important;  float: left; width: %s;}
            .pdf_overflow { margin-bottom:-2px;}
        ''' % (width, height, '100%')
        css = CSS(string=style, font_config=font_config)
        current_path = os.path.join(os.path.dirname(os.path.abspath(__file__))).replace('/models', '/static/src/export_files/')
        current_date = fields.date.today().strftime('%Y_%m_%d')
        current_obj_name = self.name.replace(' ', '_').replace('.', '_').lower()
        current_path = current_path + current_obj_name + '/' + current_date + '/'
        if not os.path.exists(current_path):
            os.makedirs(current_path)
        html.write_png(current_path + svg_file_name, stylesheets=[css], font_config=font_config, resolution=resolution)
        im = Image.open(current_path + svg_file_name)
        im.save(current_path + svg_file_name, dpi=(resolution, resolution))
        data_file = open(current_path + svg_file_name, 'r')
        temp_file_name = current_path + svg_file_name
        date_file_name = '/card_design' + temp_file_name.split('/card_design')[1]
        datas = data_file.read()
        base64_datas = base64.encodestring(datas)
        return date_file_name, data_file, base64_datas

    def pdf_generate(self, data, side_name):
        name = self.get_name(side_name, '.pdf')
        path, data_file, base64_datas = self.render_pdf(name, data, side_name)
        attachment_id = self.env['ir.attachment'].create({
            'name': name,
            'type': 'binary',
            'mimetype': 'application/x-pdf',
            'datas': base64_datas,
            'res_model': 'card.template',
            'res_id': self.id,
            'datas_fname': name,
            'card_temp_path': path,
            'public': True
        })
        return attachment_id

    def png_generate(self, data, side_name):
        name = self.get_name(side_name, '.png')
        path, data_file, base64_datas = self.render_png(name, data, side_name)
        attachment_id = self.env['ir.attachment'].create({
            'name': name,
            'type': 'binary',
            'mimetype': 'image/png',
            'datas': base64_datas,
            'res_model': 'card.template',
            'res_id': self.id,
            'datas_fname': name,
            'card_temp_path': path,
            'public': True
        })
        return attachment_id

    @api.multi
    def print_pdf(self, file_name):
        if not file_name:
            file_name = ''
        attachment_id = self.pdf_generate(self.body_html, (file_name + '_front_side'))
        return {
            'type': 'ir.actions.report.xml',
            'report_type': 'controller',
            'report_file': "/web/content/" + str(attachment_id.id) + "?download=true",
        }

    @api.multi
    def print_back_side_pdf(self, file_name):
        if not self.back_side:
            raise UserError(_("please select back side option."))
        if not file_name:
            file_name = ''
        attachment_id = self.pdf_generate(self.back_body_html, (file_name + '_back_side'))
        return {
            'type': 'ir.actions.report.xml',
            'report_type': 'controller',
            'report_file': "/web/content/" + str(attachment_id.id) + "?download=true",
        }

    @api.multi
    def print_png_export(self, file_name):
        if not file_name:
            file_name = ''
        attachment_id = self.png_generate(self.body_html, (file_name + '_front_side'))
        return {
            'type': 'ir.actions.report.xml',
            'report_type': 'controller',
            'report_file': "/web/content/" + str(attachment_id.id) + "?download=true",
        }

    @api.multi
    def print_back_side_png_export(self, file_name):
        if not self.back_side:
            raise UserError(_("please select back side option."))
        if not file_name:
            file_name = ''
        attachment_id = self.png_generate(self.back_body_html, (file_name + '_back_side'))
        return {
            'type': 'ir.actions.report.xml',
            'report_type': 'controller',
            'report_file': "/web/content/" + str(attachment_id.id) + "?download=true",
        }

    @api.multi
    def print_both_side_png_export(self, file_name):
        attachment_list = []
        attachment_id = self.png_generate(self.body_html, (file_name + '_front_side'))
        attachment_list.append(attachment_id.id)
        if self.back_side:
            attachment_id = self.png_generate(self.back_body_html, (file_name + '_back_side'))
            attachment_list.append(attachment_id.id)
        actions = []
        for attachment in attachment_list:
            actions.append({
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s?download=true' % (attachment)
            })
        return {
            'type': 'ir.actions.multi.print',
            'actions': actions,
        }

    def render_pdf_both_side(self, svg_file_name, side_name=''):
        path = self.env.ref('card_design.svg_to_pdf').value
        if not path:
            path = '/tmp'
        pdf_datas = []
        pdfs = []
        attachment_id = self.pdf_generate(self.body_html, 'front_side')
        pdf_datas.append(attachment_id.datas)
        if self.back_side:
            attachment_id = self.pdf_generate(self.back_body_html, 'back_side')
            pdf_datas.append(attachment_id.datas)

        current_obj_name = self.name.replace(' ', '_').replace('.', '_').lower() + '_'
        for inx, data in enumerate(pdf_datas):
            pdf_name = path + '/' + current_obj_name + svg_file_name + str(inx) + '.pdf'
            pdfs.append(pdf_name)
            with open(pdf_name, 'wb') as pdf:
                pdf.write(base64.b64decode(data))

        merger = PdfFileMerger()
        current_path = os.path.join(os.path.dirname(os.path.abspath(__file__))).replace('/models', '/static/src/export_files/')
        current_date = fields.date.today().strftime('%Y_%m_%d')
        current_path = current_path + current_obj_name + '/' + current_date + '/'
        if not os.path.exists(current_path):
            os.makedirs(current_path)
        for pdf_data in pdfs:
            merger.append(open(pdf_data, 'rb'))

        with open(current_path + current_obj_name + svg_file_name + '.pdf', 'wb') as fout:
            merger.write(fout)

        data_file = open(current_path + current_obj_name + svg_file_name + '.pdf', 'r')
        temp_file_name = current_path + current_obj_name + svg_file_name + '.pdf'
        date_file_name = '/card_design' + temp_file_name.split('/card_design')[1]
        datas = data_file.read()
        base64_datas = base64.encodestring(datas)
        return date_file_name, data_file, base64_datas

    @api.multi
    def print_merge_pdf_export(self, file_name):
        name = self.get_name(file_name, '.pdf')
        path, data_file, base64_datas = self.render_pdf_both_side(name, file_name)
        attachment_id = self.env['ir.attachment'].create({
            'name': name,
            'type': 'binary',
            'mimetype': 'application/x-pdf',
            'datas': base64_datas,
            'res_model': 'card.template',
            'res_id': self.id,
            'datas_fname': name,
            'card_temp_path': path,
            'public': True
        })
        return attachment_id

    @api.multi
    def print_both_side_pdf(self, file_name):
        attachment_list = []
        attachment_id = self.pdf_generate(self.body_html, (file_name + '_front_side'))
        attachment_list.append(attachment_id.id)
        if self.back_side:
            attachment_id = self.pdf_generate(self.back_body_html, (file_name + '_back_side'))
            attachment_list.append(attachment_id.id)
        actions = []
        for attachment in attachment_list:
            actions.append({
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s?download=true' % (attachment)
            })
        return {
            'type': 'ir.actions.multi.print',
            'actions': actions,
        }

    @api.multi
    def print_front_side(self):
        context = dict(self.env.context or {})
        context['active_id'] = self.id
        context['front_side'] = True
        return {
            'name': _('enter file name with out extension'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'card.export.wizard',
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new'
        }

    @api.multi
    def print_back_side(self):
        context = dict(self.env.context or {})
        context['active_id'] = self.id
        context['back_side'] = True
        return {
            'name': _('enter file name with out extension'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'card.export.wizard',
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new'
        }

    @api.multi
    def print_both_side(self):
        context = dict(self.env.context or {})
        context['active_id'] = self.id
        context['both_side'] = True
        return {
            'name': _('enter file name with out extension'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'card.export.wizard',
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new'
        }

    @api.multi
    def print_both_side_png(self):
        context = dict(self.env.context or {})
        context['active_id'] = self.id
        context['both_side'] = True
        context['png'] = True
        return {
            'name': _('enter file name with out extension'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'card.export.wizard',
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new'
        }

    @api.multi
    def print_front_side_png(self):
        context = dict(self.env.context or {})
        context['active_id'] = self.id
        context['front_side'] = True
        context['png'] = True
        return {
            'name': _('enter file name with out extension'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'card.export.wizard',
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new'
        }

    @api.multi
    def print_back_side_png(self):
        context = dict(self.env.context or {})
        context['active_id'] = self.id
        context['back_side'] = True
        context['png'] = True
        return {
            'name': _('enter file name with out extension'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'card.export.wizard',
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new'
        }


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


class respartner(models.Model):
    _inherit = 'res.partner'
    _card_designer = _('Partner')
