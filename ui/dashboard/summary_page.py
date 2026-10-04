from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QDateEdit, QTextEdit, QLabel,
)
from PyQt6.QtCore import QDate
from dashboard.view_summary import ViewSummary
from ui.dashboard.styled_text import StyledText, PINK, MUTED


class SummaryPage(QWidget):
    def __init__(self, tracker):
        super().__init__()
        self.summary = ViewSummary(tracker)

        layout = QVBoxLayout(self)

        title = QLabel("Summary")
        title.setObjectName("title")
        layout.addWidget(title)

        controls = QHBoxLayout()
        self.period_input = QComboBox()
        self.period_input.addItems(["Day", "Week"])
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        controls.addWidget(self.period_input)
        controls.addWidget(self.date_input)
        controls.addStretch()
        layout.addLayout(controls)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)
        self.text = StyledText(self.output)

        self.period_input.currentIndexChanged.connect(self.refresh)
        self.date_input.dateChanged.connect(self.refresh)

    def showEvent(self, event):
        self.refresh()
        super().showEvent(event)

    def refresh(self, *args):
        day = self.date_input.date().toString("yyyy-MM-dd")
        self.text.clear()
        if self.period_input.currentText() == "Day":
            self.show_day(day)
        else:
            self.show_week(day)

    def show_day(self, day):
        t = self.text
        data = self.summary.day_summary(day)
        t.add(f"Spending on {data['date']}", bold=True, color=PINK, size=16)
        t.add("")
        if not data["totals"]:
            t.add("No expenses", color=MUTED)
        for category, amount in data["totals"].items():
            t.add(f"{category}: ", newline=False)
            t.add(f"₱{amount:,.2f}", bold=True)
        t.add("")
        t.add(f"Total: ₱{data['total']:,.2f}", bold=True)
        t.add("Remaining allowance: ", newline=False)
        t.add(f"₱{data['remaining']:,.2f}", bold=True)

    def show_week(self, day):
        t = self.text
        for d in self.summary.week_breakdown(day):
            t.add(f"{d['day_name']} ", bold=True, color=PINK, size=15, newline=False)
            t.add(f"({d['date']})", color=MUTED)
            if not d["expenses"]:
                t.add("  No expenses", color=MUTED)
            for e in d["expenses"]:
                t.add(f"  {e.category}: ", newline=False)
                t.add(f"₱{e.amount:,.2f}", bold=True, newline=False)
                if e.note:
                    t.add(f"  ({e.note})", color=MUTED)
                else:
                    t.add("")
            t.add("")