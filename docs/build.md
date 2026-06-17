# Сборка exe

Проект собирается в Windows-приложение с помощью PyInstaller.

## Требования

Перед сборкой должно быть создано виртуальное окружение и установлены
зависимости проекта:

```powershell
python -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt
```

`pyinstaller` указан в `requirements.txt`, поэтому отдельная установка обычно
не нужна. Если виртуальное окружение уже было создано раньше, зависимости можно
обновить той же командой установки из `requirements.txt`.

## Запуск сборки

Основной способ:

```powershell
.\\build_pyinstaller.bat
```

Скрипт выполняет несколько проверок:

- переходит в папку проекта;
- проверяет наличие `.venv\\Scripts\\python.exe`;
- проверяет наличие `Galaxy_report.spec`;
- проверяет, что PyInstaller установлен в виртуальном окружении;
- запускает сборку с параметрами `--clean --noconfirm`.

## Результат сборки

Готовое приложение создаётся здесь:

```text
dist\\galaxy_report\\galaxy_report.exe
```

Запускать нужно именно этот файл из папки `dist`.

Файл из папки `build` запускать не нужно: это промежуточный результат
PyInstaller. В нём может не быть всех DLL и ресурсов, необходимых приложению.

## Роль Galaxy_report.spec

`Galaxy_report.spec` описывает, как PyInstaller собирает приложение:

- точка входа сборки: `report.py`;
- имя exe: `galaxy_report.exe`;
- режим без консольного окна: `console=False`;
- файл интерфейса `_internal\\report.ui` добавляется в сборку.

Важная строка:

```python
datas=[
    ('_internal\\report.ui', '.'),
]
```

Она кладёт `report.ui` в папку:

```text
dist\\galaxy_report\\_internal\\report.ui
```

Именно этот путь ожидает приложение при запуске из собранного exe.

## Проверка после сборки

После сборки стоит проверить:

1. Запускается ли `dist\\galaxy_report\\galaxy_report.exe`.
2. Открывается ли главное окно.
