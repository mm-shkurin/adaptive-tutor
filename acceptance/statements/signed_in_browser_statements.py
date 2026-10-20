import json

from clients.application.session_client import ScriptedProvider, SessionClient

STORAGE_KEY = "adaptivetutor.session"


class SignedInBrowserStatements:
    def __init__(self, driver, app_url: str, base_url: str, provider: ScriptedProvider):
        self.driver = driver
        self.app_url = app_url
        self.sessions = SessionClient(base_url, provider)

    def given_a_signed_in_person_with_no_documents(self) -> None:
        opened = self.sessions.open_account("ada@example.test", "Ada")
        assert opened.status_code == 200
        assert opened.body["token_type"] == "bearer"
        session = {
            "accessToken": opened.body["access_token"],
            "refreshToken": opened.body["refresh_token"],
            "userId": "",
            "displayName": "",
            "avatarUrl": None,
        }
        self.driver.get(self.app_url)
        self.driver.execute_script(
            "window.localStorage.setItem(arguments[0], arguments[1]);",
            STORAGE_KEY,
            json.dumps(session),
        )
        self.driver.get(self.app_url)

    def close(self) -> None:
        self.sessions.close()
