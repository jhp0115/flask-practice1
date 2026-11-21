from pathlib import Path

import joblib
import pandas as pd
from flask import Flask
from flask_restx import Api, Resource, fields


app = Flask(__name__)
app.config["RESTX_JSON"] = {"ensure_ascii": False}
api = Api(
    app,
    version="1.0",
    title="Sales API",
    description="수량과 단가로 총액을 예측합니다.",
    doc="/api/docs",
    prefix="/api",
)
ns = api.namespace("sales", description="총액 예측")
model = joblib.load(Path(__file__).with_name("sales_model.pkl"))

order = api.model(
    "Order",
    {
        "quantity": fields.Integer(required=True, example=40, description="수량"),
        "unit_price": fields.Float(required=True, example=200000, description="단가(원)"),
    },
)


@ns.route("/predict")
class Predict(Resource):
    @ns.expect(order, validate=True)
    def post(self):
        """수량과 단가를 받아 총액을 돌려줍니다."""
        data = api.payload
        x = pd.DataFrame(
            [[data["quantity"], data["unit_price"]]],
            columns=["quantity", "unit_price"],
        )
        x["qp"] = x["quantity"] * x["unit_price"]
        return {"total_sales": int(round(model.predict(x)[0]))}
