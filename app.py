import flask
from models import *                        
from sqlalchemy import select
from flask import request
from flask import jsonify

app = flask.Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://flask_user:12345@localhost:5432/flaskdb"
db.init_app(app)


@app.route("/")
def home():
    return "Welcome to the Home page!!!"


@app.route("/category")
def list_category():
   category_fetch_query= db.select(Category).order_by(Category.category_name)
   categories = db.session.execute(category_fetch_query).scalars()
   ret = []
   if not categories:
      return flask.jsonify({"message":"no categories found"})
   for category in categories:
      details = {"id" : category.id,
                 "category_name" : category.category_name
         }
      ret.append(details)
   return flask.jsonify(ret)


@app.route("/addcategory",methods=["POST"])
def add_category():
    data=request.json
    if not data:
       return flask.jsonify("data required"),400
    id=data.get('id')
    cname=data.get('category_name')
    new_category=Category(id=id,category_name=cname)
    db.session.add(new_category)
    db.session.commit()
    return flask.jsonify("created"),


@app.route("/product")
def list_product():
   product_select_query = db.select(Product).order_by(Product.product_name)
   products= db.session.execute(product_select_query).scalars()

   ret = []
   for product in products:
      category =db.session.query(Category).filter_by(id=product.category_id).first()
      image =db.session.query(Image).filter_by(p_id=product.product_id).first()
      details = {"id" : product.product_id,
         "product_name" : product.product_name,
         "product_price":product.price,
         "category":category.category_name if category != None else " ",
         "image":image.image if image != None else " "
         
         }
      ret.append(details)
   return flask.jsonify(ret)


@app.route("/add_product",methods=['POST'])
def add_product():
   data=request.get_json()
   if not data:
       return flask.jsonify("data required"),400
   
   product_id= data.get('product_id')
   product_name=data.get('product_name')
   price=data.get('price')
   category_name=data.get('category_name')
   image_url=data.get('image_url')
   category =db.session.query(Category).filter_by(category_name = category_name).first()
  
   if category == None:
      category=Category(category_name=category_name)
      db.session.add(category)
      db.session.commit()

   new_product = Product(product_id=product_id,product_name=product_name,price=price,category_id=category.id)
   db.session.add(new_product)
   db.session.commit()
   fetch_image =db.session.query(Image).filter_by(image=image_url).first()

   if fetch_image == None :
      add_image=Image(image=image_url,p_id=product_id)
      db.session.add(add_image)
      db.session.commit()
   return jsonify({'message':"product was added successfully"}),201


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

