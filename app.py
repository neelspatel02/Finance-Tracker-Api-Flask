from database import DataBase
from flask import Flask, jsonify, request
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from services import category_service, transaction_service, analysis_service
from werkzeug.security import generate_password_hash, check_password_hash



DB_PATH = "pft.db"

app = Flask(__name__)
app.secret_key = "aryhnarwra4y5aeryna5eryq5eryq5aenr"

login_manager = LoginManager()
login_manager.init_app(app)


# ---- DATABASE ----
db = DataBase(DB_PATH)
db.connect()
db.create_tables()


# ---- TRANSACTIONS ----

@app.route("/api/transactions", methods=["GET"])
@login_required
def get_transactions():
    return jsonify(transaction_service.get_all(db, current_user.id)), 200


@app.route("/api/transactions", methods=["POST"])
@login_required
def add_transactions():
    data = request.get_json()
    result = transaction_service.add(db,data, current_user.id)
    return jsonify(result), 201


@app.route("/api/transactions/<id>", methods=["DELETE"])
@login_required
def delete_transactions(id):
    result = transaction_service.delete(db, id)
    return jsonify(result), 200


# ---- CATEGORIES ----

@app.route("/api/categories", methods=["GET"])
@login_required
def get_categories():
    return jsonify(category_service.get_all()), 200


@app.route("/api/categories",methods=["POST"])
@login_required
def add_categories():
    data = request.get_json()
    return category_service.add(data)


@app.route("/api/categories/<id>", methods=["DELETE"])
@login_required
def delete_categories(id):
    return category_service.delete(id)


# ---- ANALYSIS -----

@app.route("/api/analysis")
@login_required
def get_analysis():
    return jsonify(analysis_service.get_total(db, current_user.id)), 200


@app.route("/api/analysis/monthly", methods=["GET"])
@login_required
def get_monthly():
    return jsonify(analysis_service.get_monthly(db, current_user.id)), 200


@app.route("/api/analysis/categories", methods=["GET"])
@login_required
def get_category_report():
    return jsonify(analysis_service.get_by_categories(db, current_user.id)), 200

#  ---- USER LOGIN -----

class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id 
        self.username = username


@login_manager.user_loader
def load_user(user_id):
    data = db.get_user_by_id(user_id)
    if data:
        return User(data["user_id"], data["username"])
    return None

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({"message": "Unauthorized"}), 401


#  REFISTER

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data["username"]
    email = data["email"]
    password_hash = generate_password_hash(data["password"])

    result = db.add_user(username, email, password_hash)

    if result:
        return jsonify({"message": "User created"}), 201
    else:
        return jsonify({"message": "User or email already exist"}), 400
    

# LOGIN

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    row = db.get_user_by_username(data["username"])

    if row and check_password_hash(row["password_hash"], data["password"]):
        user = User(row["user_id"], row["username"])
        login_user(user)
        return jsonify({"message": "Login Successful"}), 200
    
    return jsonify({"message": "Invalid credentials"}), 401


@app.route("/api/auth/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out"}), 200

app.run(debug=True)