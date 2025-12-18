# Project Cleanup Analysis

This document identifies unused files, test files, empty folders, and markdown documentation files that can be cleaned up.

## 1. UNUSED HTML TEMPLATES

### Root Level Test Files
- `test_modals.html` - Standalone test file in root

### Properties Templates Not Rendered
Based on views.py analysis, these templates exist but are NOT rendered by any view:

- `properties/templates/properties/property_list_old.html` - Old version, replaced by property_list.html
- `properties/templates/properties/property_list_new.html` - New version placeholder, not used
- `properties/templates/properties/test_bookings.html` - Test file referenced by URL but not actively used
- `properties/templates/properties/test_template.html` - Test template

### Account Templates
- `accounts/templates/accounts/user_roles.html` - NOT found in render() calls, likely unused modal

### Missing Templates Referenced in Views
These views reference templates but files don't exist (from rent app):
- `rent/templates/rent/invoice_list.html` - Referenced but may not exist
- `rent/templates/rent/tenant_summary.html` - Referenced but may not exist

---

## 2. TEST FILES (36 files)

### Root Level Test Files
All these should be moved to a `tests/` directory or removed if obsolete:

1. `test_apis_with_auth.py`
2. `test_apis.py`
3. `test_authenticated_modals.py`
4. `test_authenticated.py`
5. `test_client_property_selection.py`
6. `test_client.py`
7. `test_context.py`
8. `test_data_check.py`
9. `test_detailed_property_selection.py`
10. `test_detailed.py`
11. `test_enhanced_property_upload.py`
12. `test_fixed_functionality.py`
13. `test_house_management_comprehensive.py`
14. `test_house_rent_reminder_system.py`
15. `test_house.py`
16. `test_hotel_only.py`
17. `test_image_upload.py`
18. `test_lodge.py`
19. `test_management_system.py`
20. `test_mobile_signup_activation.py`
21. `test_property_image_functionality.py`
22. `test_property_selection.py`
23. `test_rent_navigation.py`
24. `test_rent_reminder_dashboard.py`
25. `test_response_content.py`
26. `test_role_based_api.py`
27. `test_room_api.py`
28. `test_room_modals.py`
29. `test_template_content.py`
30. `test_template_debug.py`
31. `test_template_property_selection.py`
32. `test_template_rendering.py`
33. `test_template.py`
34. `test_venue_management_comprehensive.py`
35. `test_venue.py`
36. `test_mobile_flow.ps1` - PowerShell test script

### Test Image Files
- `test_property_image_1.jpg`
- `test_property_image_2.jpg`
- `test_property_image_3.jpg`

### Other Test/Helper Scripts
- `approve_test_user.py`
- `approve_user.sql`
- `check_swagger_urls.py`
- `check_template.py`
- `check_test_users.py`
- `check_user_credentials.py`
- `check_users.py`
- `assign_tenant_role.py`
- `create_users.py`
- `comprehensive_test.py`
- `debug_user_roles.py`
- `fix_swagger_errors.py`
- `fix_swagger_targeted.py`
- `fix_test_user_approval.py`

---

## 3. EMPTY OR UNUSED DIRECTORIES

### Verified Empty Directories
These directories are confirmed empty:

- `accounts/templates/accounts/img/` - **EMPTY** (no files found)
- `secrets/` - **EMPTY** (no files found)

### Potential Empty Directories
- `assets/` - Large directory with images, likely contains assets but check if all needed

---

## 4. MARKDOWN DOCUMENTATION FILES (.md)

### Root Level MD Files (44 files)

#### Setup & Configuration
1. `API_DOCUMENTATION.md` - Main API docs (KEEP)
2. `SETUP.md` - Setup instructions (KEEP)

#### Test Documentation
3. `API_TEST_RESULTS.md` - Test results (MOVABLE TO tests/)
4. `AUTHENTICATION_TEST_SUMMARY.md` - Test summary (MOVABLE TO tests/)
5. `COMPLETE_API_TEST_SUMMARY.md` - Test summary (MOVABLE TO tests/)
6. `MOBILE_SIGNUP_TEST_GUIDE.md` - Test guide (MOVABLE TO tests/)
7. `MOBILE_TESTING_GUIDE.md` - Test guide (MOVABLE TO tests/)
8. `TEST_SWAGGER_GUIDE.md` - Test guide (MOVABLE TO tests/)
9. `SWAGGER_TESTING_GUIDE.md` - Test guide (MOVABLE TO tests/)

#### API Documentation
10. `COMPLETE_TENANT_API_DOCUMENTATION.md` - API docs (KEEP)
11. `FLUTTER_MOBILE_API_DOCUMENTATION.md` - API docs (KEEP)
12. `TENANT_API_QUICK_REFERENCE.md` - Reference (KEEP)
13. `TENANT_API_REFERENCE.md` - Reference (KEEP)

#### Feature Documentation
14. `DASHBOARD_IMPROVEMENTS.md` - Feature docs (ARCHIVE)
15. `INVOICE_MODAL_OVERLAY_FIX.md` - Bug fix doc (ARCHIVE)
16. `INVOICE_MODAL_STYLING_UPDATE.md` - Bug fix doc (ARCHIVE)
17. `COLLAPSED_SIDEBAR_FIX.md` - Bug fix doc (ARCHIVE)
18. `MOBILE_SIDEBAR_FIX.md` - Bug fix doc (ARCHIVE)
19. `METADATA_DELETE_FEATURE.md` - Feature doc (ARCHIVE)
20. `PROFILE_PHOTO_IMPLEMENTATION.md` - Feature doc (ARCHIVE)
21. `PROPERTY_TYPES_SUMMARY.md` - Feature summary (ARCHIVE)
22. `PROPERTY_TYPE_API_GUIDE.md` - Feature guide (ARCHIVE)
23. `DOCUMENTS_MODULE_SUMMARY.md` - Module summary (ARCHIVE)
24. `VENUE_MANAGEMENT_DOCUMENTATION.md` - Module docs (KEEP if active)
25. `HOUSE_RENT_REMINDER_SYSTEM.md` - Feature docs (KEEP if active)
26. `RENT_REMINDER_INTEGRATION_GUIDE.md` - Integration guide (ARCHIVE)

