# -*- coding: utf-8 -*-
# Part of Inceptus ERP Solutions Pvt.ltd.
# Part of LICENSE file for copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)
from odoo import models, fields, _, api


class PrinterLines(models.Model):
    _name = 'printer.lines'

    name = fields.Char(
        string=_("Name"),
        required=True,
    )
    printer_id = fields.Many2one(
        "printer.printer",
        string=_("Printer"),
        required=True,
    )
    default_printer = fields.Boolean(
        string=_('Default Printer')
    )

    @api.multi
    def set_default_printer(self):
        for rec in self:
            get_default_printer_id = self.search([
                ('default_printer', '=', True)
            ])
            if get_default_printer_id:
                get_default_printer_id.default_printer = False
            rec.default_printer = True

    # @api.multi
    # def test_print_data(self):
    #     self.ensure_one()
    #     for rec in self:
    #         printer = rec.printer_id
    #         printer_name = rec.name
    #         printer_config_dict = {
    #             "host": printer.host,
    #             "port": {
    #                 "secure": [int(secure_port) for secure_port in printer.secure_port.split(",")],
    #                 "insecure": [int(secure_port) for secure_port in printer.secure_port.split(",")],
    #             },
    #             'use_secure': printer.using_secure,
    #             "keep_alive": printer.keep_alive,
    #             "retries": printer.retries,
    #             "delay": printer.delay,
    #         }
    #         return {
    #             "type": "ir.actions.print.data",
    #             "res_model": self._name,
    #             "res_id": rec.id,
    #             "printer_name": printer_name,
    #             "file_path": "/card_design_printer/static/src/file/test_card.pdf",
    #             "printer_config_dict": printer_config_dict,
    #             "context": self.env.context,
    #         }


