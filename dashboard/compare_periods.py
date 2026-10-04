# ui/dashboard/compare_periods.py
from dataclasses import dataclass
from datetime import date, timedelta
from expense_tracking.expense_tracker import ExpenseTracker


def get_week_range(day: str):
    d = date.fromisoformat(day)
    monday = d - timedelta(days=d.weekday())
    sunday = monday + timedelta(days=6)
    return str(monday), str(sunday)


@dataclass
class ComparePeriods:
    tracker: ExpenseTracker

    def compare(self, start1: str, end1: str, start2: str, end2: str):
        totals1, total1 = self.tracker.get_category_totals(start1, end1)
        totals2, total2 = self.tracker.get_category_totals(start2, end2)
        return {
            "first": {"start": start1, "end": end1, "totals": totals1, "total": total1},
            "second": {"start": start2, "end": end2, "totals": totals2, "total": total2},
            "difference": total1 - total2,
        }

    def compare_days(self, day1: str, day2: str):
        return self.compare(day1, day1, day2, day2)

    def compare_weeks(self, day1: str, day2: str):
        start1, end1 = get_week_range(day1)
        start2, end2 = get_week_range(day2)
        return self.compare(start1, end1, start2, end2)