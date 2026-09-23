from flask import Flask, render_template

app = Flask(__name__)



@app.route("/") # default는 GET method.
def hello_world():
    return render_template("main.html", name="박지호", number="21010856")


@app.route("/profile")
def about_page():
    return render_template("hobbies.html", hobbies=["운동", "독서", "게임"])

@app.route("/greet/<name>")
def route_sample(name):
    return render_template("greet.html", name=name)


if __name__ == "__main__":
    app.run(debug=True)
