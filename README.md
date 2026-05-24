# 🍳 Автоматический кулинарный блог для Яндекс Дзен

Скрипт каждый день в 11:00 МСК:
1. Выбирает тему рецепта
2. Генерирует статью через Claude
3. Подбирает картинку через Unsplash
4. Обновляет RSS-фид
5. Яндекс Дзен сам подхватывает новую статью

---

## Пошаговая установка

### Шаг 1 — Создать репозиторий на GitHub

1. Зайди на [github.com](https://github.com) и зарегистрируйся (если нет аккаунта)
2. Нажми **New repository**
3. Название: `food-blog`
4. Поставь галочку **Public** (нужно для GitHub Pages)
5. Нажми **Create repository**
6. Загрузи все файлы из этой папки в репозиторий

### Шаг 2 — Получить API-ключи

**Claude API:**
1. Зайди на [console.anthropic.com](https://console.anthropic.com)
2. Раздел **API Keys** → **Create Key**
3. Скопируй ключ (начинается с `sk-ant-...`)

**Unsplash API (бесплатно):**
1. Зайди на [unsplash.com/developers](https://unsplash.com/developers)
2. **Your apps** → **New Application**
3. Название: `food-blog`, соглашаешься с условиями
4. Скопируй **Access Key**

### Шаг 3 — Добавить секреты в GitHub

В своём репозитории: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Добавь три секрета:

| Название | Значение |
|----------|----------|
| `ANTHROPIC_API_KEY` | твой ключ Claude (sk-ant-...) |
| `UNSPLASH_ACCESS_KEY` | твой ключ Unsplash |
| `BLOG_BASE_URL` | `https://ТВО_ЛОГИН.github.io/food-blog` |

### Шаг 4 — Включить GitHub Pages

В репозитории: **Settings** → **Pages**
- Source: **Deploy from a branch**
- Branch: `main`, папка `/feed`
- Нажми **Save**

Через 2-3 минуты RSS-фид будет доступен по адресу:
```
https://ТВО_ЛОГИН.github.io/food-blog/feed.xml
```

### Шаг 5 — Подключить RSS к Яндекс Дзен

1. Зайди в [dzen.ru/profile/editor](https://dzen.ru/profile/editor)
2. **Настройки** → **Источники** → **Добавить RSS**
3. Вставь ссылку на свой фид: `https://ТВО_ЛОГИН.github.io/food-blog/feed.xml`
4. Дзен сам будет проверять фид и публиковать новые статьи

### Шаг 6 — Первый запуск (тест)

1. В репозитории иди во вкладку **Actions**
2. Слева выбери **Публикация статьи**
3. Нажми **Run workflow** → **Run workflow**
4. Дождись зелёной галочки (~1-2 минуты)
5. Проверь `feed/feed.xml` — там должна появиться первая статья

---

## Структура файлов

```
food-blog/
├── .github/
│   └── workflows/
│       └── daily_post.yml    ← расписание запуска
├── scripts/
│   └── generate_article.py  ← основной скрипт
├── feed/
│   ├── feed.xml              ← RSS (обновляется автоматически)
│   └── items.json            ← база всех статей
└── used_topics.json          ← чтобы темы не повторялись
```

## Как добавить свои темы

Открой `scripts/generate_article.py`, найди список `FOOD_TOPICS` и добавляй свои темы в том же формате.

## Расходы

| Сервис | Стоимость |
|--------|-----------|
| GitHub Actions | Бесплатно (2000 мин/месяц, нам нужно ~30) |
| GitHub Pages | Бесплатно |
| Unsplash API | Бесплатно (5000 запросов/час) |
| Claude API | ~$0.01-0.03 за статью |

Итого: **около 30-90 рублей в месяц** только за Claude API.
