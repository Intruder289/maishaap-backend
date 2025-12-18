# Quick Cleanup Summary - Files and Folders to Remove/Archive

## 🗑️ FILES TO DELETE IMMEDIATELY

### Empty Directories (Confirmed Empty)
```
accounts/templates/accounts/img/    ← EMPTY (can delete)
secrets/                             ← EMPTY (can delete)
```

### Unused HTML Templates
```
properties/templates/properties/
  ├── property_list_old.html         ← Old version
  ├── property_list_new.html         ← Unused placeholder
  ├── test_bookings.html            ← Test file
  └── test_template.html             ← Test file

accounts/templates/accounts/
  └── user_roles.html                ← Not referenced in views.py

[ROOT]
  └── test_modals.html                ← Test file
```

### Unused Python Files
```
accounts/api_views_clean.py          ← NOT imported anywhere
```

---

## 📦 FILES TO ARCHIVE/MOVE

### Test Files - Move to `tests/` directory (36 files)

**Create these directories first:**
```bash
mkdir tests
mkdir tests/unit
mkdir tests/integration
mkdir tests/test_images
```

**Files to move:**
```
tests/unit/
├── test_apis_with_auth.py
├── test_apis.py
├── test_authenticated_modals.py
├── test_authenticated.py
├── test_client_property_selection.py
├── test_client.py
├── test_context.py
├── test_data_check.py
├── test_detailed_property_selection.py
├── test_detailed.py
├── test_enhanced_property_upload.py
├── test_fixed_functionality.py
├── test_hotel_only.py
├── test_image_upload.py
├── test_management_system.py
├── test_property_image_functionality.py
├── test_property_selection.py
├── test_template_content.py
├── test_template_debug.py
├── test_template_property_selection.py
├── test_template_rendering.py
├── test_template.py
└── test_response_content.py

tests/integration/
├── test_house_management_comprehensive.py
├── test_house_rent_reminder_system.py
├── test_house.py
├── test_lodge.py
├── test_rent_navigation.py
├── test_rent_reminder_dashboard.py
├── test_role_based_api.py
├── test_room_api.py
├── test_room_modals.py
├── test_venue_management_comprehensive.py
└── test_venue.py

tests/test_images/
├── test_property_image_1.jpg
├── test_property_image_2.jpg
└── test_property_image_3.jpg

tests/
└── test_mobile_signup_activation.py

[tests/docs/]
└── (copy test documentation .md files here)
```

### Helper Scripts - Move to `scripts/` directory

**Create directory:**
```bash
mkdir scripts
```

**Files to move:**
```
scripts/
├── approve_test_user.py
├── approve_user.sql
├── assign_tenant_role.py
├── check_swagger_urls.py
├── check_template.py
├── check_test_users.py
├── check_user_credentials.py
├── check_users.py
├── comprehensive_test.py
├── create_users.py
├── debug_user_roles.py
├── fix_swagger_errors.py
├── fix_swagger_targeted.py
└── fix_test_user_approval.py
```

---

## 📄 MARKDOWN FILES TO ARCHIVE

### Create archive directory:
```bash
mkdir docs
mkdir docs/archive
```

### Move to `docs/archive/` (Historical/Bug fixes):
```
docs/archive/
├── API_TEST_RESULTS.md
├── AUTHENTICATION_TEST_SUMMARY.md
├── COLLAPSED_SIDEBAR_FIX.md
├── COMPLETE_API_TEST_SUMMARY.md
├── DASHBOARD_IMPROVEMENTS.md
├── DOCUMENTS_MODULE_SUMMARY.md
├── INVOICE_MODAL_OVERLAY_FIX.md
├── INVOICE_MODAL_STYLING_UPDATE.md
├── METADATA_DELETE_FEATURE.md
├── MOBILE_SIDEBAR_FIX.md
├── PERMISSION_MIDDLEWARE_FIX.md
├── PERMISSION_MIDDLEWARE_GUIDE.md
├── PERMISSION_MIDDLEWARE_SUMMARY.md
├── PROFILE_PHOTO_IMPLEMENTATION.md
├── PROPERTY_TYPES_SUMMARY.md
├── PROPERTY_TYPE_API_GUIDE.md
├── RESPONSIVE_DASHBOARD_GUIDE.md
├── ROLE_MODAL_BODY_MOVE_FIX.md
├── ROLE_MODAL_FULLSCREEN_FIX.md
├── ROLE_MODAL_UPGRADE.md
├── RENT_REMINDER_INTEGRATION_GUIDE.md
├── SIDEBAR_BEFORE_AFTER.md
├── TEMPLATE_UPDATES.md
├── USER_MODAL_FULLSCREEN_FIX.md
└── documents/TEMPLATE_OPTIMIZATION.md
```

