from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression, pyqtSignal

from constants import Const as C


class ValidatedLineEdit(QLineEdit):
    """
    Класс для полей ввода. Базовый класс QLineEdit.
    В дополнение к базовому классу устанавливает валидатор, обрабатывает ошибки ввода
    и генерирует сигнал при потере фокуса. Сигнал нужен для обработки валидных введённых данных.
    """

    signal_focus_out = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._submitted_by_enter = False
        self.setValidator(
            QRegularExpressionValidator(QRegularExpression(C.RE_INPUT_DOUBLE))
        )
        self.returnPressed.connect(self._submit_by_enter)

    def _submit_by_enter(self) -> None:
        """Завершает ввод по Enter и снимает фокус с поля."""
        self._submitted_by_enter = True
        self.signal_focus_out.emit(self)
        self.clearFocus()

    def focusOutEvent(self, event):
        """Переопределяет метод обработки события потери фокуса."""
        if self.hasAcceptableInput():
            # Устанавливает стиль поля ввода при валидном значении и инициирует сигнал
            self.setStyleSheet("")
            if self._submitted_by_enter:
                self._submitted_by_enter = False
            else:
                self.signal_focus_out.emit(self)
        else:
            # Устанавливает стиль поля ввода при невалидном значении.
            self.setStyleSheet(C.STYLE_ERROR)
        super().focusOutEvent(event)
