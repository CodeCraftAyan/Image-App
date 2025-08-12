import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

# Config
app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 'sqlite:///gallery.db'
).replace("postgres://", "postgresql://")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model
class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    filename = db.Column(db.String(150), nullable=False)

# Ensure DB and upload folder exist — runs for both local & Render
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
with app.app_context():
    db.create_all()

# Helpers
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
@app.route("/")
def index():
    photos = Photo.query.all()
    return render_template("index.html", photos=photos)

@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        title = request.form.get("title")
        file = request.files.get("file")

        if title and file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            new_photo = Photo(title=title, filename=filename)
            db.session.add(new_photo)
            db.session.commit()

        return redirect(url_for("index"))
    return render_template("create.html")

@app.route("/<string:i_title>/<int:i_id>")
def i_view(i_title, i_id):
    photo = Photo.query.get_or_404(i_id)
    if photo.title.replace(" ", "-").lower() != i_title.lower():
        return redirect(url_for("i_view", i_title=photo.title.replace(" ", "-"), i_id=photo.id))
    return render_template("view.html", photo=photo)

if __name__ == "__main__":
    app.run(debug=True)
