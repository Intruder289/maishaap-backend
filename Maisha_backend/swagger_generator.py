"""
Custom Swagger generator with error handling to skip problematic views
"""
import logging
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.errors import SwaggerGenerationError

logger = logging.getLogger(__name__)


def clean_schema_for_serialization(schema_dict):
    """
    Recursively clean schema dictionary to remove non-serializable objects
    """
    if isinstance(schema_dict, dict):
        cleaned = {}
        for key, value in schema_dict.items():
            # Skip SerializerMetaclass and other non-serializable types
            if hasattr(value, '__class__') and 'Serializer' in value.__class__.__name__ and 'Meta' in dir(value):
                logger.warning(f"Skipping non-serializable serializer class: {key}")
                continue
            cleaned[key] = clean_schema_for_serialization(value)
        return cleaned
    elif isinstance(schema_dict, list):
        return [clean_schema_for_serialization(item) for item in schema_dict]
    else:
        return schema_dict


class ErrorHandlingSchemaGenerator(OpenAPISchemaGenerator):
    """
    Custom schema generator that catches errors during schema generation
    and skips problematic views instead of failing completely.
    
    FIX: drf-yasg passes patterns=[] for UI renderers but actual patterns for spec renderers.
    This generator stores the desired patterns and uses them even when empty patterns are passed.
    """
    
    # Class-level storage for desired patterns (set from urls.py)
    _desired_patterns = None
    
    @classmethod
    def set_desired_patterns(cls, patterns):
        """Set the patterns that should be used for endpoint discovery"""
        cls._desired_patterns = patterns
        logger.info(f"Stored {len(patterns) if patterns else 0} desired URL pattern(s) for Swagger")
    
    def __init__(self, info=None, version=None, url=None, patterns=None, urlconf=None):
        """Initialize with logging to debug pattern configuration"""
        # Use desired patterns if available, otherwise use passed patterns
        # This fixes the issue where drf-yasg passes patterns=[] for UI renderers
        if self._desired_patterns is not None and (not patterns or len(patterns) == 0):
            patterns = self._desired_patterns
            logger.info(f"Using stored desired patterns ({len(patterns)} patterns) instead of empty patterns")
        
        super().__init__(info, version, url, patterns, urlconf)
        # Check both the parameter and the instance attribute (drf-yasg stores it as self.patterns)
        patterns_to_check = patterns if patterns is not None else getattr(self, 'patterns', None)
        if patterns_to_check:
            pattern_count = len(patterns_to_check) if isinstance(patterns_to_check, (list, tuple)) else 1
            logger.info(f"Schema generator initialized with {pattern_count} URL pattern(s)")
        else:
            logger.warning("Schema generator initialized with NO patterns - endpoints may not be discovered!")
            logger.warning("This means Swagger will scan ALL URL patterns, which may cause issues")
    
    def get_endpoints(self, request):
        """
        Override get_endpoints to debug endpoint discovery and ensure patterns are used
        """
        # Log pattern information for debugging
        patterns_attr = getattr(self, 'patterns', None)
        if patterns_attr:
            pattern_count = len(patterns_attr) if isinstance(patterns_attr, (list, tuple)) else 1
            logger.info(f"Using {pattern_count} URL pattern(s) for endpoint discovery")
        else:
            logger.warning("Generator has no patterns attribute - will scan all URLs (may be slow)")
        
        try:
            endpoints = super().get_endpoints(request)
            logger.info(f"Discovered {len(endpoints)} endpoints for Swagger documentation")
            if len(endpoints) == 0:
                logger.warning("No endpoints discovered! Check that:")
                logger.warning("1. API views are DRF views (APIView, ViewSet, @api_view)")
                logger.warning("2. URL patterns are correctly included in api_patterns")
                logger.warning("3. Views are properly imported and accessible")
                logger.warning("4. Patterns are being passed to get_schema_view()")
            return endpoints
        except Exception as e:
            logger.error(f"Error discovering endpoints: {str(e)}", exc_info=True)
            # Return empty list instead of crashing
            return []
    
    def get_schema(self, request=None, public=False):
        """
        Override get_schema to catch any errors and return a minimal valid schema
        """
        try:
            schema = super().get_schema(request, public)
            # Post-process schema to ensure it's JSON serializable
            # This catches cases where serializer classes weren't properly converted
            try:
                import json
                # Try to serialize to catch any non-serializable objects
                json.dumps(schema._asdict() if hasattr(schema, '_asdict') else dict(schema))
            except (TypeError, ValueError) as json_error:
                logger.warning(f"Schema contains non-serializable objects: {str(json_error)}. Attempting to clean...")
                # If serialization fails, return minimal schema
                return self._create_minimal_schema()
            return schema
        except Exception as e:
            logger.error(f"Critical error generating schema: {str(e)}", exc_info=True)
            return self._create_minimal_schema()
    
    def _create_minimal_schema(self):
        """Create a minimal valid schema as fallback"""
        from drf_yasg import openapi
        try:
            info = self.info
        except AttributeError:
            # Fallback if info is not available
            info = openapi.Info(
                title="Maisha Backend API",
                default_version='v1',
                description="API documentation (some endpoints may be unavailable due to configuration issues)"
            )
        # Create minimal schema - Components is not available in drf-yasg.openapi
        # Provide empty string as prefix to avoid NoneType error
        schema = openapi.Swagger(
            info=info,
            paths={},
            _prefix='',  # Provide empty string instead of None
        )
        # Set components as empty dict if the schema supports it
        if hasattr(schema, 'components'):
            schema.components = {}
        return schema
    
    def get_operation(self, view, path, prefix, method, components, request, public=None):
        """
        Override get_operation to catch ONLY serialization-related errors
        We should NOT catch all exceptions - let normal operations proceed
        Note: public parameter may not be passed by parent in some drf-yasg versions
        """
        try:
            # Call parent - handle both with and without public parameter
            if public is not None:
                return super().get_operation(view, path, prefix, method, components, request, public)
            else:
                # Some versions of drf-yasg don't pass public to get_operation
                return super().get_operation(view, path, prefix, method, components, request)
        except SwaggerGenerationError as e:
            # Only skip for actual Swagger generation errors
            view_name = getattr(view, '__name__', getattr(view.__class__, '__name__', 'Unknown'))
            logger.warning(f"Skipping operation {view_name} at {path} ({method}): {str(e)}")
            return None
        except TypeError as e:
            # Only catch TypeError if it's specifically about serialization
            error_msg = str(e)
            if 'SerializerMetaclass' in error_msg or 'not JSON serializable' in error_msg:
                view_name = getattr(view, '__name__', getattr(view.__class__, '__name__', 'Unknown'))
                logger.warning(f"Skipping operation {view_name} at {path} ({method}) due to serialization issue: {error_msg}")
                return None
            # For other TypeErrors, let them propagate (might be legitimate errors)
            raise
        # Don't catch other exceptions - let them propagate so we can see what's wrong
    
    def get_paths(self, endpoints, components, request, public):
        """
        Override to catch errors - use parent implementation but handle errors gracefully
        """
        # Log endpoint information for debugging
        if endpoints:
            if isinstance(endpoints, (list, tuple)):
                logger.debug(f"get_paths called with {len(endpoints)} endpoints")
                if len(endpoints) > 0:
                    logger.debug(f"First endpoint type: {type(endpoints[0])}, value: {endpoints[0]}")
            else:
                logger.debug(f"get_paths called with endpoints type: {type(endpoints)}")
        else:
            logger.warning("get_paths called with empty endpoints")
        
        # Use parent implementation which handles endpoint processing correctly
        # Just wrap it in error handling for prefix calculation issues
        try:
            paths, prefix = super().get_paths(endpoints, components, request, public)
            logger.debug(f"get_paths returned {len(paths)} paths with prefix: {prefix}")
            return paths, prefix
        except (ValueError, TypeError, KeyError) as e:
            # Handle prefix calculation errors (empty sequence, etc.)
            logger.warning(f"Error in get_paths (likely prefix calculation): {str(e)}")
            # Return empty paths and prefix - let the schema generation continue
            return {}, ''
        except Exception as e:
            # Catch any other errors
            logger.error(f"Unexpected error in get_paths: {str(e)}", exc_info=True)
            return {}, ''
