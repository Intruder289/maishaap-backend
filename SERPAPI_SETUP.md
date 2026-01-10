# SerpApi Integration Setup Guide

## Overview

The property management system has been updated to use **SerpApi** for Google Maps geocoding instead of OpenStreetMap. This provides better accuracy, especially for Tanzania addresses.

## What Was Changed

1. **Replaced OpenStreetMap geocoding** with SerpApi Google Maps API
2. **Added fallback mechanism** - If SerpApi is not configured, it automatically falls back to OpenStreetMap
3. **Updated requirements.txt** - Added `google-search-results==2.4.2`
4. **Updated settings.py** - Added `SERPAPI_KEY` configuration

## Setup Instructions

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install `google-search-results` package.

### Step 2: Get Your SerpApi API Key

1. Sign up at https://serpapi.com/
2. Go to your dashboard: https://serpapi.com/dashboard
3. Copy your API key

### Step 3: Add API Key to Environment

Add your SerpApi API key to your `.env` file:

```env
SERPAPI_KEY=your_api_key_here
```

**OR** if you're not using `.env` file, add directly to `settings.py`:

```python
SERPAPI_KEY = 'your_api_key_here'
```

### Step 4: Restart Your Django Server

```bash
python manage.py runserver
```

## How It Works

### Primary: SerpApi (Google Maps)
- When `SERPAPI_KEY` is configured, the system uses SerpApi
- Provides better accuracy for Tanzania addresses
- Uses Google Maps data through SerpApi

### Fallback: OpenStreetMap
- If `SERPAPI_KEY` is not set or SerpApi fails, automatically falls back to OpenStreetMap
- Free, no API key required
- Good for testing or as backup

## Usage

The geocoding functionality works exactly the same as before:

1. **In Property Form**: Click "Get Coordinates" button to auto-fill latitude/longitude
2. **API Endpoint**: `/properties/geocode-address/` - POST endpoint for geocoding addresses

## Features

- ✅ Automatic fallback to OpenStreetMap if SerpApi unavailable
- ✅ Better accuracy for Tanzania addresses
- ✅ No changes needed to existing code
- ✅ Same API interface - drop-in replacement

## Cost Information

SerpApi Plans:
- **Free**: 250 searches/month (for testing)
- **Starter**: $25/month - 1,000 searches
- **Developer**: $75/month - 5,000 searches
- **Production**: $150/month - 15,000 searches

For a property management system:
- Small (100-500 properties): Free tier or Starter
- Medium (500-2,000 properties): Developer
- Large (2,000+ properties): Production

## Testing

1. Without API key: System will use OpenStreetMap (fallback)
2. With API key: System will use SerpApi (Google Maps)

Both work seamlessly - you can test immediately without an API key!

## Files Modified

- `requirements.txt` - Added google-search-results package
- `Maisha_backend/settings.py` - Added SERPAPI_KEY configuration
- `properties/utils.py` - Replaced geocoding functions with SerpApi

## Support

- SerpApi Documentation: https://serpapi.com/
- SerpApi Dashboard: https://serpapi.com/dashboard
- Contact: contact@serpapi.com