### Move to `tests/docs/`:
```
tests/docs/
├── MOBILE_SIGNUP_TEST_GUIDE.md
├── MOBILE_TESTING_GUIDE.md
├── SWAGGER_TESTING_GUIDE.md
└── TEST_SWAGGER_GUIDE.md
```

### Keep in root (Active documentation):
```
✅ API_DOCUMENTATION.md
✅ SETUP.md
✅ COMPLETE_TENANT_API_DOCUMENTATION.md
✅ FLUTTER_MOBILE_API_DOCUMENTATION.md
✅ TENANT_API_QUICK_REFERENCE.md
✅ TENANT_API_REFERENCE.md
✅ PERMISSION_ARCHITECTURE.md
✅ PERMISSION_QUICK_REFERENCE.md
✅ VENUE_MANAGEMENT_DOCUMENTATION.md
✅ HOUSE_RENT_REMINDER_SYSTEM.md
✅ accounts/ROLE_README.md
✅ documents/README.md
✅ payments/README.md
```

### Keep in staticfiles (Third-party licenses):
```
✅ staticfiles/admin/js/vendor/select2/LICENSE.md
✅ staticfiles/admin/css/vendor/select2/LICENSE-SELECT2.md
```

---

## 📊 SUMMARY STATISTICS

| Category | Count | Action |
|----------|-------|--------|
| **Files to Delete** | 8 | Delete immediately |
| **Empty Directories** | 2 | Delete |
| **Test Files to Move** | 36 | Move to `tests/` |
| **Helper Scripts to Move** | 14 | Move to `scripts/` |
| **MD Files to Archive** | ~24 | Move to `docs/archive/` |
| **MD Files to Keep** | ~15 | Keep in root/app |
| **Total Files to Handle** | ~99 | Various actions |

---

## 🚀 QUICK CLEANUP COMMANDS

```powershell
# 1. Create directory structure
mkdir tests, tests\unit, tests\integration, tests\test_images, tests\docs
mkdir scripts
mkdir docs, docs\archive

# 2. Move test files
Move-Item test_*.py tests\unit\
Move-Item test_property_image*.jpg tests\test_images\

# 3. Move helper scripts
Move-Item approve_*.py scripts\
Move-Item check_*.py scripts\
Move-Item fix_*.py scripts\
Move-Item create_users.py scripts\
Move-Item assign_tenant_role.py scripts\
Move-Item comprehensive_test.py scripts\
Move-Item debug_user_roles.py scripts\

# 4. Move documentation files
Move-Item *FIX.md docs\archive\
Move-Item *GUIDE.md docs\archive\
Move-Item *SUMMARY.md docs\archive\
Move-Item TEMPLATE_*.md docs\archive\
Move-Item MOBILE_TESTING_GUIDE.md tests\docs\
Move-Item TEST_*.md tests\docs\

# 5. Delete empty directories
Remove-Item accounts\templates\accounts\img -Force
Remove-Item secrets -Force

# 6. Delete unused files
Remove-Item accounts\api_views_clean.py
Remove-Item properties\templates\properties\property_list_old.html
Remove-Item properties\templates\properties\property_list_new.html
Remove-Item properties\templates\properties\test_*.html
Remove-Item accounts\templates\accounts\user_roles.html
Remove-Item test_modals.html
```

---

## 📋 VERIFICATION CHECKLIST

- [ ] Created `tests/` directory structure
- [ ] Created `scripts/` directory
- [ ] Created `docs/archive/` directory
- [ ] Moved all test_*.py files
- [ ] Moved all helper scripts
- [ ] Moved historical .md files to archive
- [ ] Deleted empty directories
- [ ] Deleted unused HTML templates
- [ ] Deleted unused Python files
- [ ] Verified project still runs
- [ ] Updated any hardcoded paths in scripts
- [ ] Updated README if needed

---

**After cleanup, your project structure will be:**
```
Maisha_backend/
├── tests/               (organized test files)
├── scripts/             (utility scripts)
├── docs/                (documentation)
│   └── archive/         (historical docs)
├── CLEANUP_ANALYSIS.md  (detailed analysis)
└── CLEANUP_SUMMARY.md   (this file)
```

