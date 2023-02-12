from flask import Blueprint, Flask
import pandas as pd
import matplotlib.pyplot as plt
from alpha_store.models import SalesRecord
from io import BytesIO
import base64

analytics = Blueprint("analytics", __name__, url_prefix="/apis/v1/analytics")


def configure(app: Flask) -> None:

    app.register_blueprint(analytics)
    app.logger.info("Analytics configured")


@analytics.route("/", methods=["GET"])
def index():
    return {
        "message": "Analytics api v1",
        "status_code": 200,
    },


@analytics.route("/report", methods=["GET"])
def report():

    # Get the data from the database

    data = SalesRecord.query.all()
    # Create a dataframe with the data
    df = pd.DataFrame([record.to_dict() for record in data])

    fig, axs = plt.subplots(3, 1, figsize=(10, 10))

    # Plot the data
    # sale by day
    df.groupby("sale_date")["product_price"].sum().plot(
        ax=axs[0], label="Sale by time", style="o-")

    axs[0].set_title("Sales history")
    axs[0].set_xlabel("Sale date")
    axs[0].set_ylabel("Sale value")

    # Sales by category
    df.groupby("product_category")["product_price"].sum().plot(
        kind="bar", ax=axs[1])

    axs[1].set_title("Sales revenue by category")

    # best selling games
    df.groupby("product_id").size().sort_values(
        ascending=False).head(10).plot(kind="bar", ax=axs[2])

    axs[2].set_title("best selling games")

    fig.tight_layout()
    fig.suptitle("Sales report", fontsize=16, y=1.05)

    image = BytesIO()
    plt.savefig(image, format="png")
    image.seek(0)
    image_base64 = base64.b64encode(image.read()).decode('utf-8')

    return f'<img src="data:image/png;base64,{image_base64}"/>'
