from rest_framework import serializers
from django.contrib.auth.models import User
from accounts.models import Profile, CustomRole, UserRole
from django.contrib.auth import authenticate
import re


class TenantSignupSerializer(serializers.Serializer):
    """Serializer for user registration (tenant or owner)"""
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=30)
    phone = serializers.CharField(max_length=15, required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=[('tenant', 'Tenant'), ('owner', 'Property Owner')], default='tenant')
    
    def validate_username(self, value):
        """Validate username"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value
    
    def validate_email(self, value):
        """Validate email"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    
    def validate_phone(self, value):
        """Validate phone number format and uniqueness"""
        # Allow empty/blank phone numbers
        if not value or (isinstance(value, str) and value.strip() == ''):
            return None  # Return None instead of empty string
        
        # Normalize phone number
        phone = value.strip()
        
        # Validate format if provided
        if not re.match(r'^\+?[1-9]\d{1,14}$', phone):
            raise serializers.ValidationError("Invalid phone number format")
        
        # Check uniqueness (only if phone is provided)
        from accounts.models import Profile
        if Profile.objects.filter(phone=phone).exists():
            raise serializers.ValidationError("Phone number already exists")
        
        return phone
    
    def validate(self, data):
        """Validate password confirmation"""
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
    def create(self, validated_data):
        """Create new user with role and pending approval"""
        # Remove confirm_password from validated_data
        validated_data.pop('confirm_password')
        phone = validated_data.pop('phone', '')
        role = validated_data.pop('role', 'tenant')
        
        # Create user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            is_active=True
        )
        
        # Auto-approve ALL users when registering via mobile app API
        # Since this serializer is only used for mobile app registration,
        # all users (both tenant and owner) should be auto-approved by default
        # This ensures users can login immediately after registration
        is_approved = True
        
        # Convert empty phone to None (not empty string) to avoid unique constraint violations
        # The Profile model has phone as unique=True, null=True, so None is allowed but '' is not
        if phone and isinstance(phone, str) and phone.strip():
            phone = phone.strip()
        else:
            phone = None  # Set to None if empty, blank, or not provided
        
        # Create profile with role and approval status
        profile = Profile.objects.create(
            user=user,
            phone=phone,  # None if empty, actual phone if provided
            role=role,
            is_approved=is_approved
        )
        
        # Set approved_at timestamp for auto-approved users
        from django.utils import timezone
        profile.approved_at = timezone.now()
        profile.save()
        
        # Assign custom role based on selection
        role_name = 'Tenant' if role == 'tenant' else 'Property Owner'
        try:
            custom_role = CustomRole.objects.get(name=role_name)
        except CustomRole.DoesNotExist:
            # Create role if it doesn't exist
            description = 'Property tenant with mobile app access' if role == 'tenant' else 'Property owner with mobile app access'
            custom_role = CustomRole.objects.create(
                name=role_name,
                description=description
            )
        
        # Ensure role is assigned (use get_or_create to avoid duplicates)
        user_role, created = UserRole.objects.get_or_create(user=user, role=custom_role)
        
        # Verify role assignment was successful
        if not UserRole.objects.filter(user=user, role=custom_role).exists():
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to assign {role_name} role to user {user.username}")
            # Don't fail the signup, but log the error
        
        # Log for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"User {user.username} registered - role: {role}, profile.role: {profile.role}, is_approved: {is_approved}, phone: {phone}, custom_role: {custom_role.name}, user_role_created: {created}")
        
        # Refresh profile to ensure all relationships are loaded
        profile.refresh_from_db()
        user.refresh_from_db()
        
        return user


