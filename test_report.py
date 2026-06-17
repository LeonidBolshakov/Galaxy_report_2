from unittest.mock import MagicMock

import pytest
from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication, QLineEdit

from constants import Const as C
from report import Report
from validatedlineedit import ValidatedLineEdit


NO_MODIFIER = Qt.KeyboardModifier.NoModifier
DEFAULT_POS = QPoint()
NO_DELAY = -1


@pytest.fixture(scope="session")
def app():
    application = QApplication.instance() or QApplication([])
    return application


@pytest.fixture
def window(app):
    report = Report()
    report.show()
    yield report
    report.close()


def find_required_child(parent, widget_type, name):
    child = parent.findChild(widget_type, name)
    assert child is not None, f"Widget {name!r} was not found"
    return child


def get_payment_field(window, number: int):
    field_name = f"edtPaid_{number}"
    assert hasattr(window, field_name), f"Payment field {field_name!r} was not found"
    field = getattr(window, field_name)
    assert isinstance(field, ValidatedLineEdit)
    return field


def test_input_validation_and_display(window):
    clients_widget = find_required_child(window, ValidatedLineEdit, "edtClientsWithNDS")
    total_clients_widget = find_required_child(window, QLineEdit, "edtClientsOutput")
    corporation_without_NDS_widget = find_required_child(
        window, QLineEdit, "edtCorpOutput"
    )
    corporation_with_NDS_widget = find_required_child(
        window, QLineEdit, "edtCorpNDSOutput"
    )
    left_widget = find_required_child(window, QLineEdit, "edtLeftOutput")
    over_widget = find_required_child(window, QLineEdit, "edtOverOutput")

    clients_widget.setText("100")
    window.handler_signal_focus_out(clients_widget)
    QApplication.processEvents()

    assert total_clients_widget.text() == (
        "81.97 руб. (Восемьдесят один рубль 97 коп.)"
    )
    assert corporation_without_NDS_widget.text() == (
        "40.98 руб. (Сорок рублей 98 коп.)"
    )
    assert corporation_with_NDS_widget.text() == (
        "50.00 руб. (Пятьдесят рублей 00 коп.), включая НДС "
        "9.02 руб. (Девять рублей 02 коп.)"
    )
    assert left_widget.text() == (
        "50.00 руб. (Пятьдесят рублей 00 коп.), включая НДС "
        "9.02 руб. (Девять рублей 02 коп.)"
    )
    assert over_widget.text() == (
        "0.00 руб. (Ноль рублей 00 коп.), включая НДС "
        "0.00 руб. (Ноль рублей 00 коп.)"
    )


def test_clipboard_copy(window, monkeypatch):
    mock_clipboard = MagicMock()
    monkeypatch.setattr("functions.QApplication.clipboard", lambda: mock_clipboard)
    monkeypatch.setattr("functions.show_message", MagicMock())

    output_widget = find_required_child(window, QLineEdit, "edtClientsOutput")
    output_widget.setText("100.00 руб. (Сто рублей 00 коп.)")
    QTest.mouseClick(
        output_widget,
        Qt.MouseButton.LeftButton,
        NO_MODIFIER,
        DEFAULT_POS,
        NO_DELAY,
    )

    mock_clipboard.setText.assert_called_once_with(
        "100.00 руб. (Сто рублей 00 коп.)"
    )
    assert output_widget.styleSheet() == C.STYLE_COPIED


def test_dynamic_payment_fields_are_added_once(window):
    window.edtPaid_1.setText("100")
    window.handler_signal_focus_out(window.edtPaid_1)
    QApplication.processEvents()
    paid_2 = get_payment_field(window, 2)

    assert paid_2.objectName() == "edtPaid_2"
    assert window.focusWidget() is paid_2
    assert window.paid_list == [100.0]

    paid_2.setText("50")
    window.handler_signal_focus_out(paid_2)
    QApplication.processEvents()
    paid_3 = get_payment_field(window, 3)

    assert paid_3.objectName() == "edtPaid_3"
    assert window.focusWidget() is paid_3
    assert window.paid_list == [100.0, 50.0]

    window.handler_signal_focus_out(window.edtPaid_1)
    assert get_payment_field(window, 2).objectName() == "edtPaid_2"
    assert window.paid_list == [100.0, 50.0]


