# Mobile Money Provider Field - Explanation for Mobile App

## What is `mobile_money_provider`?

The `mobile_money_provider` field is a **string field** (NOT an ID) that identifies which mobile money service the customer will use to make the payment.

## Valid Values

You must pass one of these **exact string values** (case-sensitive, uppercase):

1. **`"AIRTEL"`** - For Airtel Money
2. **`"TIGO"`** - For Tigo Pesa
3. **`"MPESA"`** - For M-Pesa (Vodacom)
4. **`"HALOPESA"`** - For Halopesa

## When to Use This Field

- **Required**: When `payment_method` is `"mobile_money"`
- **Not Required**: When `payment_method` is `"cash"` or `"online"`
- **Optional**: Can be `null` or omitted for non-mobile-money payments

## Example API Request

### Creating a Payment with Mobile Money

```json
POST /api/v1/payments/payments/
{
  "booking": 123,
  "tenant": 5,
  "amount": "200000.00",
  "payment_method": "mobile_money",
  "mobile_money_provider": "AIRTEL",  // ← Pass one of: AIRTEL, TIGO, MPESA, HALOPESA
  "status": "pending"
}
```

### Initiating Gateway Payment (Booking Payment)

```json
POST /api/v1/payments/payments/{payment_id}/initiate-gateway/
{
  "mobile_money_provider": "TIGO"  // ← Required if payment_method is "mobile_money"
}
```

## Mobile App Implementation Guide

### Step 1: Show Provider Selection UI

In your mobile app, when the user selects `payment_method: "mobile_money"`, show them a dropdown or selection list with these options:

```javascript
// Example: React Native / JavaScript
const mobileMoneyProviders = [
  { value: 'AIRTEL', label: 'AIRTEL' },
  { value: 'TIGO', label: 'TIGO' },
  { value: 'MPESA', label: 'MPESA (Vodacom)' },
  { value: 'HALOPESA', label: 'HALOPESA' }
];

// Show in UI
<Picker
  selectedValue={selectedProvider}
  onValueChange={(value) => setSelectedProvider(value)}
>
  {mobileMoneyProviders.map(provider => (
    <Picker.Item 
      key={provider.value} 
      label={provider.label} 
      value={provider.value} 
    />
  ))}
</Picker>
```

### Step 2: Send Provider Value in API Request

When creating the payment or initiating gateway payment, include the selected provider:

```javascript
// Example API call
const createPayment = async (bookingId, amount, provider) => {
  const response = await fetch('/api/v1/payments/payments/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      booking: bookingId,
      tenant: userId,
      amount: amount.toString(),
      payment_method: 'mobile_money',
      mobile_money_provider: provider,  // ← Use selected provider value
      status: 'pending'
    })
  });
  return response.json();
};

// Usage
await createPayment(123, 200000, 'AIRTEL');  // ← Pass string value
```

### Step 3: Validation

The backend will validate that:
- If `payment_method` is `"mobile_money"`, then `mobile_money_provider` must be provided
- The value must be one of: `"AIRTEL"`, `"TIGO"`, `"MPESA"`, or `"HALOPESA"`
- The value is case-insensitive (backend converts to uppercase automatically)

## Important Notes

1. **NOT an ID**: This is a **string value**, not a database ID. You pass the provider name directly.

2. **Case Handling**: The backend automatically converts the value to uppercase, but it's best practice to send uppercase values:
   - ✅ `"AIRTEL"` (correct)
   - ✅ `"airtel"` (will work, converted to uppercase)
   - ❌ `"Airtel"` (will work, but inconsistent)

3. **User Selection**: The mobile app should let the user **select their provider** based on which SIM card/service they use. This must match their actual mobile money account.

4. **Payment Flow**: 
   - User selects payment method: `"mobile_money"`
   - User selects provider: `"AIRTEL"` (or TIGO, MPESA, HALOPESA)
   - App sends both fields to API
   - Backend uses provider to route payment through correct gateway

## Complete Payment Flow Example

### 1. Create Booking Payment

```json
POST /api/v1/payments/payments/
{
  "booking": 123,
  "tenant": 5,
  "amount": "200000.00",
  "payment_method": "mobile_money",
  "mobile_money_provider": "AIRTEL",
  "status": "pending"
}
```

**Response:**
```json
{
  "id": 456,
  "booking": 123,
  "amount": "200000.00",
  "payment_method": "mobile_money",
  "mobile_money_provider": "AIRTEL",
  "status": "pending"
}
```

### 2. Initiate Gateway Payment

```json
POST /api/v1/payments/payments/456/initiate-gateway/
{
  "mobile_money_provider": "AIRTEL"
}
```

**Response:**
```json
{
  "success": true,
  "payment_id": 456,
  "transaction_reference": "TXN-123456",
  "gateway_transaction_id": "AZAM-789012",
  "phone_number_used": "+255700000000",
  "message": "Payment initiated. Check your phone for payment prompt."
}
```

## Error Handling

If you send an invalid provider value, you'll get:

```json
{
  "error": "Mobile Money Provider is required for mobile money payments. Please provide: AIRTEL, TIGO, MPESA, or HALOPESA"
}
```

Or if the value is not in the choices:

```json
{
  "mobile_money_provider": ["Invalid choice. Must be one of: AIRTEL, TIGO, MPESA, HALOPESA"]
}
```

## Summary

- **Field Type**: String (not ID)
- **Valid Values**: `"AIRTEL"`, `"TIGO"`, `"MPESA"`, `"HALOPESA"`
- **Required**: Only when `payment_method` is `"mobile_money"`
- **Usage**: Let user select their provider, then pass the selected value to the API
- **Case**: Uppercase recommended (backend converts automatically)

**Just pass the provider name as a string - no ID lookup needed!**
