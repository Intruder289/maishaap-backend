from django import forms
from django.contrib.auth.models import User
from .models import Property, PropertyType, Region, District, Amenity, PropertyImage


class BasePropertyForm(forms.ModelForm):
    """Base form for creating and editing properties"""
    
    class Meta:
        model = Property
        fields = [
            'title', 'description', 'property_type', 'region', 'district', 'address',
            'latitude', 'longitude', 'size_sqft', 'status', 'is_featured',
            'available_from', 'amenities', 'booking_expiration_hours'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter property title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the property...'
            }),
            'property_type': forms.Select(attrs={'class': 'form-control'}),
            'region': forms.Select(attrs={'class': 'form-control', 'id': 'id_region'}),
            'district': forms.Select(attrs={'class': 'form-control', 'id': 'id_district'}),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter full address'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'placeholder': 'Latitude'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'placeholder': 'Longitude'
            }),
            'size_sqft': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Size in square feet'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'available_from': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'amenities': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'booking_expiration_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '1',
                'placeholder': 'Hours (0 to disable auto-cancellation)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop('owner', None)
        super().__init__(*args, **kwargs)
        
        # Initialize district field
        if 'district' in self.fields:
            self.fields['district'].empty_label = "Select District (select region first)"
            self.fields['district'].queryset = District.objects.none()  # Start with empty queryset
            
            # If editing existing property, load districts for the property's region
            if self.instance and self.instance.pk and self.instance.region:
                self.fields['district'].queryset = District.objects.filter(region=self.instance.region)
            # If region is provided in POST data (for new properties), load districts for that region
            elif self.data and 'region' in self.data and self.data.get('region'):
                try:
                    region_id = int(self.data.get('region'))
                    self.fields['district'].queryset = District.objects.filter(region_id=region_id)
                except (ValueError, TypeError):
                    pass
        
        # Make booking_expiration_hours optional with default value
        if 'booking_expiration_hours' in self.fields:
            self.fields['booking_expiration_hours'].required = False
            # Set initial value to model default if not provided
            if not self.instance.pk and 'booking_expiration_hours' not in self.initial:
                self.initial['booking_expiration_hours'] = 12
        
        # Set owner if provided
        if self.owner:
            self.instance.owner = self.owner
    
    def clean_booking_expiration_hours(self):
        """Ensure booking_expiration_hours has a default value if not provided"""
        booking_expiration_hours = self.cleaned_data.get('booking_expiration_hours')
        if booking_expiration_hours is None or booking_expiration_hours == '':
            return 12  # Return model default
        return booking_expiration_hours


class HotelPropertyForm(BasePropertyForm):
    """Form specifically for Hotel properties"""
    
    class Meta(BasePropertyForm.Meta):
        fields = BasePropertyForm.Meta.fields + [
            'total_rooms', 'room_types', 'bathrooms', 'rent_amount', 'rent_period', 'deposit_amount',
            'utilities_included', 'is_furnished', 'pets_allowed', 'smoking_allowed'
        ]
        
        widgets = {
            **BasePropertyForm.Meta.widgets,
            'total_rooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Total number of rooms'
            }),
            'room_types': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'JSON format: {"Single": 10, "Double": 5, "Suite": 2}'
            }),
            'bathrooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'rent_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Base rate per night'
            }),
            'rent_period': forms.Select(attrs={
                'class': 'form-control'
            }),
            'deposit_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Security deposit amount'
            }),
            'utilities_included': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_furnished': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pets_allowed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'smoking_allowed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop('owner', None)
        super().__init__(*args, **kwargs)
        
        # Initialize district field
        if 'district' in self.fields:
            self.fields['district'].empty_label = "Select District (select region first)"
            self.fields['district'].queryset = District.objects.none()  # Start with empty queryset
            
            # If editing existing property, load districts for the property's region
            if self.instance and self.instance.pk and self.instance.region:
                self.fields['district'].queryset = District.objects.filter(region=self.instance.region)
            # If region is provided in POST data (for new properties), load districts for that region
            elif self.data and 'region' in self.data and self.data.get('region'):
                try:
                    region_id = int(self.data.get('region'))
                    self.fields['district'].queryset = District.objects.filter(region_id=region_id)
                except (ValueError, TypeError):
                    pass
        
        # Set owner if provided
        if self.owner:
            self.instance.owner = self.owner


