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

@app.route("/age/<num>")
def age_any(num):
    return f"<h1>{num} 살 타입은 {type(num).__name__}</h1>"

@app.route("/age2/<int:num>")
def age_any2(num):
    return f"<h1>{num} 살 타입은 {type(num).__name__}</h1>"

@app.route("/hi/<name1>")
def hi_template_render(name1):
    print("AA")
    return render_template("hi.html", name=name1)

# app.run은 맨 아래에 둬야 한다.

if __name__ == "__main__":
    app.run(debug=True)
