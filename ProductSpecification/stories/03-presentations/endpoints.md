# Презентации и прогресс — API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/presentations | Создать черновик (название). Ответ — презентация со статусом draft |
| GET | /api/v1/presentations/{id} | Своя презентация со слайдами (черновик: превью-мета; ready: распознанный текст) |
| PATCH | /api/v1/presentations/{id} | Переименовать, сменить порядок слайдов, править распознанный текст слайда |
| POST | /api/v1/presentations/{id}/slides | Добавить слайды: фото (multipart), страница своего ready PDF, или PPTX/DOCX |
| DELETE | /api/v1/presentations/{id}/slides/{slide_id} | Убрать один слайд |
| POST | /api/v1/presentations/{id}/index | Индексировать 1–40 слайдов (Idempotency-Key) |
| DELETE | /api/v1/presentations/{id} | Удалить презентацию, куски и векторы |
| GET | /api/v1/documents | Список материалов: PDF и презентации (`kind`). Без изменений пагинации |
| GET | /api/v1/progress | Прогресс владельца: статистика, темы (узлы), слабые, активность. `?material=` фильтр |

## Notes

- `Idempotency-Key` на `POST .../index` и на `POST .../slides` при office/фото-пакете: повтор ключа не дублирует слайды/прогон.
- Черновик (`draft`) не выбирается в чате и в создании викторины.
- Цитата чата/викторины для `kind=presentation` несёт `slide` (и `page`, если слайд из PDF-страницы).
- Прогресс: рёбер графа нет; weak = mastery &lt; 40%.
