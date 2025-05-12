from app import create_app
from app.routes import start_publish_thread

app = create_app()

with app.app_context():
    start_publish_thread(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True, threaded=True)