"""
Custom JWT Authentication for graceful handling of invalid tokens
This allows endpoints with IsAuthenticatedOrReadOnly to work even when
invalid/expired tokens are sent (e.g., from mobile app in guest mode)
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework import exceptions
import logging

logger = logging.getLogger(__name__)


class GracefulJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication that gracefully handles invalid tokens.
    
    For endpoints that allow unauthenticated access (IsAuthenticatedOrReadOnly),
    invalid tokens are silently ignored instead of raising an error.
    This prevents "Given token not valid for any token type" errors when:
    - Mobile app sends expired tokens in guest mode
    - Mobile app sends invalid tokens from previous sessions
    - Token validation fails for any reason on read-only endpoints
    """
    
    def authenticate(self, request):
        """
        Override authenticate to gracefully handle invalid tokens.
        Returns None (unauthenticated) instead of raising an error.
        """
        header = self.get_header(request)
        if header is None:
            return None
        
        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None
        
        # Try to validate the token
        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            return (user, validated_token)
        except (InvalidToken, TokenError) as e:
            # For invalid/expired tokens, log but don't raise error
            # This allows endpoints with IsAuthenticatedOrReadOnly to work
            # The permission class will handle unauthenticated users appropriately
            logger.debug(f"Invalid JWT token ignored (endpoint allows unauthenticated access): {str(e)}")
            return None
        except Exception as e:
            # For other exceptions, also log but don't raise
            # This prevents token validation errors from breaking guest access
            logger.warning(f"JWT authentication error (gracefully ignored): {str(e)}")
            return None

