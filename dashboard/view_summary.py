# ui/dashboard/view_summary.py
from dataclasses import dataclass
from datetime import date, timedelta
from expense_tracking.expense_tracker import ExpenseTracker
from dashboard.compare_periods import get_week_range


@dataclass
class ViewSummary:
    tracker: ExpenseTracker

    def day_summary(self, day: str):
        totals, total = self.tracker.get_category_totals(day, day)
        return {
            "date": day,
            "totals": totals,
            "total": total,
            "remaining": self.tracker.user.allowance,
        }

    def week_breakdown(self, any_day: str):
        monday, _ = get_week_range(any_day)
        start = date.fromisoformat(monday)
        days = []
        for i in range(7):
            current = start + timedelta(days=i)
            days.append({
                "day_name": current.strftime("%A"),
                "date": str(current),
                "expenses": self.tracker.get_expense_summary(str(current)),
            })
        return days