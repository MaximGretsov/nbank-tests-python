import pytest

from src.main.api.utils.normalize_browsers import norm_browser_name
from src.main.ui.pages.login_page import LoginPage
from src.main.api.classes.session_storage import SessionStorage


@pytest.fixture(autouse=True, scope="function")
def user_session_extension(request: pytest.FixtureRequest):
    SessionStorage.clear()

    mark = request.node.get_closest_marker("user_session")
    if not mark:
        yield
        return

    count = max(int(mark.args[0]) if mark.args else 1, 1)
    auth_index = int(mark.kwargs.get("auth", 0))

    user_factory = request.getfixturevalue("user_factory")
    page = request.getfixturevalue("page")

    users = [user_factory() for _ in range(count)]
    SessionStorage.add_users(users)

    LoginPage(page).auth_as_user(users[auth_index])

    yield

    SessionStorage.clear()


@pytest.fixture(autouse=True)
def admin_session_autologin(request: pytest.FixtureRequest):
    mark = request.node.get_closest_marker("admin_session")
    if not mark:
        return

    page = request.getfixturevalue("page")
    admin_user_request = request.getfixturevalue("admin_user_request")

    LoginPage(page).auth_as_user(admin_user_request)


@pytest.fixture(autouse=True)
def browser_match_guard(request: pytest.FixtureRequest):
    mark = request.node.get_closest_marker("browsers")
    if not mark:
        return

    allowed = {norm_browser_name(str(x)) for x in (mark.args or ())}
    if not allowed:
        return

    try:
        current = request.getfixturevalue("browser_name")
    except Exception:
        return

    if norm_browser_name(str(current)) not in allowed:
        pytest.skip(
            f"Пропущен: текущий браузер '{current}' не в {sorted(allowed)}"
        )