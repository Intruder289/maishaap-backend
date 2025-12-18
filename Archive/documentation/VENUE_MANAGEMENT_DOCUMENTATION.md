# Venue Management System Documentation

## Overview

The Venue Management System is a comprehensive solution for managing event venues, bookings, and related operations within the Maisha Property Management System. It provides both web-based administration and API endpoints for mobile integration.

## Features

### 🏢 Core Functionality
- **Venue Dashboard**: Real-time overview of venue operations, bookings, and revenue
- **Booking Management**: Complete booking lifecycle from creation to completion
- **Availability Management**: Calendar view and real-time availability checking
- **Customer Management**: Track venue customers and their booking history
- **Payment Processing**: Handle venue booking payments and invoicing
- **Analytics & Reporting**: Comprehensive venue performance metrics

### 🔧 Technical Features
- **Real-time Data Integration**: Live updates of venue status and bookings
- **API Endpoints**: RESTful APIs for mobile app integration
- **Capacity Management**: Automatic capacity checking and overflow handling
- **Status Workflow**: Automated booking status transitions
- **Multi-venue Support**: Manage multiple venues from single interface
- **Responsive Design**: Mobile-friendly interface

## System Architecture

### Models
The venue management system uses the existing Property model with venue-specific fields:

```python
# Venue-specific fields in Property model
capacity = models.PositiveIntegerField(help_text="Maximum capacity (for venues)")
venue_type = models.CharField(max_length=100, help_text="Type of venue")
```

### Views
- `venue_dashboard`: Main dashboard with statistics and today's events
- `venue_bookings`: Booking management interface
- `venue_availability`: Availability calendar and scheduling
- `venue_customers`: Customer management for venues
- `venue_payments`: Payment processing and tracking
- `venue_reports`: Analytics and reporting

### API Endpoints
- `api_venue_availability`: Get venue availability data
- `api_venue_booking_status`: Update booking status
- `api_venue_capacity_check`: Check venue capacity availability
- `api_venue_analytics`: Get venue performance metrics

## Usage Guide

### 1. Venue Dashboard

The venue dashboard provides a comprehensive overview of venue operations:

**Features:**
- Real-time statistics (total venues, bookings, revenue)
- Today's events and upcoming events
- Venue availability status
- Quick action buttons for common tasks

**Access:** `/properties/venue/dashboard/`

### 2. Booking Management

Manage venue bookings with full lifecycle support:

**Booking Statuses:**
- `pending`: New booking awaiting confirmation
- `confirmed`: Booking confirmed and ready
- `checked_in`: Event in progress
- `completed`: Event finished
- `cancelled`: Booking cancelled

**Actions Available:**
- View booking details
- Edit booking information
- Confirm pending bookings
- Start/end events
- Cancel bookings
- Generate invoices

**Access:** `/properties/venue/bookings/`

### 3. Availability Management

Monitor and manage venue availability:

**Features:**
- Calendar view of venue availability
- Real-time availability checking
- Venue blocking for maintenance
- Conflict detection and resolution

**Access:** `/properties/venue/availability/`

### 4. Customer Management

Track venue customers and their booking history:

**Features:**
- Customer profiles and contact information
- Booking history per customer
- VIP status management
- Customer analytics

**Access:** `/properties/venue/customers/`

### 5. Payment Processing

Handle venue booking payments:

**Features:**
- Payment tracking and status
- Receipt generation
- Payment reminders
- Refund processing

**Access:** `/properties/venue/payments/`

## API Documentation

### Venue Availability API

**Endpoint:** `GET /properties/api/venue/availability/`

**Parameters:**
- `venue_id` (optional): Specific venue ID
- `start_date` (optional): Start date (YYYY-MM-DD)
- `end_date` (optional): End date (YYYY-MM-DD)

**Response:**
```json
{
    "success": true,
    "venues": [
        {
            "id": 1,
            "title": "Conference Hall A",
            "capacity": 50,
            "status": "available",
            "bookings": [...]
        }
    ],
    "date_range": {
        "start": "2024-01-15",
        "end": "2024-01-22"
    }
}
```

### Booking Status API

**Endpoint:** `POST /properties/api/venue/booking/{booking_id}/status/`

**Parameters:**
- `action`: Status action (confirm, start, end, cancel)
- `status` (optional): Direct status update

**Response:**
```json
{
    "success": true,
    "message": "Booking confirmed successfully"
}
```

### Capacity Check API

