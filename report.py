import sys
import math
from pathlib import Path
import typing

from PyQt6 import uic
from PyQt6.QtWidgets import (
    QApplication,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
)
from PyQt6 import QtCore

import functions as f
from constants import Const as C
from validatedlineedit import ValidatedLineEdit


class OutputAN(typing.NamedTuple):
    summa: str  # Сумма
    NDS_including: bool  # Признак. НДС включен в сумму.


class Report(QMainWindow):
    edtClientsWithNDS: ValidatedLineEdit
    edtPaid: ValidatedLineEdit
    edtPaid_1: ValidatedLineEdit
    edtToCorporation: ValidatedLineEdit
    edtPercentNDS: ValidatedLineEdit
    lblPaid1: QLabel
    groupBoxInput: QGroupBox
    groupBoxHelp: QGroupBox
    formLayoutInput: QFormLayout
    edtClientsNDSOutput: QLineEdit
    edtClientsOutput: QLineEdit
    edtCorpNDSOutput: QLineEdit
    edtCorpOutput: QLineEdit
    edtLeftOutput:QLineEdit
    edtOverOutput: QLineEdit
    edtPaidOutput: QLineEdit

    def __init__(self) -> None:
        """Инициализация UI, атрибутов и подключение сигналов."""
        super().__init__()
        self.init_UI()  # Инициализация UI, подготовленного Qt Designer, в том числе установка атрибутов полей

        # Атрибуты хранят финансовые данные
        self.clients_with_nds = 0.0  # Заплачено клиентами с НДС
        self.clients = 0.0  # Заплачено клиентами без НДС
        self.corp = 0.0  # Подлежит перечислению в корпорацию без НДС
        self.corp_nds = 0.0  # В корпорацию, включая НДС
        self.left = 0.0  # Осталось заплатить, включая НДС
        self.over = 0.0  # Переплачено, включая НДС
        self.paid_all = 0.0  # Заплачено в корпорацию, включая НДС
        self.paid_1 = 0.0  # Первый платёж, включая НДС
        self.paid_list: list[float] = []
        self.percent_corp = C.PERCENT_CORP
        self.percent_NDS = (
            C.PERCENT_NDS
        )  # Процент НДС корпорации. C.PERCENT_NDS - значение по умолчанию.
        self.reference_values = {
            "percent_corp": self.percent_corp,
            "percent_NDS": self.percent_NDS,
        }
        self.input_line_edits = self._get_dict_input()
        self.output_line_edit = self._get_dict_output()

        self.lblPaid1.setText("Платёж № 1")
        self.setup_connections()  # Установка соединений сигналов и слотов
        self.set_event_filters()  # Установка фильтров событий для полей вывода
        self.set_custom_interface()  # Настройка внешнего вида интерфейса
        self.set_focus_policies()

    def init_UI(self) -> None:
        """Загрузка UI и атрибутов полей в объект класса"""

        exe_directory = (  # Директория, из которой была запущена программа
            Path(sys.argv[0]).parent
            if hasattr(sys, "frozen")  # exe файл, получен с помощью PyInstaller
            else Path(__file__).parent  # Если файл запущен как обычный Python-скрипт
        )

        ui_config_abs_path = exe_directory / C.NAME_UI
        uic.loadUi(ui_config_abs_path, self)
        if not hasattr(self, "edtPaid_1"):
            self.edtPaid_1 = self.edtPaid
            self.edtPaid_1.setObjectName("edtPaid_1")

    def setup_connections(self) -> None:
        """Для всех полей ввода назначает программу обработки сигнала завершения ввода"""
        for line_edit in self.input_line_edits.keys():
            line_edit.signal_focus_out.connect(self.handler_signal_focus_out)

    def set_event_filters(self) -> None:
        """Для всех полей вывода инициирует обработку кликов по полям."""
        for line_edit in self.output_line_edit.keys():
            line_edit.installEventFilter(self)

    def eventFilter(
            self,
            source: QtCore.QObject | None,
            event: QtCore.QEvent | None,
    ) -> bool:
        if (
                isinstance(source, QLineEdit)
                and event is not None
                and event.type() == QtCore.QEvent.Type.MouseButtonPress
        ):
            if f.put_clipboard(source):
                source.setStyleSheet(C.STYLE_COPIED)

        return super().eventFilter(source, event)

    def set_custom_interface(self) -> None:
        """Персонализирует интерфейс"""
        self.set_style_inputs()  # Устанавливает стиль для всех полей ввода информации
        self.edtToCorporation.setText(f"{self.percent_corp}")
        self.edtPercentNDS.setText(
            f"{self.percent_NDS}"
        )  # Устанавливает значение поля по умолчанию
        self._set_reference_help()

    def _set_reference_help(self) -> None:
        """Устанавливает подсказки для справочных параметров."""
        corp_help = (
            "Процент, перечисляемый в корпорацию. "
            "Изменение действует только в текущем сеансе."
        )
        nds_help = (
            "Ставка НДС, используемая при расчётах. "
            "Изменение действует только в текущем сеансе."
        )

        self.edtToCorporation.setToolTip(corp_help)
        self.edtToCorporation.setStatusTip(corp_help)
        self.edtToCorporation.setWhatsThis(corp_help)

        self.edtPercentNDS.setToolTip(nds_help)
        self.edtPercentNDS.setStatusTip(nds_help)
        self.edtPercentNDS.setWhatsThis(nds_help)

        output_help = "Кликните мышью, чтобы скопировать результат в буфер обмена."
        for line_edit in self.output_line_edit:
            line_edit.setToolTip(output_help)

    def set_focus_policies(self) -> None:
        """Исключает справочные поля из перехода клавишей Tab."""
        line_edits: list[ValidatedLineEdit] = (
            self.groupBoxHelp.findChildren(ValidatedLineEdit)
        )
        for line_edit in line_edits:
            line_edit.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)

    def set_style_inputs(self) -> None:
        """
        Устанавливает стиль для всех полей ввода информации
        Returns: None
        """

        for line_edit in self.input_line_edits:
            f.set_style_input(line_edit)

    def compute_and_display(self) -> None:
        """
        Выполняет вычисления финансовой информации и обновляет отображение значений в интерфейсе.

        Вызывает функции compute для расчётов, analysis_compute для анализа результатов и
        display для обновления интерфейса пользователя.
        """
        self.compute()
        self.analysis_compute()
        self.display()

    def compute(self) -> None:
        """
        Вычисляет основные финансовые показатели на основе введенных данных:
        - Сумма для корпорации без НДС.
        - Сумма для корпорации с НДС.
        - Общая сумма платежей.
        - Остаток платежей.
        """
        nds_clients = self.clients_with_nds * self.percent_NDS / (100 + self.percent_NDS)
        self.clients = round(self.clients_with_nds - nds_clients, 2)
        self.corp = round(self.clients * self.percent_corp / 100, 2)
        # noinspection PyPep8Naming
        nds_corp = self.corp * self.percent_NDS / 100
        self.corp_nds = round(self.corp + nds_corp, 2)
        self.paid_all =sum(self.paid_list)
        self.left = round(self.corp_nds - self.paid_all, 2)

    def analysis_compute(self) -> None:
        """
        Анализирует остаток долга после платежей.
        Если остаток отрицательный, устанавливает переплату.
        """
        if self.left < 0:
            self.over = -self.left
            self.left = 0.0
        elif math.isclose(self.left, 0.0, abs_tol=1e-9):
            self.left = 0.0
            self.over = 0.0
        else:
            self.over = 0.0

    def display(self) -> None:
        """
        Обновляет отображение всех выходных полей в интерфейсе.
        """
        for field in self.output_line_edit:
            field.setStyleSheet("")
            f.display_summa(
                field,  # Поле вывода финансового показателя
                # Значение финансового показателя
                getattr(self, self.output_line_edit[field].summa),
                # Признак. В сумму финансового показателя входит НДС.
                self.output_line_edit[field].NDS_including,
                self.percent_NDS,  # Процент НДС
            )

    def handler_signal_focus_out(self, obj: ValidatedLineEdit) -> None:
        """Обработчик сигнала выхода из фокуса поля ввода"""
        input_summa = f.parse_rubles(obj.text())

        if input_summa is None:
            return

        attribute_name = self.input_line_edits[obj]
        previous_value = getattr(self, attribute_name)
        setattr(self, attribute_name, input_summa)
        f.put_line_input(obj, input_summa)

        if attribute_name.startswith("paid_"):
            payment_number = int(attribute_name.removeprefix("paid_"))
            while len(self.paid_list) < payment_number:
                self.paid_list.append(0.0)
            self.paid_list[payment_number - 1] = input_summa

            if payment_number == len(self.paid_list):
                self._add_payment_input(payment_number + 1)
        elif (
            attribute_name in self.reference_values
            and not math.isclose(previous_value, input_summa, abs_tol=1e-9)
        ):
            self.reference_values[attribute_name] = input_summa
            self._show_reference_change_warning()

        self.compute_and_display()

    def _show_reference_change_warning(self) -> None:
        """Предупреждает об изменении справочных параметров."""
        QMessageBox.warning(
            self,
            "Изменение справочной информации",
            "Внимание! Изменение справочных значений может привести "
            "к неверным расчётам.\n\n"
            "Новое значение действует только в текущем сеансе программы. "
            "После перезапуска будет восстановлено значение по умолчанию.",
        )

    def _add_payment_input(self, payment_number: int) -> None:
        """Добавляет следующую строку платежа в форму."""
        attribute_name = f"edtPaid_{payment_number}"
        if hasattr(self, attribute_name):
            return

        label = QLabel(f"Платёж № {payment_number}", self.groupBoxInput)
        label.setObjectName(f"lblPaid{payment_number}")
        label.setFont(self.lblPaid1.font())
        label.setMinimumWidth(self.lblPaid1.minimumWidth())
        label.setMaximumWidth(self.lblPaid1.maximumWidth())
        label.setPalette(self.lblPaid1.palette())

        line_edit = ValidatedLineEdit(self.groupBoxInput)
        line_edit.setObjectName(attribute_name)
        line_edit.setFont(self.edtPaid_1.font())
        line_edit.setToolTip(f"Введите сумму платежа № {payment_number}")
        line_edit.setPlaceholderText(f"Введите сумму платежа № {payment_number}")
        f.set_style_input(line_edit)

        self.formLayoutInput.setWidget(
            payment_number,
            QFormLayout.ItemRole.LabelRole,
            label,
        )
        self.formLayoutInput.setWidget(
            payment_number,
            QFormLayout.ItemRole.FieldRole,
            line_edit,
        )

        setattr(self, attribute_name, line_edit)
        setattr(self, f"paid_{payment_number}", 0.0)
        self.input_line_edits[line_edit] = f"paid_{payment_number}"
        line_edit.signal_focus_out.connect(self.handler_signal_focus_out)

        previous_line_edit = getattr(self, f"edtPaid_{payment_number - 1}")
        self.setTabOrder(previous_line_edit, line_edit)
        QtCore.QTimer.singleShot(0, line_edit.setFocus)

    def _get_dict_input(self) -> dict:
        return {  # Словарь свойств виджетов ввода
            self.edtClientsWithNDS: "clients_with_nds",  # Поле ввода. "Клиенты" - Сумма, заплаченная клиентами (без НДС).
            self.edtPaid_1: "paid_1",  # Сумма первого платежа в корпорацию.
            self.edtToCorporation: "percent_corp",  # Процент отчислений корпорации.
            self.edtPercentNDS: "percent_NDS",  # Процент НДС, применяемый корпорацией.
        }  # Виджеты для ввода информации

    def _get_dict_output(self) -> dict:
        return {  # Словарь свойств виджетов вывода
            # Класс OutputAN - имеет 2 параметра: имя атрибута класса и признак, что НДС входит в сумму.
            # Поступило от клиентов c НДС.
            self.edtClientsOutput: OutputAN(summa="clients", NDS_including=False),
            # Перечислить в корпорацию без НДС.
            self.edtCorpOutput: OutputAN(summa="corp", NDS_including=False),
            # Перечислить в корпорацию с НДС.
            self.edtCorpNDSOutput: OutputAN(summa="corp_nds", NDS_including=True),
            self.edtPaidOutput: OutputAN(
                summa="paid_all", NDS_including=True
            ),  # Всего заплачено с НДС.
            self.edtLeftOutput: OutputAN(summa="left", NDS_including=True),  # Осталось заплатить с НДС.
            self.edtOverOutput: OutputAN(
                summa="over", NDS_including=True
            ),  # Переплачено с НДС.
        }  # Виджеты для вывода информации


# Запуск приложения
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Report()
    window.show()
    sys.exit(app.exec())
