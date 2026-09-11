from jarvis.router import Router
from jarvis.tools import file_list, file_read, system_info, web_get


def test_safe_tools_have_explicit_capability_routes() -> None:
    router = Router()
    router.register("web", "web", web_get, capability="web")
    router.register("files", "files", file_list, capability="files")
    router.register("read", "read", file_read, capability="files")
    router.register("system", "system", system_info, capability="system")
    assert router.route_names() == ("files", "read", "system", "web")
