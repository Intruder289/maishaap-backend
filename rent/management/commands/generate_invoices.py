from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from rent.models import RentInvoice
from documents.models import Lease


class Command(BaseCommand):
    help = 'Generate monthly rent invoices for all active leases'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--month',
            type=int,
            default=None,
            help='Month to generate invoices for (1-12). Defaults to next month.'
        )
        parser.add_argument(
            '--year',
            type=int,
            default=None,
            help='Year to generate invoices for. Defaults to current year or next year if next month is January.'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating invoices.'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Generate invoices even if they already exist for the period.'
        )
    
    def handle(self, *args, **options):
        # Determine the target month and year
        current_date = timezone.now().date()
        
        if options['month']:
            target_month = options['month']
        else:
            # Default to next month
            if current_date.month == 12:
                target_month = 1
            else:
                target_month = current_date.month + 1
        
        if options['year']:
            target_year = options['year']
        else:
            # Default to current year, or next year if targeting January from December
            if target_month == 1 and current_date.month == 12:
                target_year = current_date.year + 1
            else:
                target_year = current_date.year
        
        # Calculate period dates
        period_start = datetime(target_year, target_month, 1).date()
        
        if target_month == 12:
            period_end = datetime(target_year + 1, 1, 1).date() - timedelta(days=1)
        else:
            period_end = datetime(target_year, target_month + 1, 1).date() - timedelta(days=1)
        
        # Due date is typically 5 days into the month
        due_date = period_start + timedelta(days=4)  # 5th of the month
        
        self.stdout.write(f"Generating invoices for {period_start.strftime('%B %Y')}")
        self.stdout.write(f"Period: {period_start} to {period_end}")
        self.stdout.write(f"Due date: {due_date}")
        self.stdout.write("-" * 50)
        
        # Get active leases for the target period
        active_leases = Lease.objects.filter(
            status='active',
            start_date__lte=period_end,
            end_date__gte=period_start
        ).select_related('tenant', 'property_ref')
        
        self.stdout.write(f"Found {active_leases.count()} active leases")
        
        created_count = 0
        skipped_count = 0
        
        for lease in active_leases:
            # Check if invoice already exists for this period
            existing_invoice = RentInvoice.objects.filter(
                lease=lease,
                period_start=period_start,
                period_end=period_end
            ).first()
            
            if existing_invoice and not options['force']:
                self.stdout.write(
                    f"  SKIP: {lease.tenant.get_full_name() or lease.tenant.username} - "
                    f"{lease.property_ref.name} (Invoice {existing_invoice.invoice_number} exists)"
                )
                skipped_count += 1
                continue
            
            if options['dry_run']:
                self.stdout.write(
                    f"  WOULD CREATE: {lease.tenant.get_full_name() or lease.tenant.username} - "
                    f"{lease.property_ref.name} - TZS {lease.rent_amount:,.0f}"
                )
                created_count += 1
                continue
            
            # Create the invoice
            try:
                if existing_invoice and options['force']:
                    # Update existing invoice
                    existing_invoice.due_date = due_date
                    existing_invoice.base_rent = lease.rent_amount
                    existing_invoice.total_amount = lease.rent_amount
                    existing_invoice.status = 'draft'
                    existing_invoice.save()
                    
                    self.stdout.write(
                        self.style.WARNING(
                            f"  UPDATED: {lease.tenant.get_full_name() or lease.tenant.username} - "
                            f"{lease.property_ref.name} - TZS {lease.rent_amount:,.0f} (Invoice {existing_invoice.invoice_number})"
                        )
                    )
                else:
                    # Create new invoice
                    invoice = RentInvoice.objects.create(
                        lease=lease,
                        tenant=lease.tenant,
                        due_date=due_date,
                        period_start=period_start,
                        period_end=period_end,
                        base_rent=lease.rent_amount,
                        status='draft'
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  CREATED: {lease.tenant.get_full_name() or lease.tenant.username} - "
                            f"{lease.property_ref.name} - TZS {lease.rent_amount:,.0f} (Invoice {invoice.invoice_number})"
                        )
                    )
                
                created_count += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"  ERROR: Failed to create invoice for {lease.tenant.get_full_name() or lease.tenant.username} - "
                        f"{lease.property_ref.name}: {str(e)}"
                    )
                )
        
        # Summary
        self.stdout.write("-" * 50)
        if options['dry_run']:
            self.stdout.write(
                self.style.SUCCESS(
                    f"DRY RUN COMPLETE: Would create {created_count} invoices, "
                    f"{skipped_count} already exist"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"COMPLETE: Created/updated {created_count} invoices for {period_start.strftime('%B %Y')}, "
                    f"{skipped_count} skipped"
                )
            )
        
        if created_count > 0 and not options['dry_run']:
            self.stdout.write("\nNext steps:")
            self.stdout.write("1. Review generated invoices in the admin or rent dashboard")
            self.stdout.write("2. Update invoice status from 'draft' to 'sent' when ready")
            self.stdout.write("3. Send invoice notifications to tenants")
            self.stdout.write("4. Set up automated reminders for due dates")