class Printer(models.Model):
    _name = 'printer.printer'

    @api.multi
    @api.depends('line_ids', 'line_ids.default_printer')
    def _get_default_printer(self):
        for rec in self:
            default_printer_id = rec.line_ids.filtered(
                lambda r: r.default_printer
            )
            if default_printer_id:
                rec.default_printer = default_printer_id.id

    name = fields.Char(
        string=_("Name"),
        required=True
    )
    host = fields.Char(
        string=_("Host"),
        required=True,
        default="localhost"
    )
    secure_port = fields.Char(
        string=_("Secure Port"),
        required=True,
        default="8181, 8282, 8383, 8484"
    )
    insecure_port = fields.Char(
        string=_("Insecure Port"),
        required=True,
        default="8182, 8283, 8384, 8485"
    )
    using_secure = fields.Boolean(
        string=_("usingSecure"),
        default=True
    )
    keep_alive = fields.Integer(
        string=_("KeepAlive"),
        required=True,
        default=60
    )
    retries = fields.Integer(
        string=_("Retries"),
        required=True,
        default=0
    )
    delay = fields.Integer(
        string=_("Delay"),
        required=True,
        default=0
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'connected')
    ], string=_('State'), default='draft')
    line_ids = fields.One2many(
        "printer.lines",
        "printer_id",
        string=_("Printer List")
    )
    error = fields.Char(string=_("Error"))
    is_error = fields.Boolean(string=_("IS Error"))
    active_msg = fields.Char(string=_("Active Message"))
    is_active = fields.Boolean(string=_("IS Active"))
    default_printer = fields.Many2one(
        "printer.lines",
        string=_("Default Printer"),
        compute="_get_default_printer",
        store=True
    )

    @api.multi
    def reset_connection(self):
        self.write({
            'state': 'draft',
            'error': '',
            'is_error': False,
            'active_msg': '',
            'is_active': ''
        })
        return True

    @api.multi
    def check_connection(self):
        self.ensure_one()
        for rec in self:
            printer_config_dict = {
                "host": rec.host,
                "port": {
                    "secure": [int(secure_port) for secure_port in rec.secure_port.split(",")],
                    "insecure": [int(secure_port) for secure_port in rec.secure_port.split(",")],
                },
                'use_secure': rec.using_secure,
                "keep_alive": rec.keep_alive,
                "retries": rec.retries,
                "delay": rec.delay,
            }
            return {
                "type": "ir.actions.printer.connect",
                "res_model": self._name,
                "res_id": rec.id,
                "printer_config_dict": printer_config_dict,
                "context": self.env.context,
            }

    @api.multi
    def get_printer_list(self):
        self.ensure_one()
        for rec in self:
            printer_config_dict = {
                "host": rec.host,
                "port": {
                    "secure": [int(secure_port) for secure_port in rec.secure_port.split(",")],
                    "insecure": [int(secure_port) for secure_port in rec.secure_port.split(",")],
                },
                'use_secure': rec.using_secure,
                "keep_alive": rec.keep_alive,
                "retries": rec.retries,
                "delay": rec.delay,
            }
            return {
                "type": "ir.actions.printer.list",
                "res_model": self._name,
                "res_id": rec.id,
                "printer_config_dict": printer_config_dict,
                "context": self.env.context,
            }

    @api.model
    def update_printer_list(self, res_id, dict_data):
        if not res_id or not 'printer_names' in dict_data:
            return True
        line_obj = self.env['printer.lines']
        printer_list = dict_data.get('printer_names', [])
        for printer_name in printer_list:
            line_ids = line_obj.search([
                ('name', '=', printer_name),
                ('printer_id', '=', res_id)
            ])
            if line_ids:
                line_ids.write({
                    'name': printer_name
                })
            else:
                line_obj.create({
                    'name': printer_name,
                    'printer_id': res_id
                })
        return True

    @api.multi
    def test_print_data(self):
        self.ensure_one()
        for printer in self:
            if not printer.default_printer:
                return True
            printer_name = printer.default_printer.name
            data = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAlgAAAEsCAYAAAAfPc2WAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAC4jAAAuIwF4pT92AAAAB3RJTUUH4gcdBRYQgO8kIwAAIABJREFUeNrt3fl3G9eVNeyNqVCoQlVhngiCsyRLdpzB3b3S6fzz3SuJYydOPGqkxAEECBDzPOP7wd+5b4EiKVGgFCXZz1pYjrtpDFUA7sa5t871LJfLJYiIiIjoznh5CIiIiIgYsIiIiIgYsIiIiIgYsIiIiIiIAYuIiIiIAYuIiIiIAYuIiIiIGLCIiIiIGLCIiIiIGLCIiIiIiAGLiIiIiAGLiIiIiAGLiIiIiAGLiIiIiBiwiIiIiBiwiIiIiBiwiIiIiIgBi4iIiIgBi4iIiIgBi4iIiIgYsIiIiIgYsIiIiIgYsIiIiIiIAYuIiIiIAYuIiIiIAYuIiIiIAYuIiIiIGLCIiIiIGLCIiIiIGLCIiIiIiAGLiIiIiAGLiIiIiAGLiIiIiBiwiIiIiBiwiIiIiBiwiIiIiAgA4L/LO1ssFurW7XbR7/fR6/WwXC6v/PtAIIBQKARd1xEMBqFpGgKBAHw+38rfLZdLLJdLzOdzdLtddLtd9Hq9a5+HpmkIBoMrN03TXrvf25pOp5hMJhiPxxiPxxiNRhiPx5jP59e+PsuyEA6HYRgGPB6Puq1jMpmoYzsajVaO+zqCwSAMw4BhGAgGg/D7/fD5fPB6P0wOl9cwnU7R6/XQ6/UwGAzWvl855oFAALZtw7IshEKha/9ezq/7NplMrj2+wWAQlmXBtm3our72+RWj0Ugdh/F4jMVioT4L6wiFQjBNE6ZpQtM0eL1e+Hy+tZ/3cDjEYDDAYDDAdDrFbDbDbDZbeb4ej0e9pzRNQzgchmma0HX9xvuV23Q6Vbd1joPH44Gu6+qmaZq6XWW5XGI4HKLb7aLT6WAymXzYX8L///GSm67rCIVC1z7f96nf76vbbDbDfD6/9jvwNq8vFAqp7x+/369u140xw+FQfQ9Op9Mb71fGmUAgoG5XjTHL5VLdZ7fbxWw2+6DH1ufzrYxZMjZefr5uMiZ2u907+47wer0Ih8Pq8+n1etXNbT6fq8/6aDRS3wHXHTefzwfTNNV59vl86nb5fuUm3yn9fv/a95nf74dhGOo8+/3+K7OE+/0j57nX6609drrHdtu2EQ6HYdv23QUsecPLm/6rr77C119/ja+++uraN38mk8G9e/dw7949bG1tIZfLIZvNwnGclTe+fFF3Oh384Q9/wB/+8Ad8+eWX1z6XbDaLnZ0d7OzsYGtrC4VCAVtbW7Bte63XeHFxgWKxiGKxiFevXuHw8BCHh4fXhr10Oo3f/va3+O1vf4uHDx+q4HfTh+VtVKtV/OUvf8Ff/vIXHB4eqjfKeDxe634LhQJ++ctf4vPPP0ehUEAkEkEkEoFhGO/9i2U2m6nQWq1W8ec//xlffvklvv/++7Xf+DKgb2xs4Pe//z3+53/+B48ePbr2fXx2doajoyMcHR3h+PhY3a4bVLe3t/H73/8ev//973FwcHDtl9FtnZ6e4ssvv8SXX36Jk5MTFfbW/dJ/8OABfv3rX+M3v/kNstms+hGw7mD98uVLfPfdd/j+++9RqVTQbDbRaDRWPv+apsE0TYTDYeTzeXzxxRf4zW9+g4ODg2vPx8uXL/H48WM8fvwY5+fnqFarqFarax0HTdOwt7eH/f197O3tIZ/PY2NjA/l8fuW8yYC1WCzw4sUL/O///i/+7//+D8Vi8YMOvIZhIJfLIZfLYXNzEwcHB+p780Oaz+d4/PgxvvnmG3zzzTdotVrodDpqcF/nx91nn32Gzz77DI8ePUI8HkcsFkMsFls5H+PxGP1+H4PBAE+fPsXXX3+Nv/71rzg/P7/yfk3TxIMHD3D//n0cHBwgk8kgnU4jnU6/9uNZfkB/++23+OMf/4g//elPaDQaH/T4Oo6DQqGgxqzd3V3s7Owgk8lcez7+9re/4Q9/+AP++Mc/YjgcYjabXTvm3uZH2H/8x3/gP//zP/HFF1+o8BsKhVZ+iHW7XdRqNdTrdbx48QI//PADfvzxR9Tr9Svv17Zt/PKXv8SvfvUrPHr0CLZtw3Gc18bmfr+PTqeDdruNn376CX/729/w97//He12+8r7jcViePToET799FPs7+8jkUggHo8jGo2uZInRaITBYIDhcIhvvvkGX331Fb766qu1f8gHAgH4/X4Eg0H87ne/w+9+9zv893//991WsObzOSaTCYbDIcrlMh4/fow//elPNw5My+UShmGoxHf5jSFfbvP5HOPxGOfn5/jpp5/wxz/+8drnsbOzg9FopH69RKPRtd9w8uFut9s4Pz/Hy5cv8cMPP+C777679qQXCgWk02ncv38f0+kUPp9v7aQsv+jPz8/x9OlTfP/992i32+h0Omu/SRqNBsLhMLLZLGKxGHRdX/uX6duSID2ZTNDr9XB6eooffvjhxvP8tgFLKnF7e3soFAr4/PPPb3weg8EA9XodxWIRz549w5MnT/DkyROMRqMr/5tWq4WtrS01yHg8nrV/QcqXTLFYxA8//IBnz56pL4Z138uTyQSxWAy7u7uIRCIIBoN38r7s9XoolUp48uQJTk5OcHFxgUqlshL8dV2H4zhwHAfdbhe5XA4PHjy48Xx0u12Uy2U8f/4cJycnOD09xenp6VrHIRgMYjAYwOPxwDAMmKaJWCx25XmTX7ydTgfHx8f45ptv8OLFiw868FqWhd3dXXQ6HSwWC0SjUeTz+Q9evVoul2i1Wjg5OcH333+Pi4sLNJtNNJvNtb4rQqEQvF4vHMfBxsYGgsEgwuHwlWPMdDrFcDjExcUFXrx4gb/+9a84Pj6+NrDM53Pouo5oNArDMFYG3cvfP9PpVIWFr7/+GpVK5YMe30QioSqkfr8f0WgUuVzuxvPRaDRweHiIr7/+Gv1+H5PJZO0Kr2masG0bhUIBw+EQPp/vyh9g0+kUg8EArVYLZ2dnKvReF3hjsRhCoRDS6TQKhYL6wXXVD26pGJfLZTx9+hRfffXVtcEtnU7D5/MhGo0ikUggFAqtFGquev/IGPrnP/8Z3W53rfMmlWV5bQ8ePMByueQaLCIiIqK7xoBFRERExIBFRERExIBFRERExIBFRERERAxYRERERAxYRERERAxYRERERMSARURERMSARURERMSARUREREQMWEREREQMWEREREQMWEREREQMWERERETEgEVERETEgEVERETEgEVEREREDFhEREREDFhEREREDFhERERExIBFRERExIBFRERExIBFRERERAxYRERERAxYRERERAxYRERERAxYRERERMSARURERMSARURERMSARUREREQMWEREREQMWEREREQMWERERETEgEVERETEgEVERETEgEVEREREDFhEREREDFhEREREDFhEREREDFhERERExIBFRERExIBFRERExIBFRERERAxYRERERAxYRERERAxYRERERMSARURERMSARURERMSARUREREQMWEREREQMWEREREQMWEREREQMWERERETEgEVERETEgEVERETEgEVEREREDFhEREREDFhEREREDFhERERExIBFRERExIBFRERExIBFRERExIBFRERERAxYRERERAxYRERERAxYRERERMSARURERMSARURERMSARUREREQMWEREREQMWEREREQMWERERETEgEVERETEgEVERETEgEVERETEgEVEREREDFhEREREDFhEREREDFhERERExIBFRERExIBFRERExIBFRERERAxYRERERAxYRERERAxYRERERMSARURERMSARURERMSARURERMSARUREREQMWEREREQMWEREREQMWERERETEgEVERETEgEVERETEgEVEREREDFhEREREDFhEREREDFhERERExIBFRERExIBFRERExIBFRERExIBFRERERAxYRERERAxYRERERAxYRERERMSARURERMSARURERMSARUREREQMWEREREQMWEREREQMWEREREQMWERERETEgEVERETEgEVERETEgEVEREREDFhEREREDFhEREREDFhERERExIBFRERExIBFRERExIBFRERERAxYRERERAxYRERERAxYRERERAxYRERERMSARURERMSARURERMSARUREREQMWEREREQMWEREREQMWERERETEgEVERETEgEVERETEgEVEREREDFhEREREDFhEREREDFhEREREDFhERERExIBFRERExIBFRERExIBFRERERAxYRERERAxYRERERAxYRERERMSARURERPSB+HkIbpFGvV4EAgGEQiGEw2E4joN4PI5AIHDl38diMYTDYQSDQXi9Xng8njt5Hj6fD7quw7IsRKNR+Hw+BAIBGIax1v1Go1FYlgVd1+H3++Hz+e7sOb+Jx+OBx+OB1+uF3++HYRhwHAeJRGLtc+bz+eDz+RCNRmGa5rXnS56H3+9HMBiEYRiwLAuRSASJRAKj0eja42YYxsr93sVxcx+HWCyGUCiE0WiE6XS61v1GIhGYpglN0+Dz+e7sven3+xEKhWDbNqLRKObzOebzOcbjsfqbYDAI27Zh2zYcx0EoFILf73+r+7UsC47joN/vYzgcrnUcgsEgIpEIwuEwQqGQOhY3vTcDgQBM00QsFlv7fXlb8j60bRuGYSAYDL7xuL2vz6l810QiEcznc/UZm8/n73y/oVAIjuOoz6ff74fX673y8eXxgsEgLMtCLBZDv9+/8n7lfWaaJoLBIAKBwJX3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KEn4zOfzyOfzyOVyaiqZiBiwiD5IBcv979FoFL1e7709poQsmfZ6U8CSkLKxsYF0Oo10Oo1sNqt6OZVKJbTbbUwmE0ynU7WdiwSJnZ0d7OzsoFAowHEctUbpcjXmLgKW3+9HOp3GcrlEIpFQU53BYFD1dXqX6Uj3tKk0+iwUChgOhzg+Pla3er2OZrOJZrOp9lxcLBbQNE1V8qQ1xcbGBjKZDJLJJBKJhLqo4G2fn8fjQSQSgWVZ2N7eRrVaVUGtVCqp6cJut4v5fI7FYgGfz6fOQTweV4vad3Z2VFXtXSpMPp9PVbB8Ph8sy0Iul8NkMllp+yCbiLOCRcSARfReSTd1WZMjmyBLAHmfjyuNRt0B77rqjQiFQqqDuHs7HdmiRbZpkcE6HOY+ZgkAAAP1SURBVA4jk8kgk8mobu232Tj4XSpNhmEgFoupZqzyT9M01X5+7xrg5DFk+szr9SKRSKgQlclk1JZCs9lMndNAIABd11f2eJSpS2ld4Pf73+m5yD+l19RyuYRpmkilUmi32xgMBqp7u7TnkJAoAU8aqMrruu0xkkqsNIuVcz+fz1WjUdkGaJ1NyYmIAYvorQdLuYLO6/WqRcHrbIHztgO0z+dTmwu/LenVFAgEYFkWksmk2tJnsVhgPp+r0Cj7+Lm3SJHA875el6wFAqB6iMn6I03T7qx6IiFBOp8HAgE4jqN6XY3HYxVqpCO/+5hIhU+C6DrHRAJRKBRS7SHi8biaqpxOp+p5yPStbLdk2zYsy1L7Hq7TvFaOraZpKmwvFgtVtZKrKj+mXmdEDFhE/wYVLKlyuPete9+PfdtqhVx1ZlmWChDyT+D/7UHovu/LV/K9z+khCViyV6P7sd7l9d70OO7Q5DjOSqC6fA7lMS8fE/e/rxuYdV2HpmmIRqMr58Z9Xq56Du96leVVFSxN01Zeu5yDuzz2RMSARfTWg+M/y8AjQeBjmua5fOzWDSy3ebz3/Vj/LM+F4Ynonw9ryUREREQMWEREREQMWEREREQMWERERETEgEVERETEgEVERETEgEVEREREDFhERERE/wh32mj0cuflTCaDnZ2da7clkc1tI5GI2sfsqgaL0mRP9pDLZrPY3d299nnk83lkMhnEYjFYlqW29CAiIqK74fP5oGma2og8nU5ja2sLhmFc+feO4yCdTsNxHLV35lXNe2U/Ul3X1X+zvb0Nx3GuvN9EIoFMJoNIJALDMKBp2kexZZRneYd7hsxmM0ynU0ynU1QqFZyfn+P8/FxtJ3GZaZpqF3jLshAOh2EYxmub48qGrpPJBKVSCWdnZzg/P7/2eZimqXa0l5tlWdA0jZ8IIiKiOzAejzEajTAcDtFqtVCv11Gr1TAaja78e03TkEqlkEwmEY/HV/bRdJtMJphMJhiPx2g0GqhWq6hWq5hMJlfer67riMfjiMfjatN72fz9XyZgERERERHXYBERERExYBERERExYBERERExYBERERERAxYRERERAxYRERERAxYRERERMWARERERMWARERERMWAREREREQMWEREREQMWEREREQMWEREREQMWERERETFgERERETFgERERETFgEREREREDFhEREREDFhEREREDFhERERExYBERERExYBERERExYBERERERAxYRERERAxYRERERAxYRERERAxYRERERMWARERERMWARERERMWAREREREQMWEREREQMWEREREQMWERERETFgERERETFgERERETFgEREREZH4/wAZ9qxnt0/7gAAAAABJRU5ErkJggg=='
            printer_config_dict = {
                "host": printer.host,
                "port": {
                    "secure": [int(secure_port) for secure_port in printer.secure_port.split(",")],
                    "insecure": [int(secure_port) for secure_port in printer.secure_port.split(",")],
                },
                'use_secure': printer.using_secure,
                "keep_alive": printer.keep_alive,
                "retries": printer.retries,
                "delay": printer.delay,
            }
            return {
                "type": "ir.actions.print.data",
                "res_model": self._name,
                "res_id": printer.id,
                "printer_name": printer_name,
                "path": data,
                "printer_config_dict": printer_config_dict,
                "context": self.env.context,
            }