class HousePropertyForm(BasePropertyForm):
    """Form specifically for House properties"""
    
    class Meta(BasePropertyForm.Meta):
        fields = BasePropertyForm.Meta.fields + [
            'bedrooms', 'bathrooms', 'floor_number', 'total_floors', 
            'rent_amount', 'rent_period', 'deposit_amount', 'utilities_included', 
            'is_furnished', 'pets_allowed', 'smoking_allowed', 'visit_cost'
        ]
        
        widgets = {
            **BasePropertyForm.Meta.widgets,
            'bedrooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'bathrooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'floor_number': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'total_floors': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'rent_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Monthly rent amount'
            }),
            'rent_period': forms.Select(attrs={
                'class': 'form-control'
            }),
            'deposit_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Security deposit amount'
            }),
            'visit_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Visit cost (one-time fee to view owner contact)'
            }),
            'utilities_included': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_furnished': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pets_allowed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'smoking_allowed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop('owner', None)
        super().__init__(*args, **kwargs)
        
        # Initialize district field
        if 'district' in self.fields:
            self.fields['district'].empty_label = "Select District (select region first)"
            self.fields['district'].queryset = District.objects.none()  # Start with empty queryset
            
            # If editing existing property, load districts for the property's region
            if self.instance and self.instance.pk and self.instance.region:
                self.fields['district'].queryset = District.objects.filter(region=self.instance.region)
            # If region is provided in POST data (for new properties), load districts for that region
            elif self.data and 'region' in self.data and self.data.get('region'):
                try:
                    region_id = int(self.data.get('region'))
                    self.fields['district'].queryset = District.objects.filter(region_id=region_id)
                except (ValueError, TypeError):
                    pass
        
        # Set default rent_period for houses (per month)
        if 'rent_period' in self.fields and not self.instance.pk:
            self.fields['rent_period'].initial = 'month'
        
        # Set owner if provided
        if self.owner:
            self.instance.owner = self.owner


class LodgePropertyForm(BasePropertyForm):
    """Form specifically for Lodge properties"""
    
    class Meta(BasePropertyForm.Meta):
        fields = BasePropertyForm.Meta.fields + [
            'total_rooms', 'room_types', 'bathrooms', 'rent_amount', 'rent_period', 'deposit_amount',
            'utilities_included', 'is_furnished', 'pets_allowed', 'smoking_allowed'
        ]
        
        widgets = {
            **BasePropertyForm.Meta.widgets,
            'total_rooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Total number of rooms'
            }),
            'room_types': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'JSON format: {"Standard": 8, "Deluxe": 4, "Suite": 2}'
            }),
            'bathrooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'rent_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Base rate per night'
            }),
            'rent_period': forms.Select(attrs={
                'class': 'form-control'
            }),
            'deposit_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Security deposit amount'
            }),
            'utilities_included': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_furnished': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pets_allowed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'smoking_allowed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop('owner', None)
        super().__init__(*args, **kwargs)
        
        # Initialize district field
        if 'district' in self.fields:
            self.fields['district'].empty_label = "Select District (select region first)"
            self.fields['district'].queryset = District.objects.none()  # Start with empty queryset
            
            # If editing existing property, load districts for the property's region
            if self.instance and self.instance.pk and self.instance.region:
                self.fields['district'].queryset = District.objects.filter(region=self.instance.region)
            # If region is provided in POST data (for new properties), load districts for that region
            elif self.data and 'region' in self.data and self.data.get('region'):
                try:
                    region_id = int(self.data.get('region'))
                    self.fields['district'].queryset = District.objects.filter(region_id=region_id)
                except (ValueError, TypeError):
                    pass
        
        # Set default rent_period for lodges (per day)
        if 'rent_period' in self.fields and not self.instance.pk:
            self.fields['rent_period'].initial = 'day'
        
        # Set owner if provided
        if self.owner:
            self.instance.owner = self.owner


