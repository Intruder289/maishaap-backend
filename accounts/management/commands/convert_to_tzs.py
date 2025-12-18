from django.core.management.base import BaseCommand
from decimal import Decimal


class Command(BaseCommand):
    help = 'Convert USD amounts to Tanzania Shillings (TZS) across the system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--exchange-rate',
            type=float,
            default=2600.0,
            help='USD to TZS exchange rate (default: 2600)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be converted without making changes'
        )

    def handle(self, *args, **options):
        exchange_rate = Decimal(str(options['exchange_rate']))
        dry_run = options['dry_run']
        
        self.stdout.write(f"Using exchange rate: 1 USD = {exchange_rate} TZS")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - No changes will be made"))
        
        converted_count = 0
        
        # Convert payments
        try:
            from payments.models import Payment, Invoice
            
            # Convert Payment amounts
            payments = Payment.objects.all()
            for payment in payments:
                if payment.amount and payment.amount < 10000:  # Likely USD if less than 10k
                    old_amount = payment.amount
                    new_amount = payment.amount * exchange_rate
                    
                    if not dry_run:
                        payment.amount = new_amount
                        payment.save()
                    
                    self.stdout.write(f"Payment {payment.id}: ${old_amount} → TZS {new_amount}")
                    converted_count += 1
            
            # Convert Invoice amounts
            invoices = Invoice.objects.all()
            for invoice in invoices:
                if invoice.amount and invoice.amount < 10000:  # Likely USD if less than 10k
                    old_amount = invoice.amount
                    new_amount = invoice.amount * exchange_rate
                    
                    if not dry_run:
                        invoice.amount = new_amount
                        invoice.save()
                    
                    self.stdout.write(f"Invoice {invoice.id}: ${old_amount} → TZS {new_amount}")
                    converted_count += 1
                    
        except ImportError:
            self.stdout.write("Payments app not found, skipping...")
        
        # Convert property prices
        try:
            from properties.models import Property
            
            properties = Property.objects.all()
            for prop in properties:
                # Properties use rent_amount field, not price
                if prop.rent_amount and prop.rent_amount < 10000:  # Likely USD
                    old_rent = prop.rent_amount
                    new_rent = prop.rent_amount * exchange_rate
                    
                    if not dry_run:
                        prop.rent_amount = new_rent
                        prop.save()
                    
                    self.stdout.write(f"Property {prop.id} rent: ${old_rent} → TZS {new_rent}")
                    converted_count += 1
                
                # Also convert deposit amounts if they exist
                if prop.deposit_amount and prop.deposit_amount < 10000:  # Likely USD
                    old_deposit = prop.deposit_amount
                    new_deposit = prop.deposit_amount * exchange_rate
                    
                    if not dry_run:
                        prop.deposit_amount = new_deposit
                        prop.save()
                    
                    self.stdout.write(f"Property {prop.id} deposit: ${old_deposit} → TZS {new_deposit}")
                    converted_count += 1
                    
        except ImportError:
            self.stdout.write("Properties app not found, skipping...")
        
        # Convert maintenance request costs
        try:
            from maintenance.models import MaintenanceRequest
            
            requests = MaintenanceRequest.objects.all()
            for request in requests:
                if hasattr(request, 'estimated_cost') and request.estimated_cost and request.estimated_cost < 10000:
                    old_cost = request.estimated_cost
                    new_cost = request.estimated_cost * exchange_rate
                    
                    if not dry_run:
                        request.estimated_cost = new_cost
                        request.save()
                    
                    self.stdout.write(f"Maintenance {request.id}: ${old_cost} → TZS {new_cost}")
                    converted_count += 1
                    
        except ImportError:
            self.stdout.write("Maintenance app not found, skipping...")
        
        # Update activity logs with amounts
        try:
            from accounts.models import ActivityLog
            
            activities = ActivityLog.objects.filter(amount__isnull=False)
            for activity in activities:
                if activity.amount < 10000:  # Likely USD
                    old_amount = activity.amount
                    new_amount = activity.amount * exchange_rate
                    
                    if not dry_run:
                        activity.amount = new_amount
                        activity.save()
                    
                    self.stdout.write(f"Activity {activity.id}: ${old_amount} → TZS {new_amount}")
                    converted_count += 1
                    
        except Exception as e:
            self.stdout.write(f"Error converting activities: {e}")
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'DRY RUN: Would convert {converted_count} amounts from USD to TZS')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully converted {converted_count} amounts from USD to TZS!')
            )
            
        self.stdout.write("\nCurrency conversion complete. All amounts are now in Tanzania Shillings (TZS).")
        self.stdout.write("Exchange rate used: 1 USD = {} TZS".format(exchange_rate))