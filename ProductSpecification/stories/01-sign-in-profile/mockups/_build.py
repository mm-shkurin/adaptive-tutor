"""Static snapshots of story 1. Source of color and copy: adaptive-tutor-mockup.html."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent

CSS = """
:root {
  --ink: #0b1c1a; --foam: #f3f7f5; --page: #eef6f3; --accent: #1fa89a;
  --mist: #6b857e; --surface: #fff; --border: #d4e2dc; --text: #12201e;
  --text-soft: #4d6560; --radius: 12px; --danger: #b42318;
  --font: Inter, "Segoe UI", sans-serif;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: var(--font); color: var(--text); background: var(--page); line-height: 1.5; }
button, input { font: inherit; }
.btn { display: inline-flex; align-items: center; justify-content: center; height: 48px; padding: 0 22px; border-radius: var(--radius); border: 1px solid transparent; font-weight: 600; }
.btn-primary { background: var(--accent); color: #04221e; }
.btn-ghost { background: transparent; color: inherit; border-color: rgba(243,247,245,.35); }
.btn-outline { background: var(--surface); border-color: var(--border); color: var(--text); }
.btn-dark { background: var(--ink); color: #fcfcfc; }
.btn-danger { background: var(--danger); color: #fff; }
.btn:disabled { opacity: .45; }
.top {
  color: var(--foam);
  background: linear-gradient(160deg, #071412 0%, #0f2a26 45%, #14352f 100%);
  padding: 28px 40px 72px;
}
.nav { display: flex; align-items: center; gap: 28px; }
.brand { font-weight: 800; font-size: 20px; color: inherit; text-decoration: none; }
.links { display: flex; gap: 18px; margin-left: auto; }
.links a { color: var(--foam); text-decoration: none; }
.nav-actions { display: flex; gap: 10px; }
.hero { display: grid; grid-template-columns: 1.1fr .9fr; gap: 40px; align-items: center; max-width: 1120px; margin: 48px auto 0; }
h1 { font-size: 64px; letter-spacing: -1px; }
.line { font-size: 22px; margin-top: 12px; }
.sub { color: #c5ddd6; margin-top: 8px; }
.cta { display: flex; gap: 12px; margin-top: 28px; }
.sheet { background: var(--surface); color: var(--text); border-radius: 16px; padding: 16px; margin-bottom: 12px; }
.sheet b { display: block; }
.chip { display: inline-block; background: #e4f4f0; color: var(--ink); border-radius: 999px; padding: 8px 14px; font-size: 14px; }
.section { max-width: 1120px; margin: 0 auto; padding: 56px 40px; }
.eyebrow { color: var(--accent); font-weight: 700; letter-spacing: .08em; text-transform: uppercase; font-size: 13px; }
.grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-top: 24px; }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 18px; }
.card h3 { margin-bottom: 6px; }
.card p, .lead { color: var(--text-soft); }
.appbar { display: flex; align-items: center; gap: 16px; background: var(--surface); border-bottom: 1px solid var(--border); padding: 14px 28px; }
.tabs { display: flex; gap: 8px; }
.tab { height: 40px; padding: 0 14px; border-radius: 999px; border: 0; background: transparent; color: var(--text-soft); }
.tab.on { background: var(--ink); color: var(--foam); }
.who { margin-left: auto; font-weight: 600; }
.main { max-width: 760px; margin: 0 auto; padding: 32px 24px 80px; }
h2 { font-size: 32px; }
.stack { display: flex; flex-direction: column; gap: 16px; margin-top: 20px; }
.panel { background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 20px; }
.row { display: flex; gap: 16px; align-items: center; }
.avatar { width: 72px; height: 72px; border-radius: 50%; background: var(--ink); color: var(--foam); display: flex; align-items: center; justify-content: center; font-weight: 700; }
.avatar.photo { background: #1fa89a; }
.meta { color: var(--text-soft); font-size: 14px; }
.name-row { display: flex; gap: 8px; margin-top: 16px; }
input[type="text"], input[type="email"] { height: 48px; border: 1px solid var(--border); border-radius: 12px; padding: 0 12px; width: 100%; background: var(--surface); }
.counter { color: var(--mist); font-size: 13px; align-self: center; }
.theme { display: flex; gap: 8px; }
.theme button { height: 44px; padding: 0 14px; border-radius: 999px; border: 1px solid var(--border); background: var(--surface); }
.theme button.on { background: var(--ink); color: var(--foam); border-color: var(--ink); }
.split { display: flex; justify-content: space-between; align-items: center; gap: 16px; padding: 12px 0; }
.center { min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 24px; }
.gate { width: 420px; background: var(--surface); border-radius: 18px; padding: 28px; border: 1px solid var(--border); }
.gate h2 { font-size: 26px; margin-bottom: 8px; }
.spinner { width: 36px; height: 36px; border: 3px solid var(--border); border-top-color: var(--accent); border-radius: 50%; margin-bottom: 16px; }
.backdrop { position: fixed; inset: 0; background: rgba(11,28,26,.45); display: flex; align-items: center; justify-content: center; padding: 16px; }
.modal { width: 440px; background: var(--surface); border-radius: 18px; padding: 24px; }
.modal p, .modal label { color: var(--text-soft); display: block; margin: 8px 0 12px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 16px; }
.bottom { display: none; }
body.mobile { width: 375px; overflow-x: hidden; }
body.mobile .top { padding: 16px 16px 36px; }
body.mobile .links, body.mobile .hero-visual, body.mobile .tabs { display: none; }
body.mobile .nav { justify-content: space-between; }
body.mobile .hero { grid-template-columns: 1fr; margin-top: 28px; }
body.mobile h1 { font-size: 40px; }
body.mobile .section { padding: 32px 16px; }
body.mobile .grid { grid-template-columns: 1fr; }
body.mobile .appbar { padding: 12px 16px; }
body.mobile .who { display: none; }
body.mobile .main { padding: 20px 16px 88px; }
body.mobile .bottom { display: flex; position: fixed; left: 0; bottom: 0; width: 375px; background: var(--surface); border-top: 1px solid var(--border); }
body.mobile .bottom button { flex: 1 1 0; min-width: 0; height: 56px; border: 0; background: transparent; color: var(--text-soft); font-size: 10px; padding: 0 2px; }
body.mobile .bottom button.on { color: var(--ink); font-weight: 700; }
body.mobile .split { align-items: flex-start; flex-direction: column; }
body.mobile .modal, body.mobile .gate { width: 100%; }
"""

STATES = [
    "01-landing",
    "02-yandex-waiting",
    "03-yandex-failed",
    "04-signed-in",
    "05-profile-edit-name",
    "06-profile-saving",
    "07-profile-no-photo",
    "08-delete-mismatch",
    "09-delete-match",
    "10-account-deleted",
]


def landing() -> str:
    return """
    <header class="top">
      <div class="nav">
        <a class="brand" href="#">AdaptiveTutor</a>
        <nav class="links"><a href="#features">Возможности</a><a href="#modes">Режимы</a><a href="#process">Как работает</a><a href="#audience">Для кого</a></nav>
        <div class="nav-actions"><button class="btn btn-ghost">Войти</button><button class="btn btn-primary">Начать обучение</button></div>
      </div>
      <section class="hero">
        <div>
          <h1>AdaptiveTutor</h1>
          <p class="line">Учитесь по своим лекциям — с цитатами, а не догадками.</p>
          <p class="sub">AI-тьютор читает PDF, отвечает с опорой на материал и подтягивает слабые темы.</p>
          <div class="cta"><button class="btn btn-primary">Войти через Яндекс</button><button class="btn btn-ghost">Как это работает</button></div>
        </div>
        <div class="hero-visual">
          <div class="sheet"><span class="meta">Лекция · PDF</span><b>Линейная алгебра</b></div>
          <div class="sheet"><span class="meta">Ответ тьютора</span><b>Собственное число λ</b></div>
          <div class="chip">Источник: <b>слайд 12, стр. 5</b></div>
        </div>
      </section>
    </header>
    <section class="section" id="features">
      <div class="eyebrow">Возможности</div>
      <h2>Что хотите сделать?</h2>
      <p class="lead">Чат, викторины, документы и прогресс — в одном контуре обучения</p>
      <div class="grid">
        <article class="card"><h3>AI-тьютор</h3><p>Диалог по вашим материалам с цитатами на слайды и страницы</p></article>
        <article class="card"><h3>Викторины</h3><p>Вопросы по теме из загруженного материала</p></article>
        <article class="card"><h3>Документы</h3><p>Лекции и слайды, по которым тьютор отвечает</p></article>
        <article class="card"><h3>Прогресс</h3><p>Слабые темы видно до экзамена</p></article>
      </div>
    </section>
    """


def gate(title: str, text: str, actions: str) -> str:
    return f'<main class="center"><section class="gate"><h2>{title}</h2><p class="lead">{text}</p><div class="cta">{actions}</div></section></main>'


def shell(inner: str, modal: str = "") -> str:
    return f"""
    <header class="appbar">
      <a class="brand" href="#" style="color:var(--ink)">AdaptiveTutor</a>
      <nav class="tabs"><button class="tab">Чат</button><button class="tab">Викторины</button><button class="tab">Прогресс</button><button class="tab">Документы</button><button class="tab on">Профиль</button></nav>
      <div class="who">Максим</div>
    </header>
    <main class="main">{inner}</main>
    <nav class="bottom"><button>Чат</button><button>Викторины</button><button>Прогресс</button><button>Документы</button><button class="on">Профиль</button></nav>
    {modal}
    """


def identity(photo: bool, editing: bool, saving: bool) -> str:
    avatar = '<div class="avatar photo">МС</div>' if photo else '<div class="avatar">МС</div>'
    if editing:
        name = """
        <div class="name-row">
          <input type="text" value="Максим Шкурин" aria-label="Имя">
          <span class="counter">14 / 60</span>
          <button class="btn btn-dark">Сохранить</button>
          <button class="btn btn-outline">Отмена</button>
        </div>"""
    elif saving:
        name = '<div class="name-row"><button class="btn btn-dark" disabled>Сохраняем…</button></div>'
    else:
        name = '<div class="cta"><button class="btn btn-outline">Изменить имя</button></div>'
    photo_btns = '<button class="btn btn-outline">Изменить</button>'
    if photo:
        photo_btns += '<button class="btn btn-ghost">Удалить фото</button>'
    return f"""
    <h2>Мой профиль</h2>
    <p class="lead">Личные данные, внешний вид и аккаунт</p>
    <div class="stack">
      <section class="panel">
        <h3>Личные данные</h3>
        <p class="meta">Имя и фотографию можно поменять. Пароля здесь нет — вход через Яндекс ID.</p>
        <div class="row" style="margin-top:16px">{avatar}<div><b>Максим Шкурин</b><div class="meta">maxim@example.com</div><div class="meta">На AdaptiveTutor с 14 октября 2026</div><div class="meta">Роль: Студент · ОмГТУ</div></div></div>
        <div class="cta">{photo_btns}</div>
        {name}
      </section>
      <section class="panel">
        <h3>Внешний вид</h3>
        <p class="meta">Оформление на этом устройстве</p>
        <div class="theme" style="margin-top:12px"><button>Системная</button><button class="on">Светлая</button><button>Темная</button></div>
      </section>
      <section class="panel">
        <div class="split"><div><b>Выйти из аккаунта</b><div class="meta">Сессия закроется и на других устройствах</div></div><button class="btn btn-outline">Выйти</button></div>
        <div class="split"><div><b>Удаление аккаунта</b><div class="meta">Документы, чаты, викторины и прогресс будут удалены безвозвратно</div></div><button class="btn btn-danger">Удалить аккаунт</button></div>
      </section>
    </div>
    """


def delete_modal(match: bool) -> str:
    value = "maxim@example.com" if match else ""
    disabled = "" if match else " disabled"
    return f"""
    <div class="backdrop"><section class="modal" role="dialog">
      <h2>Удалить аккаунт?</h2>
      <p>Действие необратимо. Восстановить данные после подтверждения нельзя.</p>
      <label>Введите адрес аккаунта — maxim@example.com — чтобы подтвердить удаление.</label>
      <input type="email" value="{value}" aria-label="Почта для подтверждения">
      <div class="modal-actions"><button class="btn btn-outline">Отмена</button><button class="btn btn-danger"{disabled}>Удалить аккаунт</button></div>
    </section></div>
    """


def body_for(name: str) -> str:
    if name == "01-landing":
        return landing()
    if name == "02-yandex-waiting":
        return gate("Входим через Яндекс", "Ждём подтверждение. Сессия появится только после ответа.", '<div class="spinner" aria-hidden="true"></div>')
    if name == "03-yandex-failed":
        return gate("Не удалось войти", "Яндекс не подтвердил вход. Сессия не создана.", '<button class="btn btn-primary">Вернуться на главную</button>')
    if name == "04-signed-in":
        return shell(identity(True, False, False))
    if name == "05-profile-edit-name":
        return shell(identity(True, True, False))
    if name == "06-profile-saving":
        return shell(identity(True, False, True))
    if name == "07-profile-no-photo":
        return shell(identity(False, False, False))
    if name == "08-delete-mismatch":
        return shell(identity(True, False, False), delete_modal(False))
    if name == "09-delete-match":
        return shell(identity(True, False, False), delete_modal(True))
    return gate("Аккаунт удалён", "Этот аккаунт стёрт. Вход через Яндекс создаст новый.", '<button class="btn btn-primary">На главную</button>')


def page(name: str, mobile: bool) -> str:
    width = "375" if mobile else "1400"
    klass = "mobile" if mobile else "desktop"
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width={width}">
  <title>AdaptiveTutor — {name}</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
  <style>{CSS}</style>
</head>
<body class="{klass}">
{body_for(name)}
</body>
</html>
"""


def main() -> None:
    for folder in ("desktop", "mobile"):
        target = ROOT / folder
        target.mkdir(parents=True, exist_ok=True)
        mobile = folder == "mobile"
        for name in STATES:
            (target / f"{name}.html").write_text(page(name, mobile), encoding="utf-8")
    print(len(STATES) * 2)


if __name__ == "__main__":
    main()