class VenuePropertyForm(BasePropertyForm):
    """Form specifically for Venue properties"""
    
    class Meta(BasePropertyForm.Meta):
        fields = BasePropertyForm.Meta.fields + [
            'capacity', 'venue_type', 'bathrooms', 'rent_amount', 'rent_period', 'deposit_amount'
        ]
        
        widgets = {
            **BasePropertyForm.Meta.widgets,
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Maximum capacity'
            }),
            'venue_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Conference, Wedding, Meeting'
            }),
            'bathrooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'rent_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Rate per event'
            }),
            'rent_period': forms.Select(attrs={
                'class': 'form-control'
            }),
            'deposit_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Security deposit amount'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop('owner', None)
        super().__init__(*args, **kwargs)
        
        # Initialize district field
        if 'district' in self.fields:
            self.fields['district'].empty_label = "Select District (select region first)"
            self.fields['district'].queryset = District.objects.none()  # Start with empty queryset
            
            # If editing existing property, load districts for the property's region
            if self.instance and self.instance.pk and self.instance.region:
                self.fields['district'].queryset = District.objects.filter(region=self.instance.region)
            # If region is provided in POST data (for new properties), load districts for that region
            elif self.data and 'region' in self.data and self.data.get('region'):
                try:
                    region_id = int(self.data.get('region'))
                    self.fields['district'].queryset = District.objects.filter(region_id=region_id)
                except (ValueError, TypeError):
                    pass
        
        # Set default rent_period for venues (per day)
        if 'rent_period' in self.fields and not self.instance.pk:
            self.fields['rent_period'].initial = 'day'
        
        # Set owner if provided
        if self.owner:
            self.instance.owner = self.owner


# Keep the original PropertyForm for backward compatibility
class PropertyForm(BasePropertyForm):
    """Form for creating and editing properties (backward compatibility)"""
    
    class Meta(BasePropertyForm.Meta):
        fields = [
            'title', 'description', 'property_type', 'region', 'district', 'address',
            'latitude', 'longitude', 'bedrooms', 'bathrooms', 'size_sqft',
            'floor_number', 'total_floors', 'total_rooms', 'room_types',
            'capacity', 'venue_type', 'rent_amount', 'deposit_amount',
            'utilities_included', 'status', 'is_featured', 'is_furnished',
            'pets_allowed', 'smoking_allowed', 'available_from', 'amenities'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter property title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the property...'
            }),
            'property_type': forms.Select(attrs={'class': 'form-control'}),
            'region': forms.Select(attrs={'class': 'form-control', 'id': 'id_region'}),
            'district': forms.Select(attrs={'class': 'form-control', 'id': 'id_district'}),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter full address'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'placeholder': 'Latitude'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'placeholder': 'Longitude'
            }),
            'bedrooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'bathrooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'total_rooms': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Total number of rooms'
            }),
            'room_types': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'JSON format: {"Single": 10, "Double": 5, "Suite": 2}'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Maximum capacity'
            }),
            'venue_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Conference, Wedding, Meeting'
            }),
            'size_sqft': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Size in square feet'
            }),
            'floor_number': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'total_floors': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'rent_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Monthly rent amount'
            }),
            'deposit_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Security deposit amount'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'available_from': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'amenities': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'utilities_included': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_furnished': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pets_allowed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'smoking_allowed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
        help_texts = {
            'size_sqft': 'Enter the total area in square feet',
            'utilities_included': 'Check if utilities (water, electricity, etc.) are included in rent',
            'is_featured': 'Featured properties will be highlighted in listings',
            'deposit_amount': 'Leave blank if no deposit required',
        }
    
    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop('owner', None)
        super().__init__(*args, **kwargs)
        
        # Make certain fields required
        self.fields['property_type'].empty_label = "Select Property Type"
        self.fields['region'].empty_label = "Select Region"
        
        # Set owner if provided
        if self.owner:
            self.instance.owner = self.owner
        
        # Add JavaScript for dynamic field visibility
        self.fields['property_type'].widget.attrs.update({
            'onchange': 'togglePropertyFields(this.value)'
        })
        
        # Initially hide type-specific fields
        self.fields['total_rooms'].widget.attrs.update({'style': 'display: none;'})
        self.fields['room_types'].widget.attrs.update({'style': 'display: none;'})
        self.fields['capacity'].widget.attrs.update({'style': 'display: none;'})
        self.fields['venue_type'].widget.attrs.update({'style': 'display: none;'})
        
        # Make bedrooms optional for venues
        self.fields['bedrooms'].required = False
        self.fields['bathrooms'].required = False
    
    def clean_district(self):
        """Validate that district belongs to the selected region"""
        district = self.cleaned_data.get('district')
        region = self.cleaned_data.get('region')
        
        if district and region:
            if district.region != region:
                raise forms.ValidationError(
                    "Selected district does not belong to the selected region. Please select a valid district."
                )
        
        return district
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validate that floor_number is not greater than total_floors
        floor_number = cleaned_data.get('floor_number')
        total_floors = cleaned_data.get('total_floors')
        
        if floor_number and total_floors and floor_number > total_floors:
            raise forms.ValidationError(
                "Floor number cannot be greater than total floors."
            )
        
        # Validate district belongs to region (if both are provided)
        district = cleaned_data.get('district')
        region = cleaned_data.get('region')
        if district and region and district.region != region:
            raise forms.ValidationError({
                'district': "Selected district does not belong to the selected region."
            })
        
        return cleaned_data


