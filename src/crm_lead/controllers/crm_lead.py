from odoo import http
from odoo.http import request
import logging
import json

_logger = logging.getLogger(__name__)

class ContactFormController(http.Controller):

    @http.route('/api/contact_form/', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def contact_form(self, **kw):
        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            name = data.get("name")
            email = data.get("email")
            phone = data.get("phone")

            lead_vals = {
                "name": f"Landing Form - {name}" if name else "Landing Form",
                "contact_name": name,
                "email_from": email,
                "phone": phone,
                "user_id": 2
            }

            lead = request.env["crm.lead"].sudo().create(lead_vals)
            return json.dumps({"success": True, "lead_id": lead.id})
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})
