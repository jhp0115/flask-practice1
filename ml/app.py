from flask import Flask
from flask_restx import Api, Resource, fields
import joblib
import pandas as pd

app = Flask(__name__)
app.config["RESTX_JSON"] = {"ensure_ascii": False}

api = Api(
    app,
    version="1.0",
    title="Iris API",
    description="Iris 측정값 넷을 받아 품종을 돌려준다",
    doc="/api/docs",
    prefix="/api",
)

ns = api.namespace("iris", description="Iris 품종 예측")


@app.route("/")
def page():
    return app.send_static_file("index.html")  # static/index.html을 그대로 반환


# 서버를 켤 때 한 번만 읽는다. 요청마다 다시 읽지 않는다.
model = joblib.load("iris_model.pkl")

COLUMNS = [
    "sepal length (cm)",
    "sepal width (cm)",
    "petal length (cm)",
    "petal width (cm)",
]

NAMES = ["setosa", "versicolor", "virginica"]




###

flower = api.model(
    "Flower",
    {
        "sepal_length": fields.Float(
            required=True, example=6.0, description="꽃받침 길이 (cm)"
        ),
        "sepal_width": fields.Float(
            required=True, example=2.9, description="꽃받침 너비 (cm)"
        ),
        "petal_length": fields.Float(
            required=True, example=4.5, description="꽃잎 길이 (cm)"
        ),
        "petal_width": fields.Float(
            required=True, example=1.5, description="꽃잎 너비 (cm)"
        ),
    },
)


@ns.route("/predict")
class Predict(Resource):
    @ns.doc("품종 예측")
    @ns.expect(flower, validate=True)
    def post(self):
        """측정값 넷을 받아 품종과 확률을 돌려준다."""
        d = api.payload

        x = pd.DataFrame(
            [[
                d["sepal_length"],
                d["sepal_width"],
                d["petal_length"],
                d["petal_width"],
            ]],
            columns=COLUMNS,
        )

        proba = model.predict_proba(x)[0]
        i = int(proba.argmax())

        return {
            "species": NAMES[i],
            "probability": round(float(proba[i]), 2),
        }