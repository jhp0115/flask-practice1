from flask import Flask, Blueprint, render_template, request, redirect, url_for 
from flask_sqlalchemy import SQLAlchemy 
from flask_restx import Api, Resource, fields

app = Flask(__name__)

# 전 : 4장에서 쓰던 줄
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db' 
# 후 : 오늘 바꾸는 줄. 왼쪽은 그대로이고 따옴표 안만 바뀐다
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://flask_user:password@localhost/flask_todo_db'

app.config["ERROR_404_HELP"] = False # 한글을 \uc6b0\uc720 처럼 바꾸지 않고 그대로 내보냅니다. 
app.config["RESTX_JSON"] = {"ensure_ascii": False}

db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    text = db.Column(db.String(100), nullable=False) 
    done = db.Column(db.Boolean, default=False) 
    def __repr__(self): 
        return f'<Todo {self.id} {self.text}>'

# ----------------------------------------------------------------- API 
# # Blueprint 로 한 번 감싸고 거기에 Api 를 붙입니다. 
# # 이렇게 해야 /api 아래에서만 JSON 이 나오고, 위의 화면 라우트는 그대로 남습니다. 
api_bp = Blueprint("api", __name__, url_prefix="/api") 
api = Api( api_bp, version="1.0", title="Todo API", description="4장에서 만든 todo 앱의 API", doc="/docs",                       
          # 문서는 /api/docs 에 열립니다
    ) 
ns = api.namespace("todos", description="할 일 하나하나를 다루는 곳")

# 주고받을 데이터의 모양입니다. 이것이 곧 문서가 됩니다.
todo_model = api.model(
    "Todo",
    {
        "id": fields.Integer(
            readonly=True,
            description="줄 번호. 서버가 붙입니다",
        ),
        "text": fields.String(
            required=True,
            description="할 일 글자",
            example="우유 사기",
        ),
        "done": fields.Boolean(
            description="완료 여부",
            example=False,
        ),
    },
)

# 만들 때와 바꿀 때 받을 것. id는 받지 않습니다.
todo_input = api.model(
    "TodoInput",
    {
        "text": fields.String(
            required=True,
            description="할 일 글자",
            example="우유 사기",
        ),
        "done": fields.Boolean(
            description="완료 여부",
            example=False,
        ),
    },
)


# (4)

@ns.route("/")
class TodoList(Resource):
    @ns.doc("목록 보기")
    @ns.marshal_list_with(todo_model)
    def get(self):
        """할 일을 전부 돌려준다"""
        return Todo.query.all()

    @ns.doc("새로 만들기")
    @ns.expect(todo_input, validate=True)
    @ns.marshal_with(todo_model, code=201)
    def post(self):
        """할 일을 하나 만든다"""
        todo = Todo(
            text=api.payload["text"],
            done=api.payload.get("done", False),
        )

        db.session.add(todo)
        db.session.commit()

        # 만들었으면 201과 함께 그것이 어디 있는지
        # Location에 적어 줍니다.
        return todo, 201, {
            "Location": f"/api/todos/{todo.id}",
        }


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST': 
        db.session.add(Todo(text=request.form['todo'])) 
        db.session.commit() 
        return redirect(url_for('index')) 
    todos = Todo.query.all() 
    return render_template('index.html', todos=todos)

@app.route('/toggle/<int:id>') 
def toggle(id): 
    todo = db.get_or_404(Todo, id) 
    todo.done = not todo.done 
    db.session.commit() 
    return redirect(url_for('index'))

@app.route('/delete/<int:id>') 
def delete(id): 
    todo = db.get_or_404(Todo, id) 
    db.session.delete(todo) 
    db.session.commit() 
    return redirect(url_for('index'))



#(5)

@ns.route("/<int:id>")
@ns.param("id", "할 일의 줄 번호")
@ns.response(404, "그 번호의 할 일이 없습니다")
class TodoItem(Resource):
    @ns.doc("하나 보기")
    @ns.marshal_with(todo_model)
    def get(self, id):
        """할 일 하나를 돌려준다"""
        return get_or_abort(id)

#(6)
    @ns.doc("통째로 바꾸기")
    @ns.expect(todo_input, validate=True)
    @ns.marshal_with(todo_model)
    def put(self, id):
        """할 일 하나를 통째로 바꾼다. 보내지 않은 칸은 기본값이 된다"""
        todo = get_or_abort(id)

        todo.text = api.payload["text"]
        todo.done = api.payload.get("done", False)

        db.session.commit()
        return todo

    @ns.doc("일부만 바꾸기")
    @ns.expect(todo_input)
    @ns.marshal_with(todo_model)
    def patch(self, id):
        """보낸 칸만 바꾼다. 완료 표시를 뒤집을 때 씁니다"""
        todo = get_or_abort(id)

        if "text" in api.payload:
            todo.text = api.payload["text"]

        if "done" in api.payload:
            todo.done = api.payload["done"]

        db.session.commit()
        return todo

#(7)
    @ns.doc("지우기")
    @ns.response(204, "지웠습니다. 돌려줄 내용이 없습니다")
    def delete(self, id):
        """할 일 하나를 지운다"""
        todo = get_or_abort(id)

        db.session.delete(todo)
        db.session.commit()

        return "", 204


def get_or_abort(id):
    """없는 번호면 404를 JSON으로 돌려준다."""
    todo = db.session.get(Todo, id)

    if todo is None:
        # abort에 넘긴 것이 그대로 JSON의 message가 됩니다.
        ns.abort(404, f"{id}번 할 일이 없습니다")

    return todo


app.register_blueprint(api_bp)




with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)