class TenantLoginSerializer(serializers.Serializer):
    """Serializer for user login (tenant or owner)"""
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)
    
    def _normalize_phone(self, phone):
        """Normalize phone input by stripping spaces and handling different formats."""
        if not phone:
            return ''
        # Remove all spaces and dashes
        normalized = phone.strip().replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        return normalized
    
    def _find_user_by_phone(self, phone):
        """Find user by phone number, trying multiple formats"""
        if not phone:
            return None
        
        # Try exact match first
        profile_qs = Profile.objects.filter(phone__iexact=phone).select_related('user')
        if profile_qs.exists():
            return profile_qs.first().user
        
        # Try without leading + if phone starts with +
        if phone.startswith('+'):
            phone_without_plus = phone[1:]
            profile_qs = Profile.objects.filter(phone__iexact=phone_without_plus).select_related('user')
            if profile_qs.exists():
                return profile_qs.first().user
        
        # Try with + if phone doesn't start with +
        if not phone.startswith('+'):
            phone_with_plus = '+' + phone
            profile_qs = Profile.objects.filter(phone__iexact=phone_with_plus).select_related('user')
            if profile_qs.exists():
                return profile_qs.first().user
        
        return None
    
    def validate(self, data):
        """Validate login credentials and approval status"""
        email = data.get('email', '').strip()
        phone = self._normalize_phone(data.get('phone'))
        password = data.get('password')
        
        if not password:
            raise serializers.ValidationError("Password is required")
        
        if not email and not phone:
            raise serializers.ValidationError("Either email or phone is required")
        
        user = None
        
        if email:
            try:
                user = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid email or password")
        elif phone:
            # Lookup profile by phone number with multiple format attempts
            try:
                user = self._find_user_by_phone(phone)
                if not user:
                    raise serializers.ValidationError("No account found with that phone number")
                
                # Note: Phone field is unique in database, so multiple accounts check is redundant
                # but kept for defensive programming and clarity
            except serializers.ValidationError:
                # Re-raise validation errors as-is
                raise
            except Exception as e:
                # Log and return a generic error for unexpected exceptions
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error during phone login: {str(e)}", exc_info=True)
                raise serializers.ValidationError("An error occurred during login. Please try again or use email instead.")
        
        if not user:
            raise serializers.ValidationError("Invalid login credentials")
        
        # Authenticate using username/password
        auth_user = authenticate(username=user.username, password=password)
        if not auth_user:
            raise serializers.ValidationError("Invalid email/phone or password")
        
        if not auth_user.is_active:
            raise serializers.ValidationError("User account is disabled")
        
        # Allow admin users to skip approval checks
        if auth_user.is_superuser or auth_user.is_staff:
            data['user'] = auth_user
            return data
        
        try:
            profile = auth_user.profile
            
            if profile.is_deactivated:
                reason = profile.deactivation_reason or "due to contract issues or some disagreement"
                raise serializers.ValidationError(
                    f"Your account has been deactivated. {reason}. Please contact the administrator for more information."
                )
            
            if not profile.is_approved:
                raise serializers.ValidationError("Your account is pending admin approval. Please wait for approval before logging in.")
            
            # Check if user has tenant, owner, or manager role
            valid_roles = ['Tenant', 'Property Owner', 'Manager']
            user_roles = list(profile.get_user_roles().values_list('name', flat=True))
            
            # Also check profile role field as fallback
            profile_role_display = profile.get_role_display()
            if profile_role_display and profile_role_display in valid_roles:
                if profile_role_display not in user_roles:
                    user_roles.append(profile_role_display)
            
            # Check Django groups for Manager role (backward compatibility)
            if 'Manager' not in user_roles:
                groups = auth_user.groups.values_list('name', flat=True)
                if 'Manager' in groups or 'Property manager' in groups:
                    user_roles.append('Manager')
            
            # If still no valid role found, check profile.role directly
            if not any(role in valid_roles for role in user_roles):
                if profile.role == 'tenant' or profile.role == 'owner':
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.info(f"User {auth_user.username} login allowed via profile.role: {profile.role}")
                else:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"User {auth_user.username} login failed - roles: {user_roles}, profile role: {profile.role}, profile role display: {profile_role_display}, valid_roles: {valid_roles}")
                    raise serializers.ValidationError("User is not authorized for mobile app access")
        except Profile.DoesNotExist:
            from accounts.models import Profile
            Profile.objects.create(
                user=auth_user,
                role='tenant',
                is_approved=False
            )
            raise serializers.ValidationError("Your account is pending admin approval. Please wait for approval before logging in.")
        
        data['user'] = auth_user
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile information"""
    full_name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    is_approved = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'role', 'phone', 'is_approved', 'date_joined']
        read_only_fields = ['id', 'username', 'date_joined']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_role(self, obj):
        try:
            profile = obj.profile
            roles = profile.get_user_roles()
            if roles.exists():
                return [role.name for role in roles]
            return []
        except Profile.DoesNotExist:
            return []
    
    def get_phone(self, obj):
        try:
            return obj.profile.phone
        except Profile.DoesNotExist:
            return None
    
    def get_is_approved(self, obj):
        try:
            return obj.profile.is_approved
        except Profile.DoesNotExist:
            return False


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    phone = serializers.CharField(source='profile.phone', max_length=15, required=False, allow_blank=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone']
    
    def validate_phone(self, value):
        """Validate phone number format"""
        if value and not re.match(r'^\+?[1-9]\d{1,14}$', value):
            raise serializers.ValidationError("Invalid phone number format")
        return value
    
    def update(self, instance, validated_data):
        """Update user and profile"""
        profile_data = validated_data.pop('profile', {})
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update profile
        if profile_data:
            profile, created = Profile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    def validate_current_password(self, value):
        """Validate current password"""
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect")
        return value
    
    def validate(self, data):
        """Validate password confirmation"""
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New passwords do not match")
        return data
    
    def save(self):
        """Change user password"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class AdminApprovalSerializer(serializers.Serializer):
    """Serializer for admin approval/rejection of users"""
    user_id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=[('approve', 'Approve'), ('reject', 'Reject')])
    
    def validate_user_id(self, value):
        """Validate user exists and has a profile"""
        try:
            user = User.objects.get(id=value)
            if not hasattr(user, 'profile'):
                raise serializers.ValidationError("User does not have a profile")
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")


class PendingUserSerializer(serializers.ModelSerializer):
    """Serializer for listing pending users"""
    username = serializers.CharField(source='user.username')
    email = serializers.CharField(source='user.email')
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    date_joined = serializers.DateTimeField(source='user.date_joined')
    role_display = serializers.CharField(source='get_role_display')
    
    class Meta:
        model = Profile
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'role', 'role_display', 'date_joined', 'is_approved']