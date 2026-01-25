# Phone Number Sources Explained - Smart Phone Logic

**Understanding Which Phone Number is Used for Payment**

---

## 📱 Two Types of Phone Numbers in the System

### 1. **Customer Phone** (`Customer.phone`)
- **Stored in:** `Customer` model (separate from User account)
- **When it's set:** When creating a booking (provided in booking request)
- **Purpose:** Contact information for the person making the booking
- **Example:** John Doe books a hotel room and provides his phone `+255700000000`

### 2. **User Profile Phone** (`Profile.phone`)
- **Stored in:** `Profile` model (linked to User account)
- **When it's set:** During user registration or profile update
- **Purpose:** The logged-in user's phone number
- **Example:** User registers with phone `+255711111111` (stored in their profile)

---

## 🎯 Which Phone Number is Used for Payment?

### Scenario 1: **Booking Payment - Admin/Staff Creates Payment**

**Phone Used:** `booking.customer.phone` (Customer's phone from booking)

**Why?** When admin creates a payment for a booking, the **customer** should receive the payment prompt, not the admin.

**Source:** Phone number provided when creating the booking:
```javascript
POST /api/v1/properties/bookings/create/
{
  "customer_name": "John Doe",
  "phone": "+255700000000",  // ← This phone is stored in Customer.phone
  "email": "john@example.com",
  ...
}
```

**Flow:**
1. Admin creates booking with customer phone `+255700000000`
2. Phone stored in `Customer` model: `booking.customer.phone = "+255700000000"`
3. Admin creates payment for this booking
4. Smart logic: Uses `booking.customer.phone` → `+255700000000`
5. Payment prompt sent to customer's phone (`+255700000000`)

**NOT the admin's registration phone!** ✅

---

### Scenario 2: **Booking Payment - Customer Creates Payment**

**Phone Used:** `user.profile.phone` (Customer's own profile phone)

**Why?** When a customer creates their own payment, they should receive the payment prompt on their own phone.

**Source:** Phone number from user's profile (set during registration/profile update)

**Flow:**
1. Customer registers with phone `+255711111111` (stored in `Profile.phone`)
2. Customer creates booking
3. Customer creates payment for their booking
4. Smart logic: Uses `user.profile.phone` → `+255711111111`
5. Payment prompt sent to customer's own phone (`+255711111111`)

**This IS the registration/profile phone!** ✅

---

### Scenario 3: **Rent Payment - Admin/Staff Creates Payment**

**Phone Used:** `rent_invoice.tenant.profile.phone` (Tenant's profile phone)

**Why?** When admin creates a rent payment, the **tenant** should receive the payment prompt.

**Source:** Phone number from tenant's profile (set during registration/profile update)

**Flow:**
1. Tenant registers with phone `+255722222222` (stored in `Profile.phone`)
2. Admin creates rent invoice for tenant
3. Admin creates payment for rent invoice
4. Smart logic: Uses `rent_invoice.tenant.profile.phone` → `+255722222222`
5. Payment prompt sent to tenant's phone (`+255722222222`)

**This IS the tenant's registration/profile phone!** ✅

---

### Scenario 4: **Rent Payment - Tenant Creates Payment**

**Phone Used:** `user.profile.phone` (Tenant's own profile phone)

**Why?** When tenant creates their own payment, they should receive the payment prompt on their own phone.

**Source:** Phone number from tenant's profile (set during registration/profile update)

**Flow:**
1. Tenant registers with phone `+255722222222` (stored in `Profile.phone`)
2. Tenant creates payment for their rent invoice
3. Smart logic: Uses `user.profile.phone` → `+255722222222`
4. Payment prompt sent to tenant's own phone (`+255722222222`)

**This IS the registration/profile phone!** ✅

---

### Scenario 5: **Visit Payment - Anyone Creates Payment**

**Phone Used:** `user.profile.phone` (Their own profile phone)

**Why?** Visit payments are always for the person making the payment.

**Source:** Phone number from user's profile (set during registration/profile update)

**Flow:**
1. User registers with phone `+255733333333` (stored in `Profile.phone`)
2. User creates visit payment
3. Smart logic: Uses `user.profile.phone` → `+255733333333`
4. Payment prompt sent to user's own phone (`+255733333333`)

**This IS the registration/profile phone!** ✅

---

## 📊 Summary Table

| Payment Type | User Type | Phone Number Used | Source | Is Registration Phone? |
|-------------|-----------|------------------|--------|----------------------|
| **Booking Payment** | Admin/Staff | `booking.customer.phone` | From booking request | ❌ **NO** - Booking phone |
| **Booking Payment** | Customer | `user.profile.phone` | From user profile | ✅ **YES** - Registration phone |
| **Rent Payment** | Admin/Staff | `rent_invoice.tenant.profile.phone` | From tenant profile | ✅ **YES** - Tenant's registration phone |
| **Rent Payment** | Tenant | `user.profile.phone` | From user profile | ✅ **YES** - Registration phone |
| **Visit Payment** | Anyone | `user.profile.phone` | From user profile | ✅ **YES** - Registration phone |

---

## 🔍 Key Points

### 1. **Booking Payments (Admin/Staff)**
- **Uses:** Phone provided when creating the booking (`Customer.phone`)
- **NOT:** Admin's registration phone
- **Reason:** Customer should receive payment prompt, not admin

### 2. **All Other Payments**
- **Uses:** Phone from user profile (`Profile.phone`)
- **Source:** Registration or profile update
- **Reason:** Person making payment should receive prompt

### 3. **Two Separate Phone Numbers**
- **Customer Phone:** For booking contact (can be different from user's phone)
- **Profile Phone:** User's account phone (from registration)

### 4. **Example Scenario**
```
Admin (phone: +255788888888) creates booking for:
- Customer: John Doe
- Customer phone: +255700000000 (provided in booking)

When admin creates payment:
→ Payment prompt goes to: +255700000000 (customer's phone)
→ NOT to: +255788888888 (admin's phone)

When customer creates payment:
→ Payment prompt goes to: +255711111111 (customer's profile phone)
→ NOT to: +255700000000 (booking phone, if different)
```

---

## ✅ Response Field: `phone_number_used`

After initiating payment, the response includes which phone was used:

```json
{
  "success": true,
  "payment_id": 80,
  "phone_number_used": "+255700000000",  // ← Shows which phone was used
  "message": "Payment initiated successfully..."
}
```

This confirms:
- **For booking payments (admin):** Shows customer's booking phone
- **For other payments:** Shows user's profile phone

---

## 🎯 Conclusion

**The phone number used depends on:**
1. **Who is making the payment** (admin/staff vs customer/tenant)
2. **What type of payment** (booking vs rent vs visit)

**For booking payments created by admin/staff:**
- Uses **customer's phone from booking** (provided when creating booking)
- **NOT** the admin's registration phone

**For all other payments:**
- Uses **user's profile phone** (from registration/profile update)
- **YES**, this is the registration phone

---

**Ready for Mobile App Integration!** ✅