class PropertyImageForm(forms.ModelForm):
    """Form for property images"""
    
    class Meta:
        model = PropertyImage
        fields = ['image', 'caption', 'is_primary', 'order']
        
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'caption': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Image caption (optional)'
            }),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'value': '0'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make image optional when editing (if instance exists)
        if self.instance and self.instance.pk:
            self.fields['image'].required = False
        
        help_texts = {
            'is_primary': 'Primary image will be used as the main property photo',
            'order': 'Display order (0 = first, 1 = second, etc.)'
        }


class PropertySearchForm(forms.Form):
    """Form for searching properties"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search properties...'
        })
    )
    
    property_type = forms.ModelChoiceField(
        queryset=PropertyType.objects.all(),
        required=False,
        empty_label="Any Type",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        empty_label="Any Region",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    district = forms.ModelChoiceField(
        queryset=District.objects.all(),
        required=False,
        empty_label="Any District",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_district_filter'})
    )
    
    min_bedrooms = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min bedrooms'
        })
    )
    
    max_bedrooms = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max bedrooms'
        })
    )
    
    min_rent = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min rent',
            'step': '0.01'
        })
    )
    
    max_rent = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max rent',
            'step': '0.01'
        })
    )
    
    is_furnished = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    pets_allowed = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    amenities = forms.ModelMultipleChoiceField(
        queryset=Amenity.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )


class RegionForm(forms.ModelForm):
    """Form for creating and editing regions"""
    
    class Meta:
        model = Region
        fields = ['name', 'description']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Region name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description (optional)'
            })
        }


class DistrictForm(forms.ModelForm):
    """Form for creating and editing districts"""
    
    class Meta:
        model = District
        fields = ['name', 'region', 'description']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'District name'
            }),
            'region': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select region'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description (optional)'
            })
        }


class PropertyTypeForm(forms.ModelForm):
    """Form for creating and editing property types"""
    
    class Meta:
        model = PropertyType
        fields = ['name', 'description']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Property type name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description (optional)'
            })
        }


class AmenityForm(forms.ModelForm):
    """Form for creating and editing amenities"""
    
    class Meta:
        model = Amenity
        fields = ['name', 'description', 'icon']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Amenity name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description (optional)'
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Icon name (optional)'
            })
        }
        
        help_texts = {
            'icon': 'Icon name for mobile app (e.g., wifi, parking, gym)'
        }


# Formset for handling multiple property images
PropertyImageFormSet = forms.inlineformset_factory(
    Property,
    PropertyImage,
    form=PropertyImageForm,
    extra=1,  # Reduced from 3 to minimize empty forms
    can_delete=True,
    max_num=10,
    validate_min=False,  # Don't require minimum number of forms
    min_num=0  # Allow zero forms (for editing without new images)
)