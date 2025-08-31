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
```bash
git clone https://github.com/<твой-аккаунт>/forbidden-castle.git
cd forbidden-castle
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install -r requirements.txt
