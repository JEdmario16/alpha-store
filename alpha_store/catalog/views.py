from flask import Blueprint, request, current_app, Flask, jsonify
from alpha_store.models import Products
from collections import OrderedDict
import pandas as pd

catalog = Blueprint("catalog", __name__, url_prefix="/apis/v1/catalog")


def configure(app: Flask) -> None:

    app.register_blueprint(catalog)
    app.logger.info("Catalog configured")


@catalog.route("/", methods=["GET"])
def index():
    return {
        "message": "Catalog api v1",
        "status_code": 200,
    }, 200


@catalog.route("/get_products_by_id/<int:product_id>", methods=["GET"])
def get_products_by_id(product_id):

    product = Products.query.filter_by(id=product_id).first()

    if product:
        return {
            "message": "Product found",
            "status_code": 200,
            "product": product.to_dict()
        }, 200

    return {
        "message": "Product not found",
        "status_code": 404,
        "product": {}
    }, 404


@catalog.route("/get_products_by_name/<string:product_name>", methods=["GET"])
def get_products_by_name(product_name):

    product = Products.query.filter_by(name=product_name).first()

    if product:
        return {
            "message": "Product found",
            "status_code": 200,
            "product": product.to_dict()
        }, 200

    return {
        "message": "Product not found",
        "status_code": 404,
        "product": {}
    }, 404


@catalog.route("/get_products", methods=["GET"])
def get_all_products():

    start = request.args.get("start", 0, type=int)
    limit = request.args.get("limit", 10, type=int)
    limit = limit if limit < 10 else 10  # Limit the max number of products to 10

    products = Products.query.order_by(
        Products.id).slice(start, start + limit).all()

    if not products:
        return {
            "message": "No products found",
            "status_code": 200,
            "products": []
        }, 200

    # To create the filters, Pandas is the easiest way but it can be expensive
    # Just using some manipulations with SQLAlchemy and python built-in's, we can get the same result
    # However, since Pandas is a ``Desirable requirement`` for this position, I'll use it

    # Get the filters from the query string
    sort_by = request.args.get("sort_by", 'name', type=str).lower()
    sort_type = request.args.get("sort_type", 'asc', type=str).lower()

    valid_sort_types = ("asc", "desc")
    valid_sort_fields = ("name", "price", "score")

    if (sort_by and sort_by not in valid_sort_fields):
        return {
            "message": f"Invalid sort_by field: {sort_by}",
            "status_code": 400,
        }, 400

    if (sort_type and sort_type not in valid_sort_types):
        return {
            "message": f"Invalid sort_type field: {sort_type}",
            "status_code": 400,
        }, 400

    # Convert the sort_type to boolean
    sort_type = sort_type == "asc"

    # Sort the products
    if sort_by:
        products = pd.DataFrame(product.to_dict() for product in products)
        products.sort_values(by=sort_by, inplace=True,
                             ascending=sort_type)

        products = products.to_dict(orient="records")

    return {
        "message": "Products found",
        "status_code": 200,
        "products": products
    }, 200


