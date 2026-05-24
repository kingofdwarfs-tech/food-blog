import requests
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
import random

GROQ_API_KEY = os.environ["GROQ_API_KEY"]
UNSPLASH_ACCESS_KEY = os.environ["UNSPLASH_ACCESS_KEY"]
BLOG_URL = os.environ["BLOG_BASE_URL"]

FOOD_TOPICS = [
    "рецепт борща с говядиной", "блюда из курицы быстрый ужин",
    "домашняя паста рецепт", "выпечка на кефире", "салат с авокадо",
    "суп-пюре из тыквы", "блины на молоке классические", "пирог с яблоками",
    "котлеты домашние сочные", "рецепт оливье", "лазанья домашняя",
    "торт без выпечки", "рыба в духовке", "плов узбекский",
    "шарлотка простой рецепт", "роллы дома", "гречка с грибами",
    "запеканка из творога", "маринованные огурцы быстро", "холодец рецепт",
]

def pick_topic(used_topics_file="used_topics.json"):
    used = []
    if Path(used_topics_file).exists():
        with open(used_topics_file) as f:
            used = json.load(f)
    available = [t for t in FOOD_TOPICS if t not in used]
    if not available:
        used = []
        available = FOOD_TOPICS[:]
    topic = random.choice(available)
    used.append(topic)
    with open(used_topics_file, "w") as f:
        json.dump(used, f, ensure_ascii=False, indent=2)
    return topic


def generate_article(topic: str) -> dict:
    prompt = f"""Напиши кулинарную статью для Яндекс Дзен на тему: "{topic}".

Статья должна содержать:
1. Цепляющий заголовок (без кавычек, до 80 символов)
2. Вводный абзац (2-3 предложения, почему это блюдо стоит попробовать)
3. Список ингредиентов (с количеством)
4. Пошаговый рецепт (5-8 шагов)
5. Советы и лайфхаки (2-3 пункта)
6. Заключительный абзац

Стиль: дружелюбный, разговорный, как будто рассказывает подруга. Объём: 600-800 слов.

Ответь ТОЛЬКО в JSON формате без markdown-блоков и без ```json:
{{
  "title": "заголовок",
  "description": "краткое описание для анонса (1-2 предложения)",
  "content_html": "полный HTML текст статьи",
  "image_search_query": "английский поисковый запрос для Unsplash (2-3 слова)"
}}"""

    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.9,
            "max_tokens": 2048,
        },
        timeout=60,
    )
    resp.raise_for_status()

    raw = resp.json()["choices"][0]["message"]["content"].strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(raw)


def get_image_url(search_query: str) -> str:
    resp = requests.get(
        "https://api.unsplash.com/search/photos",
        params={
            "query": search_query,
            "per_page": 10,
            "orientation": "landscape",
            "client_id": UNSPLASH_ACCESS_KEY,
        },
        timeout=10,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if not results:
        return ""
    return random.choice(results[:5])["urls"]["regular"]


def load_feed(feed_path: str) -> list:
    if not Path(feed_path).exists():
        return []
    with open(feed_path) as f:
        return json.load(f)


def save_feed(feed_path: str, items: list):
    with open(feed_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def build_rss(items: list, blog_url: str) -> str:
    rss = Element("rss", version="2.0")
    rss.set("xmlns:media", "http://search.yahoo.com/mrss/")
    rss.set("xmlns:content", "http://purl.org/rss/1.0/modules/content/")

    channel = SubElement(rss, "channel")
    SubElement(channel, "title").text = "Кулинарный блог Ольги"
    SubElement(channel, "link").text = blog_url
    SubElement(channel, "description").text = "Простые и вкусные рецепты каждый день"
    SubElement(channel, "language").text = "ru"
    SubElement(channel, "lastBuildDate").text = datetime.now(timezone.utc).strftime(
        "%a, %d %b %Y %H:%M:%S +0000"
    )

    for item_data in items[:30]:
        item = SubElement(channel, "item")
        SubElement(item, "title").text = item_data["title"]
        SubElement(item, "link").text = f"{blog_url}/articles/{item_data['id']}.html"
        SubElement(item, "description").text = item_data["description"]
        SubElement(item, "pubDate").text = item_data["pub_date"]
        SubElement(item, "guid").text = item_data["id"]

        content = SubElement(item, "content:encoded")
        html = item_data["content_html"]
        if item_data.get("image_url"):
            img_tag = f'<img src="{item_data["image_url"]}" alt="{item_data["title"]}" style="max-width:100%;"/><br/>'
            html = img_tag + html
        content.text = html

        if item_data.get("image_url"):
            media = SubElement(item, "media:content")
            media.set("url", item_data["image_url"])
            media.set("medium", "image")

    xmlstr = minidom.parseString(tostring(rss, encoding="unicode")).toprettyxml(indent="  ")
    return "\n".join(xmlstr.split("\n")[1:])


def main():
    feed_path = "feed/items.json"
    rss_path = "feed/feed.xml"

    topic = pick_topic()
    print(f"Тема: {topic}")

    article = generate_article(topic)
    print(f"Заголовок: {article['title']}")

    image_url = ""
    try:
        image_url = get_image_url(article["image_search_query"])
        print(f"Картинка: {image_url}")
    except Exception as e:
        print(f"Не удалось получить картинку: {e}")

    item = {
        "id": str(uuid.uuid4()),
        "title": article["title"],
        "description": article["description"],
        "content_html": article["content_html"],
        "image_url": image_url,
        "pub_date": datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000"),
        "topic": topic,
    }

    items = load_feed(feed_path)
    items.insert(0, item)
    save_feed(feed_path, items)

    rss_xml = build_rss(items, BLOG_URL)
    Path("feed").mkdir(exist_ok=True)
    with open(rss_path, "w", encoding="utf-8") as f:
        f.write(rss_xml)

    print(f"Готово! Статей в фиде: {len(items)}")


if __name__ == "__main__":
    main()
