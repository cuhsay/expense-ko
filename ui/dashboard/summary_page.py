from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QDateEdit,
    QTextEdit, QLabel, QSplitter,
)
from PyQt6.QtCore import QDate
from dashboard.view_summary import ViewSummary
from ui.dashboard.chart_widgets import ChartWidget
from ui.dashboard.styled_text import StyledText, PINK, MUTED
from typing import override
import numpy as np


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

        splitter = QSplitter()
        layout.addWidget(splitter)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.text = StyledText(self.output)

        self.chart = ChartWidget(figsize=(8, 5))
        splitter.addWidget(self.output)
        splitter.addWidget(self.chart)

        self.period_input.currentIndexChanged.connect(self.refresh)
        self.date_input.dateChanged.connect(self.refresh)

    @override
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
        data = self.summary.day_summary(day)
        t = self.text
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

        self.draw_day_chart(data)

    def draw_day_chart(self, data):
        self.chart.clear()
        totals = data["totals"]
        if not totals:
            return

        ax = self.chart.subplot()
        cats = list(totals.keys())
        vals = [totals[c] for c in cats]
        colors = ["#6d28d9", "#f472b6", "#34d399", "#fbbf24", "#60a5fa",
                   "#f97316", "#a78bfa", "#fb923c", "#4ade80", "#f87171"]

        wedges, texts, autotexts = ax.pie(
            vals, labels=None, autopct="%1.1f%%",
            colors=colors[:len(cats)], startangle=140,
            textprops={"fontsize": 9},
        )
        for at in autotexts:
            at.set_fontsize(8)

        ax.legend(wedges, [f"{c} — ₱{v:,.2f}" for c, v in zip(cats, vals)],
                  title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1),
                  fontsize=8)
        self.chart.refresh()

    def show_week(self, day):
        t = self.text
        days = self.summary.week_breakdown(day)
        for d in days:
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

        self.draw_week_chart(days)

    def draw_week_chart(self, days):
        self.chart.clear()
        has_any = any(d["expenses"] for d in days)
        if not has_any:
            return

        day_labels = [d["day_name"][:3] for d in days]
        day_totals = [sum(e.amount for e in d["expenses"]) for d in days]

        ax = self.chart.subplot()
        x = np.arange(len(day_labels))
        bars = ax.bar(x, day_totals, color="#6d28d9", alpha=0.85, width=0.6)
        ax.set_xticks(x)
        ax.set_xticklabels(day_labels)
        ax.set_ylabel("Total (₱)")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width()/2, h, f"₱{h:,.0f}",
                        ha="center", va="bottom", fontsize=8)

        self.chart.refresh()