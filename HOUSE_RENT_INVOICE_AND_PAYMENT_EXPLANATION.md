# House Rent - Invoice and Payment System Explained

## Overview

House rent works differently from hotel/lodge bookings. Instead of one-time payments, it uses a **lease-based system** with **monthly invoices** and **recurring payments**.

---

## Key Concepts

### 1. **Lease** (Rental Agreement)
A **Lease** is a long-term rental contract between a property owner and a tenant.

**Example:**
- Property: "3 Bedroom House in Dar es Salaam"
- Tenant: John Doe
- Lease Period: January 1, 2026 to December 31, 2026 (12 months)
- Monthly Rent: TZS 500,000
- Status: `active`

**What it contains:**
- Property reference
- Tenant (user)
- Start date and end date
- Monthly rent amount
- Status (pending, active, terminated, expired)

---

### 2. **RentInvoice** (Monthly Bill)
A **RentInvoice** is a monthly bill generated for each active lease.

**How it works:**
- **One invoice per month** for each active lease
- Generated automatically (or manually by admin)
- Each invoice covers a specific period (e.g., January 1-31)
- Contains the amount due for that month

**Example Invoice:**
```json
{
  "id": 45,
  "invoice_number": "INV-202601-ABC123",
  "lease": 10,                    // ← Links to Lease ID
  "tenant": 5,                    // ← Tenant user ID
  "invoice_date": "2026-01-01",
  "due_date": "2026-01-05",       // ← Payment due date (5 days after invoice date)
  "period_start": "2026-01-01",   // ← Month this invoice covers
  "period_end": "2026-01-31",
  "base_rent": "500000.00",       // ← Monthly rent amount
  "late_fee": "0.00",             // ← Added if payment is late
  "other_charges": "0.00",         // ← Additional charges (utilities, etc.)
  "discount": "0.00",             // ← Discounts applied
  "total_amount": "500000.00",    // ← Total to pay
  "amount_paid": "0.00",          // ← How much has been paid
  "status": "pending"             // ← pending, paid, overdue, cancelled
}
```

**Invoice Statuses:**
- `draft` - Invoice created but not sent
- `sent` - Invoice sent to tenant
- `paid` - Fully paid (`amount_paid >= total_amount`)
- `overdue` - Past due date and not fully paid
- `cancelled` - Invoice cancelled

**Invoice Calculation:**
```
total_amount = base_rent + late_fee + other_charges - discount
balance_due = total_amount - amount_paid
```

---

### 3. **Payment** (Payment Record)
A **Payment** is a payment made against a rent invoice.

**Key Points:**
- Payments are linked to a specific `rent_invoice`
- Can be **partial** (paying part of invoice) or **full** (paying entire invoice)
- Multiple payments can be made for one invoice
- Invoice `amount_paid` is automatically updated when payments are completed

**Example Payment:**
```json
{
  "id": 80,
  "rent_invoice": 45,             // ← Links to RentInvoice ID
  "lease": 10,                    // ← Links to Lease ID
  "tenant": 5,                    // ← Tenant user ID
  "amount": "500000.00",          // ← Payment amount
  "payment_method": "mobile_money", // ← cash, mobile_money, online
  "mobile_money_provider": "AIRTEL", // ← Required for mobile_money
  "status": "pending",            // ← pending, completed, failed, cancelled
  "paid_date": "2026-01-25",
  "transaction_id": "TXN-123456"
}
```

**Payment Methods:**
- `cash` - Cash payment (recorded manually)
- `mobile_money` - Mobile money via AZAM Pay (requires `mobile_money_provider`)
- `online` - Online payment via AZAM Pay

---

## Complete Flow: From Lease to Payment

### Step 1: Create Lease (Admin/Property Owner)
A lease is created when a tenant signs a rental agreement.

**Example:**
```
Lease Created:
- Property: House ID 123
- Tenant: User ID 5 (John Doe)
- Start: 2026-01-01
- End: 2026-12-31
- Monthly Rent: TZS 500,000
- Status: active
```

---

### Step 2: Generate Monthly Invoice (Automatic or Manual)

**Option A: Automatic Generation (Admin)**
```http
POST /api/v1/rent/invoices/generate-monthly/
{
  "month": 1,
  "year": 2026
}
```

**Option B: Manual Creation (Admin)**
```http
POST /api/v1/rent/invoices/
{
  "lease": 10,
  "period_start": "2026-01-01",
  "period_end": "2026-01-31",
  "due_date": "2026-01-05",
  "base_rent": "500000.00"
}
```

**Result:** Invoice created with:
- `invoice_number`: "INV-202601-ABC123"
- `total_amount`: "500000.00"
- `status`: "draft" or "sent"

---

### Step 3: Tenant Views Invoice (Mobile App)

**Get All Invoices:**
```http
GET /api/v1/rent/invoices/
```

