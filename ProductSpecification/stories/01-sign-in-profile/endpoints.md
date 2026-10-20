# Вход и профиль — API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/auth/oauth/yandex/start | Начать вход: редирект на Яндекс |
| GET | /api/v1/auth/oauth/yandex/callback | Возврат от Яндекса: редирект с одноразовым кодом или ошибкой |
| POST | /api/v1/auth/oauth/exchange | Обменять код на сессию |
| POST | /api/v1/auth/refresh | Обновить access-токен |
| POST | /api/v1/auth/logout | Отозвать access- и refresh-токен |
| GET | /api/v1/user/profile | Свой профиль |
| PATCH | /api/v1/user/profile | Своё имя |
| PUT | /api/v1/user/avatar | Загрузить фото |
| DELETE | /api/v1/user/avatar | Убрать фото |
| DELETE | /api/v1/user | Удалить свой аккаунт |

## Notes

- Тема на устройство не уходит: системная, светлая и тёмная живут в браузере.
- «Студент · ОмГТУ» — текст экрана, не поле ответа.
- Удаление на сервере не просит почту. Экран не шлёт `DELETE`, пока введённая почта не равна `email` профиля.
- `start` ставит куку `signin_browser`. Обмен кода принимает её только из того же браузера. На локальном стенде фронт и API должны быть одним сайтом, иначе браузер не приложит куку к обмену.
