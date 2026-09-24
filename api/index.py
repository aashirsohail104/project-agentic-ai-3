import os

os.environ.setdefault("CHAINLIT_APP_ROOT", "/tmp")
os.environ.setdefault("CHAINLIT_HOST", "0.0.0.0")
os.environ.setdefault("CHAINLIT_PORT", "8000")

import src.ui.app as _app_module  # noqa: F401  (registers @cl.on_message handlers)

from chainlit.server import app as asgi_app  # noqa: E402

app = asgi_app