**Response:**
```json
{
  "count": 3,
  "results": [
    {
      "id": 45,
      "invoice_number": "INV-202601-ABC123",
      "due_date": "2026-01-05",
      "total_amount": "500000.00",
      "amount_paid": "0.00",
      "balance_due": "500000.00",
      "status": "pending",
      "period_start": "2026-01-01",
      "period_end": "2026-01-31"
    },
    {
      "id": 46,
      "invoice_number": "INV-202602-DEF456",
      "due_date": "2026-02-05",
      "total_amount": "500000.00",
      "amount_paid": "0.00",
      "status": "pending",
      "period_start": "2026-02-01",
      "period_end": "2026-02-28"
    }
  ]
}
```

**Get Specific Invoice:**
```http
GET /api/v1/rent/invoices/45/
```

---

### Step 4: Create Payment (Mobile App)

**Create Payment Record:**
```http
POST /api/v1/rent/payments/
{
  "rent_invoice": 45,              // ← Invoice ID from Step 3
  "amount": "500000.00",           // ← Amount to pay (can be partial)
  "payment_method": "mobile_money",
  "mobile_money_provider": "AIRTEL",
  "reference_number": "REF-12345"  // Optional
}
```

**Response:**
```json
{
  "id": 80,                        // ← Payment ID (save this!)
  "rent_invoice": 45,
  "amount": "500000.00",
  "payment_method": "mobile_money",
  "mobile_money_provider": "AIRTEL",
  "status": "pending",
  "created_at": "2026-01-25T10:30:00Z",
  "invoice": {                     // ← Updated invoice info (always shown!)
    "id": 45,
    "invoice_number": "INV-202601-ABC123",
    "total_amount": "500000.00",
    "amount_paid": "0.00",         // ← Current amount paid
    "balance_due": "500000.00",    // ← Remaining amount (always updated!)
    "status": "pending"
  }
}
```

**Note**: The response **always includes** the updated invoice information with `balance_due` so you know exactly how much remains to be paid.

**Important Notes:**
- Payment is created with `status: "pending"`
- Invoice `amount_paid` is **NOT updated yet** (only updated when payment is completed)
- You can make **partial payments** (e.g., pay 250,000 now, 250,000 later)
- **STRICT Overpayment Protection**: 
  - ✅ **NO OVERPAYMENT ALLOWED** - The system strictly prevents paying more than the invoice balance
  - ✅ If invoice is already fully paid, **no additional payments are allowed**
  - ✅ Payment amount **cannot exceed** `balance_due`
  - ✅ System uses database locking to prevent race conditions
  - ✅ If you try to overpay, you'll get a clear error with the exact `balance_due` amount

---

### Step 5: Initiate Gateway Payment (Mobile App)

**Initiate AZAM Pay Payment:**
```http
POST /api/v1/rent/payments/80/initiate-gateway/
```

**Response:**
```json
{
  "success": true,
  "payment_id": 80,
  "transaction_id": 20,
  "payment_link": "https://checkout.azampay.co.tz/...",
  "transaction_reference": "RENT-80-1769145132",
  "message": "Payment initiated successfully. Redirect user to payment_link."
}
```

**What Happens:**
- Payment prompt sent to **tenant's phone** (smart phone logic)
- Tenant receives AZAM Pay prompt
- Tenant approves/rejects payment on phone
- Payment status updates automatically via webhook

---

### Step 6: Verify Payment Status (Mobile App)

**Check Payment Status:**
```http
GET /api/v1/rent/payments/80/
```

**Response (Pending):**
```json
{
  "id": 80,
  "status": "pending",
  "amount": "500000.00",
  "rent_invoice": 45
}
```

**Response (Completed):**
```json
{
  "id": 80,
  "status": "completed",          // ← Payment successful! ✅
  "amount": "500000.00",
  "rent_invoice": 45,
  "paid_date": "2026-01-25",
  "transaction_id": "TXN-123456"
}
```

**When Payment Completes:**
- Payment `status` changes to `"completed"`
- Invoice `amount_paid` is automatically updated
- If `amount_paid >= total_amount`, invoice `status` changes to `"paid"`

---

## Partial Payments Example

A tenant can make **multiple payments** for one invoice. **Important**: The system prevents overpayment - you cannot pay more than the invoice balance due. Each payment is validated against the current balance before being accepted.

### Example: Paying Invoice in Two Parts

**Invoice:**
- `total_amount`: "500000.00"
- `amount_paid`: "0.00"
- `balance_due`: "500000.00"

**Payment 1 (Partial):**
```json
POST /api/v1/rent/payments/
{
  "rent_invoice": 45,
  "amount": "250000.00",           // ← Paying half
  "payment_method": "mobile_money",
  "mobile_money_provider": "AIRTEL"
}
```

