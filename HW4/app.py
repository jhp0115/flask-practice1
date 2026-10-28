import os

from flask import Blueprint, Flask, redirect, render_template, request, url_for
from flask_restx import Api, Resource, fields
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100), nullable=False)
    done = db.Column(db.Boolean, nullable=False, default=False)
    note = db.Column(db.String(500), nullable=False, default="")

    def __repr__(self):
        return f"<Todo {self.id} {self.text}>"


api_bp = Blueprint("api", __name__, url_prefix="/api")
api = Api(
    api_bp,
    version="1.0",
    title="Todo API",
    description="Todo 목록과 설명을 관리하는 API",
    doc="/docs",
)
ns = api.namespace("todos", description="할 일 관리")

todo_model = api.model(
    "Todo",
    {
        "id": fields.Integer(readonly=True, description="서버가 부여한 번호"),
        "text": fields.String(required=True, description="할 일", example="우유 사기"),
        "done": fields.Boolean(description="완료 여부", example=False),
        "note": fields.String(description="설명", example="2리터짜리로"),
    },
)
todo_input = api.model(
    "TodoInput",
    {
        "text": fields.String(required=True, description="할 일", example="우유 사기"),
        "done": fields.Boolean(description="완료 여부", example=False),
        "note": fields.String(description="설명", example="2리터짜리로"),
    },
)
todo_patch = api.model(
    "TodoPatch",
    {
        "text": fields.String(description="바꿀 할 일"),
        "done": fields.Boolean(description="바꿀 완료 여부"),
        "note": fields.String(description="바꿀 설명"),
    },
)


def get_or_abort(todo_id):
    todo = db.session.get(Todo, todo_id)
    if todo is None:
        ns.abort(404, f"{todo_id}번 할 일이 없습니다")
    return todo


@ns.route("/")
class TodoList(Resource):
    @ns.doc("목록 보기")
    @ns.param("done", "true면 완료한 것만, false면 아직 안 한 것만")
    @ns.marshal_list_with(todo_model)
    def get(self):
        """전체 목록을 보거나 완료 여부로 골라 본다."""
        query = Todo.query
        done = request.args.get("done")
        if done is not None:
            query = query.filter_by(done=(done.lower() == "true"))
        return query.order_by(Todo.id).all()

    @ns.doc("새로 만들기")
    @ns.expect(todo_input, validate=True)
    @ns.marshal_with(todo_model, code=201)
    def post(self):
        """할 일을 하나 만든다."""
        todo = Todo(
            text=api.payload["text"],
            done=api.payload.get("done", False),
            note=api.payload.get("note", ""),
        )
        db.session.add(todo)
        db.session.commit()
        return todo, 201, {"Location": f"/api/todos/{todo.id}"}


@ns.route("/<int:id>")
@ns.param("id", "할 일의 번호")
@ns.response(404, "그 번호의 할 일이 없습니다")
class TodoItem(Resource):
    @ns.doc("하나 보기")
    @ns.marshal_with(todo_model)
    def get(self, id):
        """할 일 하나를 돌려준다."""
        return get_or_abort(id)

    @ns.doc("통째로 바꾸기")
    @ns.expect(todo_input, validate=True)
    @ns.marshal_with(todo_model)
    def put(self, id):
        """전체를 바꾼다. 생략한 완료 여부와 설명은 기본값이 된다."""
        todo = get_or_abort(id)
        todo.text = api.payload["text"]
        todo.done = api.payload.get("done", False)
        todo.note = api.payload.get("note", "")
        db.session.commit()
        return todo

    @ns.doc("일부만 바꾸기")
    @ns.expect(todo_patch, validate=True)
    @ns.marshal_with(todo_model)
    def patch(self, id):
        """보낸 칸만 바꾼다."""
        todo = get_or_abort(id)
        for field in ("text", "done", "note"):
            if field in api.payload:
                setattr(todo, field, api.payload[field])
        db.session.commit()
        return todo

    @ns.doc("지우기")
    @ns.response(204, "지웠습니다")
    def delete(self, id):
        """할 일 하나를 지운다."""
        todo = get_or_abort(id)
        db.session.delete(todo)
        db.session.commit()
        return "", 204


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", "sqlite:///todo.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        ERROR_404_HELP=False,
        RESTX_JSON={"ensure_ascii": False},
    )
    if config:
        app.config.update(config)
    db.init_app(app)

    @app.route("/", methods=["GET", "POST"])
    def index():
        if request.method == "POST":
            db.session.add(
                Todo(text=request.form["todo"], note=request.form.get("note", ""))
            )
            db.session.commit()
            return redirect(url_for("index"))
        return render_template("index.html", todos=Todo.query.order_by(Todo.id).all())

    @app.route("/toggle/<int:id>")
    def toggle(id):
        todo = db.get_or_404(Todo, id)
        todo.done = not todo.done
        db.session.commit()
        return redirect(url_for("index"))

    @app.route("/delete/<int:id>")
    def delete(id):
        todo = db.get_or_404(Todo, id)
        db.session.delete(todo)
        db.session.commit()
        return redirect(url_for("index"))

    app.register_blueprint(api_bp)
    with app.app_context():
        db.create_all()
    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
