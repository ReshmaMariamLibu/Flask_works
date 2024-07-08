import flask
from models import *
from sqlalchemy import select
from flask import request
from flask import jsonify
from flask_cors import CORS

app = flask.Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://flask_user:12345@localhost:5432/flaskdb"
)
db.init_app(app)


@app.route("/")
def home():
    return "Welcome to the Home page!!!"


@app.route("/category")
def list_category():
    category_fetch_query = db.select(Category).order_by(Category.created_at.desc())
    categories = db.session.execute(category_fetch_query).scalars()
    ret = []
    if not categories:
        return flask.jsonify({"message": "no categories found"})
    for category in categories:
        details = {"id": category.id, "category_name": category.category_name}
        ret.append(details)
    return flask.jsonify(ret)


@app.route("/addcategory", methods=["POST"])
def add_category():
    data = request.json
    if not data:
        return flask.jsonify("data required"), 400
    cname = data.get("category_name")
    category = db.session.query(Category).filter_by(category_name=cname).first()
    if category:
        return (flask.jsonify({"message":"category exist"}),400)
    new_category = Category(category_name=cname)
    db.session.add(new_category)
    db.session.commit()
    details={"id": new_category.id, "category_name": new_category.category_name}
    return (flask.jsonify(details),200)


@app.route("/product")
def list_product():
    product_select_query = db.select(Product).order_by(Product.created_at.desc())
    products = db.session.execute(product_select_query).scalars()

    ret = []
    for product in products:
        category = db.session.query(Category).filter_by(id=product.category_id).first()
        image = db.session.query(Image).filter_by(p_id=product.product_id).first()
        details = {
            "id": product.product_id,
            "product_name": product.product_name,
            "product_price": product.price,
            "category": category.category_name if category != None else " ",
            "image": image.image if image != None else " ",
        }
        ret.append(details)
    return flask.jsonify(ret)


@app.route("/product/<int:id>", methods=["GET"])
def get_product(id):
    try:
        product = db.session.query(Product).filter_by(product_id=id).first()
        if not product:
            return jsonify({"message": "Product not found"}), 404

        category = db.session.query(Category).filter_by(id=product.category_id).first()
        image = db.session.query(Image).filter_by(p_id=product.product_id).first()

        product_details = {
            "id": product.product_id,
            "product_name": product.product_name,
            "product_price": product.price,
            "category": category.category_name if category else " ",
            "image": image.image if image else " ",
        }

        return jsonify(product_details), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route("/add_product", methods=["POST"])
def add_product():
    data = request.get_json()
    if not data:
        return jsonify({"message": "data required"}), 400

    product_name = data.get("product_name")
    price = data.get("price")
    category_name = data.get("category_name")
    image_url = data.get("image_url")

    if not all([product_name, price, category_name, image_url]):
        return (
            jsonify(
                {
                    "message": "All fields (product_name, price, category_name, image_url) are required"
                }
            ),
            400,
        )
    product = db.session.query(Product).filter_by(product_name=product_name).first()
    if product:
        return jsonify({"message": "product already exist"}), 400

    try:
        category = (
            db.session.query(Category).filter_by(category_name=category_name).first()
        )
        if category is None:
            category = Category(category_name=category_name)
            db.session.add(category)
            db.session.commit()

        fetch_image = db.session.query(Image).filter_by(image=image_url).first()

        if fetch_image :
          return jsonify({"message": "image already exist"}), 400
        
        new_product = Product(
            product_name=product_name, price=price, category_id=category.id
        )
        db.session.add(new_product)
        db.session.commit()
   
        add_image = Image(image=image_url, p_id=new_product.product_id)
        db.session.add(add_image)
        db.session.commit()

        details = {
            "id": new_product.product_id,
            "product_name": new_product.product_name,
            "product_price": new_product.price,
            "category": category.category_name if category != None else " ",
            "image": add_image.image if add_image != None else " ",
        }

        return jsonify(details), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# @app.route("/image")
# def list_image():
#     image_fetch_query = db.select(Image).order_by(Image.id)
#     images = db.session.execute(image_fetch_query).scalars()
#     ret = []
#     if not images:
#         return jsonify({"message": "no images found"})
#     for image in images:
#         product = db.session.query(Product).filter_by(product_id=image.p_id).first()
#         details = {
#             "id": image.id,
#             "image": image.image,
#             "product_id": image.p_id,
#             "product_name": product.product_name if product else ""
#         }
#         ret.append(details)
#     return jsonify(ret)

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    init_db()
    app.run(port=5000)