#### Permission & Role Documentation
27. `PERMISSION_ARCHITECTURE.md` - Architecture (KEEP)
28. `PERMISSION_MIDDLEWARE_FIX.md` - Bug fix doc (ARCHIVE)
29. `PERMISSION_MIDDLEWARE_GUIDE.md` - Guide (ARCHIVE)
30. `PERMISSION_MIDDLEWARE_SUMMARY.md` - Summary (ARCHIVE)
31. `PERMISSION_QUICK_REFERENCE.md` - Reference (KEEP)
32. `ROLE_MODAL_BODY_MOVE_FIX.md` - Bug fix doc (ARCHIVE)
33. `ROLE_MODAL_FULLSCREEN_FIX.md` - Bug fix doc (ARCHIVE)
34. `ROLE_MODAL_UPGRADE.md` - Feature doc (ARCHIVE)
35. `USER_MODAL_FULLSCREEN_FIX.md` - Bug fix doc (ARCHIVE)

#### Styling & UI
36. `SIDEBAR_BEFORE_AFTER.md` - UI change doc (ARCHIVE)
37. `RESPONSIVE_DASHBOARD_GUIDE.md` - Guide (ARCHIVE)
38. `TEMPLATE_UPDATES.md` - Update doc (ARCHIVE)

#### Module-Specific
39. `documents/TEMPLATE_OPTIMIZATION.md` - Template doc (ARCHIVE)
40. `documents/README.md` - Module README (KEEP)
41. `payments/README.md` - Module README (KEEP)
42. `accounts/ROLE_README.md` - Module README (KEEP)
43. `staticfiles/admin/js/vendor/select2/LICENSE.md` - Third-party license (KEEP)
44. `staticfiles/admin/css/vendor/select2/LICENSE-SELECT2.md` - Third-party license (KEEP)

---

## 5. UNUSED PYTHON FILES

### Scripts in Root Directory
These appear to be one-time utility scripts:

- `approve_test_user.py`
- `approve_user.sql`
- `assign_tenant_role.py`
- `check_swagger_urls.py`
- `check_template.py`
- `check_test_users.py`
- `check_user_credentials.py`
- `check_users.py`
- `create_users.py`
- `comprehensive_test.py`
- `debug_user_roles.py`
- `fix_swagger_errors.py`
- `fix_swagger_targeted.py`
- `fix_test_user_approval.py`

### Batch Files
- `install_api_deps.bat` - Setup script (KEEP for reference)

---

## 6. POTENTIALLY UNUSED PYTHON FILES

### Accounts Module
Looking at accounts directory, there are multiple API views files that may be duplicates:

- `accounts/api_views.py` - Main API views (USED in api_urls.py)
- `accounts/api_views_ajax.py` - AJAX views for HTML templates (USED in api_urls.py)
- `accounts/api_views_clean.py` - Clean version (NOT USED - can be deleted)

**Verification**: Grep search confirms `api_views_clean.py` is NOT imported anywhere in the codebase.

---

## 7. CLEANUP RECOMMENDATIONS

### Priority 1: Create Tests Directory
```bash
mkdir tests
mkdir tests/unit
mkdir tests/integration
mkdir tests/docs
```

### Priority 2: Move Test Files
Move all `test_*.py` files to `tests/unit/` or `tests/integration/`

### Priority 3: Archive Documentation
Create a `docs/archive/` directory for historical/bug fix documentation:
- Move all `*_FIX.md` files
- Move all `*_SUMMARY.md` files that are historical
- Move all `*_GUIDE.md` files for old features

### Priority 4: Remove Unused Templates
- Delete `property_list_old.html`
- Delete `property_list_new.html`
- Delete `test_bookings.html`
- Delete `test_template.html`
- Delete `test_modals.html`

### Priority 5: Clean Up Scripts
Move utility scripts to `scripts/` directory:
- All check_*.py files
- All fix_*.py files
- approve_*.py files

### Priority 6: Delete Confirmed Unused Files
- `accounts/api_views_clean.py` - NOT imported anywhere
- `accounts/templates/accounts/user_roles.html` - NOT referenced in views

---

## 8. SUMMARY STATISTICS

- **Test Files**: ~36 in root directory
- **Test Images**: 3 JPG files
- **Unused HTML**: ~5 templates
- **Helper Scripts**: ~15 files
- **MD Documentation**: 44 files total
  - Keep: ~15 essential docs
  - Archive: ~20 historical/bug fix docs
  - Move to tests/: ~8 test guides
- **Empty Directories**: 1-2 (needs verification)

---

## 9. SUGGESTED DIRECTORY STRUCTURE

```
Maisha_backend/
├── tests/
│   ├── unit/
│   │   └── [all test_*.py files]
│   ├── integration/
│   │   └── [comprehensive test files]
│   └── docs/
│       └── [test guides moved here]
├── docs/
│   ├── API_DOCUMENTATION.md
│   ├── SETUP.md
│   ├── [active feature docs]
│   └── archive/
│       └── [historical/bug fix docs]
├── scripts/
│   ├── check_*.py
│   ├── fix_*.py
│   └── approve_*.py
└── [rest of project structure]
```

---

Generated: Analysis of Maisha_backend project
Date: Current analysis

