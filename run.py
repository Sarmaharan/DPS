"""Run the DPS web application."""
import os

# Ensure we run from project root
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render will provide PORT
    app.run(host='0.0.0.0', port=port, debug=False)