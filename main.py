import os
from pathlib import Path

# Carrega .env antes de importar o app/app_config
try:
    from dotenv import load_dotenv, find_dotenv

    dotenv_path = find_dotenv(usecwd=True)
    if dotenv_path:
        load_dotenv(dotenv_path=dotenv_path, override=False)
    else:
        local_env = Path(__file__).with_name(".env")
        if local_env.exists():
            load_dotenv(dotenv_path=str(local_env), override=False)
except Exception:
    pass

from app import create_app

app = create_app()

if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    try:
        port = int(os.getenv("FLASK_PORT", "5000"))
    except ValueError:
        port = 5000
    debug = (os.getenv("FLASK_DEBUG", "") or "").lower() in {"1", "true", "yes"}

    app.run(host=host, port=port, debug=debug)
