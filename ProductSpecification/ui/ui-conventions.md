# UI conventions — AdaptiveTutor

The visual source is `adaptive-tutor-mockup.html`. Story mockups copy these tokens. They do not invent a second palette.

## Tokens

| Token | Value |
|-------|-------|
| Ink | `#0b1c1a` |
| Page | `#eef6f3` |
| Accent | `#1fa89a` |
| Surface | `#ffffff` |
| Border | `#d4e2dc` |
| Text | `#12201e` |
| Soft text | `#4d6560` |
| Radius | 12px, cards 16px |
| Font | Inter |
| Control height | 48px, at least 44px on a phone |

## Language

Interface text is Russian.

## Shell

- Guest sees the landing. The only door is «Войти через Яндекс».
- Signed-in chrome is the top tabs on a wide screen and a bottom bar on a phone: Чат, Викторины, Прогресс, Документы, Профиль.
- Theme choices are Системная, Светлая, Темная. The choice lives on the device.

## Documents

The screen is the Documents panel of `adaptive-tutor-mockup.html`: two doors, then «Ваши материалы».

- Doors: «Загрузить PDF» (до 50 MB) and «Создать презентацию». The presentation door is drawn here and built in story 3.
- A row shows the file name, a short line, and one pill: «Ждёт», «В процессе», «Готов», «Не удалось».
- «Не удалось» names the reason on the row. A refused upload names the reason under the PDF door and does not add a row.
- An empty list says «Пока нет материалов».

## Story mockups

Each screen state is its own HTML file, once at 1400px and once at 375px, under `stories/NN-story-name/mockups/desktop` and `mobile`.
