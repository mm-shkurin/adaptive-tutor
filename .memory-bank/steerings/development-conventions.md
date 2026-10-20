# How work is resumed

- Состояние шага: `progress.md` истории. Маркеры `[x]` `[~]` `[ ]` `[S]`.
- Почему так решили: только `/handoff`, в summary истории. Рутину туда не писать.
- Энциклопедия проекта: этот каталог `.memory-bank/`.
- Новая сессия читает банк и `stories.md` до вопросов. Хук `.cursor/hooks/context_hook.py` подмешивает их в старт сессии.
- Коммиты на рабочую ветку, без pull request. См. `.claude/rules/workflow.md`.
