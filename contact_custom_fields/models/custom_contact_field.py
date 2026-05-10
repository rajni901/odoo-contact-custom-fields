import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class CustomContactField(models.Model):
    _name = 'custom.contact.field'
    _description = 'Custom Contact Field'
    _order = 'sequence, id'

    name = fields.Char(string='Field Label', required=True)
    field_name = fields.Char(string='Technical Name', readonly=True, copy=False)
    sequence = fields.Integer(string='Sequence', default=10)
    field_type = fields.Selection([
        ('char', 'Text (Short)'),
        ('text', 'Text (Long)'),
        ('integer', 'Number (Integer)'),
        ('float', 'Number (Decimal)'),
        ('boolean', 'Checkbox'),
        ('date', 'Date'),
        ('datetime', 'Date & Time'),
        ('selection', 'Dropdown'),
        ('many2one', 'Related Record (Many2one)'),
    ], string='Field Type', required=True, default='char')
    selection_options = fields.Text(
        string='Dropdown Options',
        help='Enter one option per line.\nExample:\nActive\nInactive\nPending'
    )
    related_model_id = fields.Many2one(
        'ir.model',
        string='Related Model',
        help='Required for Many2one field type.'
    )
    field_id = fields.Many2one(
        'ir.model.fields',
        string='System Field',
        readonly=True,
        ondelete='set null',
        copy=False
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('created', 'Created'),
    ], string='Status', default='draft', readonly=True, copy=False)

    @api.onchange('name')
    def _onchange_name(self):
        if self.name:
            tech = re.sub(r'[^a-z0-9]', '_', self.name.lower().strip())
            tech = re.sub(r'_+', '_', tech).strip('_')
            self.field_name = 'x_' + tech

    @api.constrains('field_type', 'selection_options')
    def _check_selection(self):
        for rec in self:
            if rec.field_type == 'selection' and not rec.selection_options:
                raise ValidationError(_('Dropdown Options are required for the Dropdown field type.'))

    @api.constrains('field_type', 'related_model_id')
    def _check_many2one(self):
        for rec in self:
            if rec.field_type == 'many2one' and not rec.related_model_id:
                raise ValidationError(_('Related Model is required for the Many2one field type.'))

    def _parse_selection_options(self):
        lines = [l.strip() for l in self.selection_options.split('\n') if l.strip()]
        result = []
        for line in lines:
            key = re.sub(r'[^a-z0-9]', '_', line.lower())
            key = re.sub(r'_+', '_', key).strip('_')
            result.append((key, line))
        return result

    def _rebuild_partner_view(self):
        all_fields = self.env['custom.contact.field'].search(
            [('state', '=', 'created')], order='sequence, id'
        )
        base_view = self.env.ref('base.view_partner_form')
        existing_view = self.env['ir.ui.view'].sudo().search([
            ('name', '=', 'res.partner.form.contact_custom_fields'),
        ], limit=1)

        if not all_fields:
            if existing_view:
                existing_view.sudo().unlink()
            return

        fields_xml = '\n                '.join(
            f'<field name="{f.field_name}"/>' for f in all_fields
        )

        arch = f"""<?xml version="1.0"?>
<data>
    <notebook position="inside">
        <page string="Custom Fields" name="contact_custom_fields_page">
            <group>
                {fields_xml}
            </group>
        </page>
    </notebook>
</data>"""

        if existing_view:
            existing_view.sudo().write({'arch_db': arch})
        else:
            self.env['ir.ui.view'].sudo().create({
                'name': 'res.partner.form.contact_custom_fields',
                'model': 'res.partner',
                'inherit_id': base_view.id,
                'arch_db': arch,
                'priority': 99,
            })

    def action_create_field(self):
        self.ensure_one()

        if self.state == 'created':
            raise UserError(_('This field has already been added to the Contact form.'))

        if not self.field_name:
            if not self.name:
                raise UserError(_('Please enter a Field Label first.'))
            tech = re.sub(r'[^a-z0-9]', '_', self.name.lower().strip())
            tech = re.sub(r'_+', '_', tech).strip('_')
            self.field_name = 'x_' + tech

        partner_model = self.env['ir.model'].sudo()._get('res.partner')

        duplicate = self.env['ir.model.fields'].sudo().search([
            ('model_id', '=', partner_model.id),
            ('name', '=', self.field_name),
        ], limit=1)
        if duplicate:
            raise UserError(_(
                'A field with technical name "%s" already exists on the Contact model.' % self.field_name
            ))

        field_vals = {
            'name': self.field_name,
            'field_description': self.name,
            'model_id': partner_model.id,
            'ttype': self.field_type,
            'state': 'manual',
        }
        if self.field_type == 'selection':
            field_vals['selection'] = str(self._parse_selection_options())
        if self.field_type == 'many2one':
            field_vals['relation'] = self.related_model_id.model

        new_field = self.env['ir.model.fields'].sudo().create(field_vals)

        self.write({
            'field_id': new_field.id,
            'state': 'created',
        })

        self._rebuild_partner_view()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Field Created'),
                'message': _('"%s" has been added to the Contact form under the Custom Fields tab.' % self.name),
                'type': 'success',
                'sticky': False,
            }
        }

    def unlink(self):
        for rec in self:
            if rec.state == 'created' and rec.field_id:
                try:
                    rec.field_id.sudo().unlink()
                except Exception as e:
                    raise UserError(_(
                        'Cannot delete field "%s": %s' % (rec.name, str(e))
                    ))
        result = super().unlink()
        self._rebuild_partner_view()
        return result
