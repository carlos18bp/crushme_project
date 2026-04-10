---
name: blog-ai-weekly
description: "Weekly AI blog post creation — search news from 10 sources, summarize, write bilingual ES+EN article, and publish via Django shell."
disable-model-invocation: true
allowed-tools: Bash, WebSearch, WebFetch
---

# Blog AI Weekly — Crear articulo semanal de IA

Workflow para crear un articulo de blog cada ~7 dias basado en noticias relevantes de inteligencia artificial.

## Paso 1 — Buscar noticias de IA

Buscar noticias recientes de IA en estas **10 fuentes principales**:

| # | Fuente | Dominio |
|---|--------|---------|
| 1 | OpenAI Blog | openai.com/blog |
| 2 | Google AI Blog | blog.google/technology/ai |
| 3 | Meta AI Blog | ai.meta.com/blog |
| 4 | Microsoft AI Blog | blogs.microsoft.com/ai |
| 5 | Hugging Face Blog | huggingface.co/blog |
| 6 | TechCrunch AI | techcrunch.com (AI section) |
| 7 | The Verge AI | theverge.com (AI section) |
| 8 | arXiv Trending | arxiv.org (trending AI papers) |
| 9 | VentureBeat AI | venturebeat.com/ai |
| 10 | Ars Technica AI | arstechnica.com (AI section) |

Recopilar al menos **5-8 noticias relevantes** con titulo, resumen breve y URL fuente.

## Paso 2 — Seleccionar tema

1. Identificar el tema mas relevante o trending de la semana.
2. Si hay varios temas fuertes, presentar un **top 3** con contexto.
3. Preguntar al usuario cual tema prefiere.

## Paso 3 — Redactar el articulo (bilingue ES + EN)

### Titulos
- Atractivo, SEO-friendly, max 80 caracteres por idioma.

### Excerpts
- 1-2 oraciones, max 200 caracteres por idioma.
- No traduccion literal — adaptar tono a cada audiencia.

### Contenido (HTML)
```html
<h2>Titulo principal</h2>
<p>Introduccion y contexto...</p>
<h3>Subtema 1</h3>
<p>Desarrollo...</p>
<h3>Impacto y perspectiva</h3>
<p>Conclusion...</p>
```

### Reglas de redaccion
- Tono profesional pero accesible.
- No copiar/pegar — resumir y aportar analisis.
- 400-800 palabras por idioma.
- El contenido en ingles NO es traduccion literal del espanol.

### Sources (JSON)
```json
[
  {"name": "OpenAI Blog", "url": "https://openai.com/blog/..."},
  {"name": "TechCrunch", "url": "https://techcrunch.com/..."}
]
```

## Paso 4 — Imagen de portada

Preguntar al usuario:
- **Opcion A**: Proporcionar URL de imagen
- **Opcion B**: Generar descripcion para IA (DALL-E, Midjourney)
- **Opcion C**: Sin imagen por ahora

## Paso 5 — Crear el blog post

Presentar resumen al usuario. Si aprueba, crear via Django shell:

```bash
source /home/ryzepeck/webapps/crushme_project/backend/venv/bin/activate && python /home/ryzepeck/webapps/crushme_project/backend/manage.py shell -c "
from content.models import BlogPost
from django.utils import timezone

post = BlogPost.objects.create(
    title_es='TITULO_ES',
    title_en='TITLE_EN',
    excerpt_es='EXCERPT_ES',
    excerpt_en='EXCERPT_EN',
    content_es='''HTML_ES''',
    content_en='''HTML_EN''',
    sources=SOURCES_JSON,
    cover_image='URL_O_VACIO',
    is_published=True,
    published_at=timezone.now(),
)
print(f'Blog post created: {post.title_es} (slug: {post.slug}, id: {post.id})')
"
```

## Paso 6 — Verificar

```bash
source /home/ryzepeck/webapps/crushme_project/backend/venv/bin/activate && python /home/ryzepeck/webapps/crushme_project/backend/manage.py shell -c "
from content.models import BlogPost
post = BlogPost.objects.filter(is_published=True).first()
print(f'Latest: {post.title_es} | Slug: {post.slug} | Sources: {len(post.sources)}')
"
```