**Note**: If you try to pay more than the balance (e.g., 600,000 when balance is 500,000), the API will return an error:
```json
{
  "amount": ["Payment amount (600000.00) cannot exceed invoice balance due (500000.00). Maximum payment allowed: 500000.00"]
}
```

**After Payment 1 Completes:**
- Invoice `amount_paid`: "250000.00"
- Invoice `balance_due`: "250000.00"
- Invoice `status`: "pending" (not fully paid yet)

**Payment 2 (Remaining):**
```json
POST /api/v1/rent/payments/
{
  "rent_invoice": 45,
  "amount": "250000.00",           // ← Paying remaining balance
  "payment_method": "mobile_money",
  "mobile_money_provider": "TIGO"
}
```

**Note**: After Payment 1 completes, the balance becomes 250,000. If you try to pay more than 250,000, the system will reject it.

**After Payment 2 Completes:**
- Invoice `amount_paid`: "500000.00"
- Invoice `balance_due`: "0.00"
- Invoice `status`: "paid" ✅

---

## Invoice Status Updates

### Automatic Status Updates

**When Invoice Becomes Overdue:**
- If `due_date` has passed AND `amount_paid < total_amount`
- Invoice `status` automatically changes to `"overdue"`

**When Invoice Becomes Paid:**
- If `amount_paid >= total_amount`
- Invoice `status` automatically changes to `"paid"`

**Late Fees:**
- Late fees can be added to invoices that are overdue
- `late_fee` is added to `total_amount`
- Invoice must be recalculated

---

## Mobile App Flow Summary

### For Tenant (Mobile App):

```
1. GET /api/v1/rent/invoices/          → View all invoices
2. GET /api/v1/rent/invoices/45/       → View invoice details
3. POST /api/v1/rent/payments/         → Create payment
   {
     "rent_invoice": 45,
     "amount": "500000.00",
     "payment_method": "mobile_money",
     "mobile_money_provider": "AIRTEL"
   }
4. POST /api/v1/rent/payments/80/initiate-gateway/  → Initiate payment
5. GET /api/v1/rent/payments/80/       → Poll until status = "completed"
```

### For Admin/Property Owner:

```
1. Create Lease (when tenant signs agreement)
2. Generate Monthly Invoices (automatic or manual)
3. View All Invoices (for all tenants)
4. View Payment History
5. Add Late Fees (if needed)
```

---

## Key Differences: House Rent vs Hotel/Lodge Bookings

| Aspect | House Rent | Hotel/Lodge Booking |
|--------|-----------|---------------------|
| **Duration** | Long-term (months/years) | Short-term (days) |
| **Payment Type** | Recurring monthly | One-time |
| **Invoice** | Monthly invoices | No invoice (direct payment) |
| **Lease** | Required (rental agreement) | Not required |
| **Payment Link** | Links to `rent_invoice` | Links to `booking` |
| **Partial Payments** | Supported | Usually full payment |

---

## Important Fields Explained

### RentInvoice Fields:
- `lease` - The rental agreement this invoice belongs to
- `period_start` / `period_end` - The month/period this invoice covers
- `base_rent` - Monthly rent amount from lease
- `total_amount` - Total to pay (base_rent + late_fee + other_charges - discount)
- `amount_paid` - Sum of all completed payments for this invoice
- `balance_due` - Remaining amount (`total_amount - amount_paid`)

### Payment Fields:
- `rent_invoice` - The invoice this payment is for
- `lease` - The lease (same as invoice's lease)
- `tenant` - The tenant making the payment
- `amount` - Payment amount (can be partial)
- `status` - Payment status (pending → completed)

---

## Summary

**House Rent System:**
1. **Lease** = Long-term rental agreement
2. **RentInvoice** = Monthly bill (one per month per lease)
3. **Payment** = Payment made against invoice (can be multiple payments per invoice)

**Flow:**
- Lease created → Monthly invoices generated → Tenant pays invoices → Invoice status updates

**Mobile App:**
- View invoices → Create payment → Initiate gateway → Verify status → Done!

**STRICT Overpayment Protection:**
- ✅ **NO OVERPAYMENT ALLOWED** - System strictly enforces exact payment amounts
- ✅ **Invoice must not be fully paid** - If `balance_due <= 0`, no additional payments allowed
- ✅ **Payment amount cannot exceed balance** - Maximum payment = `balance_due` (exact remaining amount)
- ✅ **Database-level locking** - Prevents race conditions when multiple payments are created simultaneously
- ✅ **Pending payments considered** - System accounts for pending payments when calculating balance
- ✅ **Always shows remaining amount** - Every payment response includes updated `balance_due`
- ✅ **Clear error messages** - If overpayment attempted, error shows exact `balance_due` and maximum allowed amount
- ✅ **Automatic balance updates** - `balance_due` is automatically recalculated after each payment

All APIs are documented in Swagger and ready for mobile app integration! 🎉
