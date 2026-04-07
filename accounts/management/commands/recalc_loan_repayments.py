from decimal import Decimal
from django.core.management.base import BaseCommand
from accounts.models import LoanApplication

RATE = Decimal("0.003")  # 0.3% monthly


def calc_emi(amount: Decimal, rate: Decimal, term_months: int) -> Decimal:
    """EMI Reducing Balance: P * r * (1+r)^n / ((1+r)^n - 1)"""
    r = rate
    n = term_months
    factor = (1 + r) ** n
    emi = amount * r * factor / (factor - 1)
    return emi.quantize(Decimal("0.01"))


class Command(BaseCommand):
    help = "Recalculate all loan monthly_repayment using EMI Reducing Balance at 0.3%"

    def handle(self, *args, **options):
        loans = LoanApplication.objects.filter(
            amount__isnull=False,
            term_months__isnull=False,
        ).exclude(amount=0)

        total = loans.count()
        updated = 0

        self.stdout.write(f"Found {total} loan records to update...")

        for loan in loans:
            try:
                amount = Decimal(str(loan.amount))
                term = int(loan.term_months)
                monthly = calc_emi(amount, RATE, term)

                loan.interest_rate_monthly = RATE
                loan.monthly_repayment = monthly
                loan.save(update_fields=["interest_rate_monthly", "monthly_repayment"])
                updated += 1
                self.stdout.write(
                    f"  [OK] Loan #{loan.id} | {loan.user} | "
                    f"Amount={amount:,.0f} | Term={term}m | "
                    f"EMI={monthly:,.2f}"
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  [ERROR] Loan #{loan.id}: {e}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone! Updated {updated}/{total} loan records to EMI 0.3%."
            )
        )