def test_reference_change_can_be_rejected_or_accepted(window, monkeypatch):
    confirm = MagicMock(side_effect=[False, True])
    monkeypatch.setattr(window, "_confirm_reference_change", confirm)

    window.handler_signal_focus_out(window.edtPercentNDS)
    confirm.assert_not_called()

    window.edtPercentNDS.setText("20")
    window.handler_signal_focus_out(window.edtPercentNDS)
    assert window.percent_NDS == C.PERCENT_NDS
    assert window.edtPercentNDS.text() == "22.00"

    window.edtToCorporation.setText("45")
    window.handler_signal_focus_out(window.edtToCorporation)
    assert window.percent_corp == 45.0
    assert confirm.call_count == 2


def test_empty_reference_fields_are_restored(window, monkeypatch):
    def assert_some_reference_field_is_empty(*args):
        assert window.edtToCorporation.text() == "" or window.edtPercentNDS.text() == ""

    show_message = MagicMock(side_effect=assert_some_reference_field_is_empty)
    monkeypatch.setattr("report.f.show_message", show_message)

    window.edtToCorporation.clear()
    window.edtToCorporation.signal_invalid_focus_out.emit(window.edtToCorporation)
    assert window.edtToCorporation.text() == "50.00"
    assert window.percent_corp == C.PERCENT_CORP

    window.edtPercentNDS.clear()
    window.edtPercentNDS.signal_invalid_focus_out.emit(window.edtPercentNDS)
    assert window.edtPercentNDS.text() == "22.00"
    assert window.percent_NDS == C.PERCENT_NDS
    assert show_message.call_count == 2


def test_copied_output_style_is_reset_after_display(window, monkeypatch):
    monkeypatch.setattr("functions.QApplication.clipboard", lambda: MagicMock())
    monkeypatch.setattr("functions.show_message", MagicMock())
    output_widget = window.edtClientsOutput
    output_widget.setText("Результат")

    QTest.mouseClick(
        output_widget,
        Qt.MouseButton.LeftButton,
        NO_MODIFIER,
        DEFAULT_POS,
        NO_DELAY,
    )
    QApplication.processEvents()

    assert output_widget.styleSheet() == C.STYLE_COPIED

    window.display()
    assert output_widget.styleSheet() == ""


def test_enter_behaves_like_tab_for_reference_field(window, monkeypatch):
    window.edtToCorporation.setFocus()
    window.edtToCorporation.setText("45")
    monkeypatch.setattr(window, "_confirm_reference_change", lambda: True)

    QTest.keyClick(window.edtToCorporation, Qt.Key.Key_Return, NO_MODIFIER, NO_DELAY)
    QApplication.processEvents()

    assert window.percent_corp == 45.0
    assert window.focusWidget() is window.edtClientsWithNDS


def test_enter_restores_empty_reference_field(window, monkeypatch):
    show_message = MagicMock()
    monkeypatch.setattr("report.f.show_message", show_message)
    window.edtPercentNDS.setFocus()
    window.edtPercentNDS.clear()

    QTest.keyClick(window.edtPercentNDS, Qt.Key.Key_Return, NO_MODIFIER, NO_DELAY)
    QApplication.processEvents()

    show_message.assert_called_once()
    assert window.edtPercentNDS.text() == "22.00"
    assert window.focusWidget() is window.edtPercentNDS


def test_enter_creates_next_payment_field(window):
    window.edtPaid_1.setFocus()
    window.edtPaid_1.setText("100")

    QTest.keyClick(window.edtPaid_1, Qt.Key.Key_Return, NO_MODIFIER, NO_DELAY)
    QApplication.processEvents()

    assert window.paid_list == [100.0]
    assert window.focusWidget() is get_payment_field(window, 2)
