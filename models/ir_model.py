# -*- coding: utf-8 -*-
import logging
from odoo import models, api
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)


class IrModel(models.Model):
    _inherit = 'ir.model'

    @api.model
    def get_browsable_models(self, search_term='', limit=100):
        """
        Get all models that can be browsed (have at least one view).
        Returns list of dicts with model info.
        """
        domain = [('transient', '=', False)]
        
        if search_term:
            search_term = search_term.lower()
            domain += [
                '|',
                ('name', 'ilike', search_term),
                ('model', 'ilike', search_term),
            ]
        
        # Use sudo() to ensure we can read ir.model records
        ir_models = self.sudo().search(domain, limit=limit, order='name')
        
        _logger.info("Model Browser: Found %d ir.model records for search '%s'", len(ir_models), search_term)
        
        result = []
        for ir_model in ir_models:
            try:
                model_obj = self.env.get(ir_model.model)
                if model_obj is None:
                    _logger.debug("Model Browser: Model %s not in registry", ir_model.model)
                    continue
                
                # Get record count - use sudo to avoid access errors blocking model listing
                # We still show the model even if count fails
                count = 0
                try:
                    # First check if user has read access to this model
                    model_obj.check_access_rights('read', raise_exception=False)
                    count = model_obj.sudo().search_count([])
                except (AccessError, Exception) as e:
                    _logger.debug("Model Browser: Cannot get count for %s: %s", ir_model.model, e)
                    count = 0
                
                result.append({
                    'id': ir_model.id,
                    'name': ir_model.name,
                    'model': ir_model.model,
                    'count': count,
                    'info': ir_model.info or '',
                })
            except Exception as e:
                _logger.warning("Model Browser: Error processing model %s: %s", ir_model.model, e)
                continue
        
        _logger.info("Model Browser: Returning %d browsable models", len(result))
        
        # If no models found, return debug info
        if not result and not search_term:
            return [{
                'id': 0,
                'name': f'DEBUG: Found {len(ir_models)} ir.model records but 0 browsable',
                'model': 'ir.model',
                'count': len(ir_models),
                'info': 'Check server logs for details',
            }]
        
        return result

    @api.model
    def get_model_action(self, model_name):
        """
        Get or create an action to open the model's list view.
        """
        # First try to find existing action
        action = self.env['ir.actions.act_window'].search([
            ('res_model', '=', model_name),
            ('view_mode', 'ilike', 'list'),
        ], limit=1)
        
        if action:
            return action.id
        
        # Create a temporary action
        model = self.search([('model', '=', model_name)], limit=1)
        if not model:
            return False
        
        action = self.env['ir.actions.act_window'].create({
            'name': model.name,
            'res_model': model_name,
            'view_mode': 'list,form',
            'type': 'ir.actions.act_window',
        })
        return action.id

