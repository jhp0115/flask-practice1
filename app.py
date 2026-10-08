from flask import Flask, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)



@app.route("/") # default는 GET method.
def main():
    return f"<a href='{url_for('aboutPage')}'>{url_for('aboutPage')}</a>"

@app.route("/info")
def aboutPage():
    return "About"

# @app.route("/user/<name>")
# def userPage(name):
#     return f"{name}"

@app.route("/post/<int:no>")
def postPage(no):
    return f"{no}"

@app.route("/notes/")
def notesPage():
    return "Notes"

@app.route("/hello/")
@app.route("/hello/<name>")
def helloPage(name=None):
    return f"안녕하세요, {name}"


##

@app.route("/search", methods=["GET"])
def search():
    query = request.args.get('q', '')
    page = request.args.get('page', '1')
    if not query:
        return '검색어를 입력하세요'
    return f'{query} 검색 결과: {page} 페이지'

@app.route('/write', methods=['GET', 'POST'])
def write():
    if request.method == 'POST':
        banana = request.form['banana']
        melon = request.form['melon']
        return (f'banana = {banana} ({type(banana).__name__}) / '
        f'melon = {melon} ({type(melon).__name__})')
    return '''
    <form method="post">
        <input type="text" name="banana">
        <input type="number" name="melon">
        <button type="submit">보내기</button>
    </form>'''

# enctype 중요하다!
@app.route('/attach', methods=['GET', 'POST'])
def attach():
    if request.method == 'POST':
        f = request.files.get('cherry')
        if f is None:
            return 'cherry 가 files 에 없습니다'
        return f'{f.filename} / {len(f.read())} 바이트'
    return '''
    <form method="post" enctype="multipart/form-data">
        <input type="text" name="banana">
        <input type="file" name="cherry">
        <button type="submit">보내기</button>
    </form>'''


# 실습 3
@app.route('/user/<username>')
def user_profile(username):
    return render_template('profile.html',
    username=username,
    posts=[])


if __name__ == "__main__":
    app.run(debug=True)
