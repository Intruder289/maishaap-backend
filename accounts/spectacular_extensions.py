"""
OpenAPI extensions for drf-spectacular
"""
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.plumbing import build_bearer_security_scheme_object
from .authentication import GracefulJWTAuthentication


class GracefulJWTAuthenticationExtension(OpenApiAuthenticationExtension):
    """
    OpenAPI extension for GracefulJWTAuthentication
    This tells drf-spectacular how to document JWT authentication
    """
    target_class = GracefulJWTAuthentication
    name = 'Bearer'

    def get_security_definition(self, auto_schema):
        """
        Return the security definition for JWT Bearer authentication
        """
        return build_bearer_security_scheme_object(
            header_name='Authorization',
            token_prefix='Bearer',
            bearer_format='JWT'
        )
