from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Sum, F
from rent.models import RentInvoice, LateFee
from datetime import timedelta


class Command(BaseCommand):
    help = 'Calculate and apply late fees to overdue invoices'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what late fees would be applied without actually applying them.'
        )
        parser.add_argument(
            '--max-late-fee',
            type=float,
            help='Maximum late fee to apply per invoice (overrides lease settings)'
        )
        parser.add_argument(
            '--grace-period',
            type=int,
            help='Grace period in days before applying late fees (overrides lease settings)'
        )
    
    def handle(self, *args, **options):
        today = timezone.now().date()
        
        self.stdout.write(f"Processing late fees for {today}")
        self.stdout.write("-" * 50)
        
        # Find overdue invoices
        overdue_invoices = RentInvoice.objects.filter(
            due_date__lt=today,
            status__in=['sent', 'overdue'],
            balance_due__gt=0
        ).select_related('lease', 'tenant')
        
        self.stdout.write(f"Found {overdue_invoices.count()} overdue invoices")
        
        applied_count = 0
        skipped_count = 0
        error_count = 0
        total_fees_applied = 0
        
        for invoice in overdue_invoices:
            try:
                days_overdue = (today - invoice.due_date).days
                
                # Get late fee configuration for this lease
                late_fee_config = LateFee.objects.filter(
                    lease=invoice.lease,
                    is_active=True
                ).first()
                
                if not late_fee_config:
                    self.stdout.write(f"  SKIP: No late fee configuration for {invoice.invoice_number}")
                    skipped_count += 1
                    continue
                
                # Use command line overrides if provided
                grace_period = options.get('grace_period', late_fee_config.grace_period_days)
                max_late_fee = options.get('max_late_fee')
                if max_late_fee:
                    max_late_fee = float(max_late_fee)
                else:
                    max_late_fee = late_fee_config.max_late_fee
                
                # Check if still in grace period
                if days_overdue <= grace_period:
                    self.stdout.write(
                        f"  SKIP: {invoice.invoice_number} still in grace period "
                        f"({days_overdue}/{grace_period} days)"
                    )
                    skipped_count += 1
                    continue
                
                # Calculate late fee
                calculated_fee = late_fee_config.calculate_late_fee(invoice, days_overdue)
                
                # Apply maximum limit if set
                if max_late_fee and calculated_fee > max_late_fee:
                    calculated_fee = max_late_fee
                
                # Check if late fee already applied
                current_late_fee = invoice.late_fee
                if current_late_fee >= calculated_fee:
                    self.stdout.write(
                        f"  SKIP: {invoice.invoice_number} already has adequate late fee "
                        f"(${current_late_fee} >= ${calculated_fee})"
                    )
                    skipped_count += 1
                    continue
                
                # Calculate additional late fee to apply
                additional_fee = calculated_fee - current_late_fee
                
                if options['dry_run']:
                    self.stdout.write(
                        f"  WOULD APPLY: ${additional_fee:.2f} late fee to {invoice.invoice_number} "
                        f"({days_overdue} days overdue, total late fee would be ${calculated_fee:.2f})"
                    )
                    applied_count += 1
                    total_fees_applied += additional_fee
                    continue
                
                # Apply the late fee
                invoice.late_fee = calculated_fee
                invoice.status = 'overdue'
                invoice.save()  # This will recalculate total_amount
                
                self.stdout.write(
                    self.style.WARNING(
                        f"  APPLIED: ${additional_fee:.2f} late fee to {invoice.invoice_number} "
                        f"({days_overdue} days overdue, total late fee now ${calculated_fee:.2f})"
                    )
                )
                
                applied_count += 1
                total_fees_applied += additional_fee
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  ERROR: Failed to process {invoice.invoice_number}: {str(e)}")
                )
                error_count += 1
        
        # Summary
        self.stdout.write("-" * 50)
        if options['dry_run']:
            self.stdout.write(
                self.style.SUCCESS(
                    f"DRY RUN COMPLETE: Would apply ${total_fees_applied:.2f} in late fees to {applied_count} invoices, "
                    f"{skipped_count} skipped"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"COMPLETE: Applied ${total_fees_applied:.2f} in late fees to {applied_count} invoices, "
                    f"{skipped_count} skipped, {error_count} errors"
                )
            )
        
        if applied_count > 0 and not options['dry_run']:
            self.stdout.write("\nNext steps:")
            self.stdout.write("1. Review updated invoices in the admin or rent dashboard")
            self.stdout.write("2. Send late fee notifications to affected tenants")
            self.stdout.write("3. Consider sending additional payment reminders")