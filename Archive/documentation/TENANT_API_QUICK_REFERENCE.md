# Tenant API Quick Reference Card

## 🚀 Base URL
```
http://127.0.0.1:8001/api/v1
```

---

## 📋 All Tenant APIs (40 Total)

### 🔓 PUBLIC APIs (9 endpoints - No Auth Required)

#### Authentication
1. `POST /auth/signup/` - User registration
2. `POST /auth/login/` - User login

#### Properties
3. `GET /properties/` - List all properties
4. `GET /properties/{id}/` - Get property details
5. `GET /property-types/` - List property types
6. `GET /regions/` - List regions
7. `GET /amenities/` - List amenities
8. `GET /featured/` - Featured properties
9. `GET /recent/` - Recent properties

---

### 🔒 PROTECTED APIs (31 endpoints - Auth Required)

Add header to all requests:
```
Authorization: Bearer <access_token>
```

#### Authentication
10. `GET /auth/profile/` - Get profile
11. `PUT /auth/profile/update/` - Update profile
12. `POST /auth/change-password/` - Change password
13. `POST /auth/verify/` - Verify token
14. `POST /auth/refresh/` - Refresh token
15. `POST /auth/logout/` - Logout

#### Properties
16. `POST /search/` - Advanced search
17. `GET /my-properties/` - My properties
18. `POST /toggle-favorite/` - Toggle favorite
19. `GET /favorites/` - Get favorites
20. `POST /properties/{id}/view/` - Track view

#### Rent
21. `GET /rent/invoices/` - List invoices
22. `GET /rent/invoices/{id}/` - Invoice details
23. `GET /rent/payments/` - List payments
24. `GET /rent/late-fees/` - List late fees
25. `GET /rent/reminders/` - List reminders

#### Payments
26. `GET /payments/providers/` - Payment providers
27. `GET /payments/invoices/` - List invoices
28. `GET /payments/invoices/{id}/` - Invoice details
29. `GET /payments/payments/` - List payments
30. `GET /payments/payments/{id}/` - Payment details
31. `GET /payments/transactions/` - List transactions
32. `GET /payments/expenses/` - List expenses

#### Maintenance
33. `GET /maintenance/requests/` - List requests
34. `GET /maintenance/requests/{id}/` - Request details
35. `POST /maintenance/requests/` - Create request
36. `PUT /maintenance/requests/{id}/` - Update request

#### Documents
37. `GET /documents/` - List documents
38. `POST /documents/upload/` - Upload document

#### Reports
39. `GET /reports/` - List reports

#### Complaints
40. `GET /complaints/` - List complaints
41. `POST /complaints/` - Create complaint

---

## 🔑 How to Use

### 1. Get Access Token
```bash
POST /auth/login/
{
  "email": "your@email.com",
  "password": "yourpassword"
}

# Response includes:
{
  "tokens": {
    "access": "Bearer token here",
    "refresh": "Refresh token here"
  }
}
```

### 2. Use Token in Requests
```bash
curl -X GET http://127.0.0.1:8001/api/v1/auth/profile/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📊 Quick Stats

- **Total**: 40 endpoints
- **Public**: 9 (no authentication)
- **Protected**: 31 (JWT required)
- **Methods**: GET, POST, PUT, PATCH, DELETE
- **Format**: JSON

---

## 🧪 Test Credentials

```
Email: api_test@example.com
Password: test123
Status: ✅ Approved
Role: ✅ Tenant
```

---

## 🌐 Swagger UI

**Access**: http://127.0.0.1:8001/swagger/

Test all APIs interactively!

---

## 📚 Full Documentation

- Complete details: `TENANT_API_REFERENCE.md`
- API docs: `API_DOCUMENTATION.md`
- Test results: `COMPLETE_API_TEST_SUMMARY.md`


