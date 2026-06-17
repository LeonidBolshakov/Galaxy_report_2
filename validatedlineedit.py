from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression, Qt, pyqtSignal

from constants import Const as C


class ValidatedLineEdit(QLineEdit):
    """
    Класс для полей ввода. Базовый класс QLineEdit.
    В дополнение к базовому классу устанавливает валидатор, обрабатывает ошибки ввода
    и генерирует сигнал при потере фокуса. Сигнал нужен для обработки валидных введённых данных.
    """

    signal_focus_out = pyqtSignal(object)
    signal_invalid_focus_out = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._skip_next_focus_out = False
        self.setValidator(
            QRegularExpressionValidator(QRegularExpression(C.RE_INPUT_DOUBLE))
        )

    def keyPressEvent(self, event):
        """Enter завершает ввод: сначала отправляет сигнал, затем переносит фокус."""
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._skip_next_focus_out = True
            if self.hasAcceptableInput():
                self.setStyleSheet("")
                self.signal_focus_out.emit(self)
            else:
                self.setStyleSheet(C.STYLE_ERROR)
                self.signal_invalid_focus_out.emit(self)
            self.focusNextChild()
            event.accept()
            return

        super().keyPressEvent(event)

    def focusOutEvent(self, event):
        """Переопределяет метод обработки события потери фокуса."""
        if self.hasAcceptableInput():
            # Устанавливает стиль поля ввода при валидном значении и инициирует сигнал
            self.setStyleSheet("")
            if self._skip_next_focus_out:
                self._skip_next_focus_out = False
            else:
                self.signal_focus_out.emit(self)
        else:
            # Устанавливает стиль поля ввода при невалидном значении.
            self.setStyleSheet(C.STYLE_ERROR)
            if self._skip_next_focus_out:
                self._skip_next_focus_out = False
            else:
                self.signal_invalid_focus_out.emit(self)
        super().focusOutEvent(event)
