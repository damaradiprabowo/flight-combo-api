from flask import Flask
from .routes.find_combinations import find_combinations_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(find_combinations_bp)

@app.route("/")
def index():
    return "God is dead."

if __name__ == '__main__':
    app.run(debug=False)
