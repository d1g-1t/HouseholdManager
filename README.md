# HouseholdManager

Бэкенд семейного бюджет-менеджера с OCR распознаванием чеков, ML-категоризацией расходов и real-time синхронизацией.

## Стек

**Backend:** Django 5.0, Django Ninja, Pydantic v2  
**База данных:** PostgreSQL 16, Redis 7  
**Асинхронность:** Celery, Django Channels, WebSocket  
**ML/OCR:** Scikit-learn, Tesseract, OpenCV  
**Инфраструктура:** Docker Compose, Prometheus

## Запуск

```bash
git clone https://github.com/yourusername/HouseholdManager.git
cd HouseholdManager
make setup
```

**Сервисы:**
- API: http://localhost:8000/api/docs
- Admin: http://localhost:8000/admin
- Flower: http://localhost:5555

## Команды

```bash
make setup       # Полная установка
make docker-up   # Запуск сервисов
make docker-down # Остановка
make test        # Тесты
make superuser   # Создать админа
make shell       # Django shell
```

## Архитектура

```
├── apps/
│   ├── users/          # JWT-аутентификация
│   ├── families/       # Мультитенантность
│   ├── expenses/       # CRUD расходов
│   ├── receipts/       # OCR чеков
│   ├── categories/     # Категории
│   ├── budgets/        # Бюджеты и лимиты
│   ├── analytics/      # Аналитика
│   ├── notifications/  # WebSocket уведомления
│   ├── telegram_bot/   # Telegram интеграция
│   └── ml_categorizer/ # ML категоризация
├── household_manager/  # Django settings
├── docker-compose.yml  # 6 сервисов
└── Makefile
```

## API

Swagger документация: `/api/docs`

**Эндпоинты:**
- `/api/users/` - Регистрация, JWT токены
- `/api/families/` - Управление семьями
- `/api/expenses/` - Расходы
- `/api/receipts/` - Загрузка чеков
- `/api/budgets/` - Бюджеты
- `/api/categories/` - Категории
- `/api/analytics/` - Отчёты

## Docker сервисы

| Сервис | Порт | Описание |
|--------|------|----------|
| web | 8000 | Django API |
| db | 5432 | PostgreSQL |
| redis | 6379 | Cache/Broker |
| celery_worker | - | Фоновые задачи |
| celery_beat | - | Планировщик |
| flower | 5555 | Мониторинг Celery |

## Требования

- Docker & Docker Compose
- Make (Linux/macOS) или make.bat (Windows)

## Лицензия

MIT