**Endpoint:** `GET /properties/api/venue/capacity-check/`

**Parameters:**
- `venue_id`: Venue ID
- `event_date`: Event date (YYYY-MM-DD)
- `guest_count`: Number of guests
- `exclude_booking_id` (optional): Booking ID to exclude from conflict check

**Response:**
```json
{
    "success": true,
    "available": true,
    "message": "Venue is available for booking",
    "venue": {
        "id": 1,
        "title": "Conference Hall A",
        "capacity": 50
    }
}
```

### Analytics API

**Endpoint:** `GET /properties/api/venue/analytics/`

**Parameters:**
- `venue_id` (optional): Specific venue ID
- `period`: Time period (week, month, quarter, year)

**Response:**
```json
{
    "success": true,
    "analytics": [
        {
            "venue_id": 1,
            "venue_title": "Conference Hall A",
            "period": "month",
            "date_range": {
                "start": "2024-01-01",
                "end": "2024-01-31"
            },
            "metrics": {
                "total_bookings": 15,
                "confirmed_bookings": 12,
                "completed_bookings": 10,
                "cancelled_bookings": 1,
                "total_revenue": 7500.00,
                "average_guests": 35.5,
                "occupancy_rate": 78.2
            }
        }
    ]
}
```

## JavaScript Integration

### Event Management Functions

```javascript
// Start an event
function startEvent(bookingId) {
    $.post(`/properties/api/venue/booking/${bookingId}/status/`, {
        action: 'start',
        csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
    }, function(response) {
        if (response.success) {
            showNotification('Event started successfully', 'success');
            location.reload();
        }
    });
}

// Check venue capacity
function checkVenueCapacity(venueId, guestCount) {
    $.get('/properties/api/venue/capacity-check/', {
        venue_id: venueId,
        guest_count: guestCount
    }, function(response) {
        if (response.success && response.available) {
            // Show success message
        } else {
            // Show error message
        }
    });
}
```

## Configuration

### Venue Types
Configure venue types in the PropertyType model:
- Conference
- Wedding
- Meeting
- Party
- Seminar
- Team Building

### Booking Status Workflow
1. `pending` → `confirmed` (manual confirmation)
2. `confirmed` → `checked_in` (event start)
3. `checked_in` → `completed` (event end)
4. Any status → `cancelled` (cancellation)

### Payment Integration
The system integrates with the existing Payment model for:
- Payment tracking
- Receipt generation
- Refund processing
- Payment reminders

## Testing

### Test Script
Run the comprehensive test script:
```bash
python test_venue_management_comprehensive.py
```

### Test Coverage
- Venue dashboard functionality
- Booking management operations
- API endpoint responses
- Data integration
- User interface components

## Security

### Authentication
- All views require user authentication (`@login_required`)
- API endpoints require authentication
- CSRF protection on all forms

### Authorization
- Users can only manage venues they own
- Admin users can manage all venues
- Role-based access control

## Performance

### Optimization Features
- Database query optimization with `select_related` and `prefetch_related`
- Pagination for large datasets
- Caching for frequently accessed data
- Real-time updates without full page reloads

### Scalability
- Support for unlimited venues
- Efficient booking conflict detection
- Optimized calendar rendering
- API rate limiting

## Troubleshooting

### Common Issues

**Issue:** Venue dashboard shows no data
**Solution:** Ensure venues have `property_type.name = 'venue'`

**Issue:** Booking status not updating
**Solution:** Check API endpoint permissions and CSRF token

**Issue:** Capacity check failing
**Solution:** Verify venue capacity is set and guest count is valid

### Debug Mode
Enable debug logging in settings:
```python
LOGGING = {
    'loggers': {
        'properties.venue': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

## Future Enhancements

### Planned Features
- Advanced calendar integration
- Automated booking confirmations
- Equipment management system
- Multi-language support
- Mobile app integration
- Advanced analytics dashboard
- Automated invoicing
- Customer communication system

### Integration Opportunities
- Calendar applications (Google Calendar, Outlook)
- Payment gateways (Stripe, PayPal)
- Email marketing platforms
- CRM systems
- Accounting software

## Support

For technical support or feature requests:
- Check the test script for functionality verification
- Review API documentation for integration issues
- Consult the troubleshooting section for common problems
- Contact the development team for advanced support

---

**Last Updated:** January 2024
**Version:** 1.0
**Compatibility:** Django 4.x, Python 3.8+
