from PyQt6.QtGui import QTextCursor, QTextCharFormat, QColor

PINK = "#B0285A"
MUTED = "#5D4A51"


class StyledText:
    def __init__(self, text_edit):
        self.text_edit = text_edit

    def clear(self):
        self.text_edit.clear()

    def add(self, text, bold=False, color="#000000", size=14, newline=True):
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        style = QTextCharFormat()
        style.setFontWeight(700 if bold else 400)
        style.setForeground(QColor(color))
        style.setFontPointSize(size)
        cursor.insertText(text + ("\n" if newline else ""), style)