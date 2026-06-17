from unittest.mock import MagicMock

import pytest

from functions import (
    extract_NDS,
    filter_rubles,
    parse_rubles,
    show_summa,
    summa_to_words,
)


def test_filter_rubles():
    assert filter_rubles("12345.67") == "12345.67"
    assert filter_rubles("-372") == "-372"
    assert filter_rubles("1к2345.678") == "1к2345.678"
    assert filter_rubles("1 234'5.678") == "12345.678"


def test_parse_rubles():
    assert parse_rubles("1234.567") == 1234.57
    assert parse_rubles("1'234.56") == 1234.56
    assert parse_rubles("1000") == 1000.00
    assert parse_rubles("") == 0.0


def test_extract_NDS():
    assert extract_NDS(1000.0, 5.0) == pytest.approx(47.61904761904762)
    assert extract_NDS(1234.56, 5.0) == pytest.approx(58.78857142857142)
    assert extract_NDS(0.0, 5.0) == 0.0
    assert extract_NDS(1000.0, 0.0) == 0.0
    assert extract_NDS(-1000.0, 5.0) == pytest.approx(-47.61904761904762)


def test_amount_to_words():
    assert summa_to_words(1234.56) == (
        "Одна тысяча двести тридцать четыре рубля 56 коп."
    )
    assert summa_to_words(1.01) == "Один рубль 01 коп."
    assert summa_to_words(2.02) == "Два рубля 02 коп."
    assert summa_to_words(5.05) == "Пять рублей 05 коп."
    assert summa_to_words(21.21) == "Двадцать один рубль 21 коп."
    assert summa_to_words(11.11) == "Одиннадцать рублей 11 коп."
    assert summa_to_words(14.14) == "Четырнадцать рублей 14 коп."
    assert summa_to_words(0.99) == "Ноль рублей 99 коп."
    assert summa_to_words(0.0) == "Ноль рублей 00 коп."
    assert summa_to_words(1000000.00) == "Один миллион рублей 00 коп."
    assert summa_to_words(-1234567.127) == (
        "Минус один миллион двести тридцать четыре тысячи пятьсот "
        "шестьдесят семь рублей -13 коп."
    )


def test_show_summa():
    assert show_summa(1234.56) == (
        "1234.56 руб. (Одна тысяча двести тридцать четыре рубля 56 коп.)"
    )
    assert show_summa(0.0) == "0.00 руб. (Ноль рублей 00 коп.)"
    assert show_summa(1.0145) == "1.01 руб. (Один рубль 01 коп.)"


def test_parse_rubles_edge_cases():
    assert parse_rubles(".123") == 0.12
    assert parse_rubles("123.") == 123.0
    assert parse_rubles("  1234.56  ") == 1234.56


def test_parse_rubles_error_case(monkeypatch):
    mock_msgbox = MagicMock()
    mock_instance = MagicMock()
    mock_msgbox.return_value = mock_instance
    monkeypatch.setattr("functions.QMessageBox", mock_msgbox)

    assert parse_rubles(".123.") is None
    mock_msgbox.assert_called_once()
    mock_instance.exec.assert_called_once()


def test_amount_to_words_negative():
    assert summa_to_words(-1234.56) == (
        "Минус одна тысяча двести тридцать четыре рубля -56 коп."
    )
