from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QDateEdit,
    QPushButton, QTextEdit, QLabel, QSplitter,
)
from PyQt6.QtCore import QDate
from dashboard.compare_periods import ComparePeriods
from ui.dashboard.chart_widgets import ChartWidget
from ui.dashboard.styled_text import StyledText, PINK, MUTED
from typing import override
import numpy as np


class ComparePage(QWidget):
    def __init__(self, tracker):
        super().__init__()
        self.compare = ComparePeriods(tracker)

        layout = QVBoxLayout(self)

        title = QLabel("Compare")
        title.setObjectName("title")
        layout.addWidget(title)

        hint = QLabel("For weeks, pick any date inside each week.")
        layout.addWidget(hint)

        controls = QHBoxLayout()
        self.mode_input = QComboBox()
        self.mode_input.addItems(["Weeks", "Days"])

        self.first_date = QDateEdit(QDate.currentDate())
        self.second_date = QDateEdit(QDate.currentDate().addDays(-7))
        for date_input in (self.first_date, self.second_date):
            date_input.setCalendarPopup(True)
            date_input.setDisplayFormat("yyyy-MM-dd")

        compare_button = QPushButton("Compare")
        compare_button.clicked.connect(self.run_compare)

        controls.addWidget(self.mode_input)
        controls.addWidget(self.first_date)
        controls.addWidget(QLabel("vs"))
        controls.addWidget(self.second_date)
        controls.addWidget(compare_button)
        controls.addStretch()
        layout.addLayout(controls)

        splitter = QSplitter()
        layout.addWidget(splitter)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.text = StyledText(self.output)

        self.chart = ChartWidget(figsize=(8, 5))
        splitter.addWidget(self.output)
        splitter.addWidget(self.chart)

    @override
    def showEvent(self, event):
        self.run_compare()
        super().showEvent(event)

    def run_compare(self):
        first = self.first_date.date().toString("yyyy-MM-dd")
        second = self.second_date.date().toString("yyyy-MM-dd")
        if self.mode_input.currentText() == "Weeks":
            result = self.compare.compare_weeks(first, second)
        else:
            result = self.compare.compare_days(first, second)
        self.text.clear()
        self.show_result(result)
        self.draw_chart(result)

    def show_period(self, label, period):
        t = self.text
        if period["start"] == period["end"]:
            dates = period["start"]
        else:
            dates = f"{period['start']} to {period['end']}"
        t.add(f"{label} ", bold=True, color=PINK, size=16, newline=False)
        t.add(f"({dates})", color=MUTED)
        if not period["totals"]:
            t.add("No expenses", color=MUTED)
        for category, amount in period["totals"].items():
            t.add(f"{category}: ", newline=False)
            t.add(f"₱{amount:,.2f}", bold=True)
        t.add(f"Total: ₱{period['total']:,.2f}", bold=True)
        t.add("")

    def show_result(self, result):
        self.show_period("First", result["first"])
        self.show_period("Second", result["second"])
        difference = result["difference"]
        if difference > 0:
            text = f"The first period cost ₱{difference:,.2f} more."
        elif difference < 0:
            text = f"The second period cost ₱{-difference:,.2f} more."
        else:
            text = "Both periods cost the same."
        self.text.add(text, bold=True, color=PINK, size=15)

    def draw_chart(self, result):
        self.chart.clear()
        first = result["first"]
        second = result["second"]

        all_cats = sorted(set(first["totals"]) | set(second["totals"]))
        if not all_cats:
            return

        x = np.arange(len(all_cats))
        width = 0.35

        ax = self.chart.subplot()
        vals1 = [first["totals"].get(c, 0) for c in all_cats]
        vals2 = [second["totals"].get(c, 0) for c in all_cats]

        bars1 = ax.bar(x - width/2, vals1, width, label="First Period", color="#6d28d9", alpha=0.85)
        bars2 = ax.bar(x + width/2, vals2, width, label="Second Period", color="#f472b6", alpha=0.85)

        ax.set_xticks(x)
        ax.set_xticklabels(all_cats, rotation=30, ha="right")
        ax.set_ylabel("Amount (₱)")
        ax.legend()
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        for bar in bars1:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width()/2, h, f"₱{h:,.0f}",
                        ha="center", va="bottom", fontsize=8)
        for bar in bars2:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width()/2, h, f"₱{h:,.0f}",
                        ha="center", va="bottom", fontsize=8)

        self.chart.refresh()