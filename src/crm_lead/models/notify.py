from odoo import models, fields, api, _
import logging
from pytz import timezone
from datetime import datetime
tz = timezone('Asia/Tashkent')

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model_create_multi
    def create(self, vals_list):
        leads = super().create(vals_list)
        odoobot_partner = self.env.ref('base.partner_root').sudo()
        hr_group = self.env.ref('crm_lead.group_hr_manager_custom')

        for lead in leads:
            message = _("🆕 New CRM Lead Created: %s") % (lead.name)
            company_id = lead.company_id.id
            hr_users = self.env['res.users'].search([
                ('groups_id', 'in', hr_group.id),
                ('company_id', '=', company_id),
                ('active', '=', True),
            ])
            for user in hr_users:
                if not user.partner_id:
                    continue

                responsible_partner_id = int(user.partner_id.id)
                odoobot_id = int(odoobot_partner.id)

                channel = self.env['discuss.channel'].sudo().search([
                    ('channel_type', '=', 'chat'),
                    ('channel_partner_ids', 'in', [odoobot_id]),
                    ('channel_partner_ids', 'in', [responsible_partner_id]),
                ], limit=1)
                if not channel:
                    channel = self.env['discuss.channel'].sudo().create({
                        'name': "Chat",
                        'channel_type': 'chat',
                    })
                    channel.sudo().write({
                        'channel_partner_ids': [(4, odoobot_id), (4, responsible_partner_id)]
                    })

                # Xabar yuborish
                channel.sudo().message_post(
                    body=message,
                    author_id=odoobot_id,
                    message_type='notification',
                    subtype_xmlid='mail.mt_comment',
                )

        return leads
