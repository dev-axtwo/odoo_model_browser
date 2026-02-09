# -*- coding: utf-8 -*-
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class ModelBrowserController(http.Controller):

    @http.route('/model_browser/search', type='json', auth='user')
    def search_models(self, search_term='', limit=100):
        """Search models by name or technical name."""
        try:
            result = request.env['ir.model'].get_browsable_models(search_term, limit)
            _logger.info("Model Browser Controller: Returning %d models", len(result))
            return result
        except Exception as e:
            _logger.error("Model Browser Controller error: %s", e, exc_info=True)
            # Return error as a visible item
            return [{
                'id': 0,
                'name': f'ERROR: {str(e)[:100]}',
                'model': 'error',
                'count': 0,
                'info': str(e),
            }]

    @http.route('/model_browser/open', type='json', auth='user')
    def open_model(self, model_name):
        """Get action to open model list view."""
        action_id = request.env['ir.model'].get_model_action(model_name)
        if action_id:
            action = request.env['ir.actions.act_window'].browse(action_id).read()[0]
            return action
        return False

