# Forbidden Castle of Lockers 🏰🔒

Настольное приложение на PyQt5 для визуального учёта и планировки локеров/ячейкохранилищ поверх схемы помещения.

![screenshot](docs/screenshot.png)

## ✨ Возможности
- Добавление локеров по одному и сеткой.
- Перетаскивание, масштабирование, привязка к сетке.
- Нумерация, владельцы и инв. номера.
- JSON сохранение/загрузка, автосейв.
- Экспорт в TXT и Excel.
- Лимиты по вместимости.

## 🚀 Установка
```
bash
git clone https://github.com/<твой-аккаунт>/forbidden-castle.git
cd forbidden-castle
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

## 📄 requirements.txt
```
PyQt5>=5.15.0
openpyxl>=3.1.0
```

## ▶️ Запуск
```
py -3 -m lockers.app
```
## 📂 Структура
```
lockers/
  core/        # логика и состояние
  ui/          # интерфейс
  utils/       # вспомогалки
legacy_app.py  # старая версия (для истории)

```

## 📌 Roadmap
 ```
 Drag&drop картинок в фон.

 Поиск по владельцам.

 Экспорт в PDF.
```

👥 Авторы
Yahont Ruby и
Сеточка ✨
---

### 📄 `CHANGELOG.md`

```markdown
# Changelog
Все заметные изменения в этом проекте будут задокументированы в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/).

## [Unreleased]
### Добавлено
- Возможность подключать внешний фон через диалог.
- Экспорт в TXT и Excel.

### Изменено
- `LockerItem` вынесен в отдельный модуль.
- `LockerScene` отделена от главного окна.
- Автосейв теперь каждые 60 секунд.

### Исправлено
- Привязка к сетке иногда смещала локеры не туда.
- Краш при пустом JSON.

## [0.1.0] - 2025-08-31
### Добавлено
- Первая рабочая версия (`legacy_app.py`).
