import unittest

from app import create_app, db


class TodoApiTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        })
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def make_todo(self, **data):
        return self.client.post("/api/todos/", json={"text": "우유 사기", **data})

    def test_create_returns_201_note_and_location(self):
        response = self.make_todo(note="2리터짜리로")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.headers["Location"], "/api/todos/1")
        self.assertEqual(
            response.get_json(),
            {"id": 1, "text": "우유 사기", "done": False, "note": "2리터짜리로"},
        )

    def test_omitted_note_is_empty(self):
        response = self.make_todo()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["note"], "")

    def test_list_and_read_one(self):
        self.make_todo(note="2리터짜리로")
        self.client.post("/api/todos/", json={"text": "책 반납"})
        response = self.client.get("/api/todos/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 2)
        self.assertEqual(response.get_json()[0]["note"], "2리터짜리로")
        self.assertEqual(response.get_json()[1]["note"], "")
        self.assertEqual(self.client.get("/api/todos/1").get_json()["note"], "2리터짜리로")
        self.assertEqual(self.client.get("/api/todos/2").get_json()["text"], "책 반납")

    def test_filter_by_done_and_unfiltered_list(self):
        self.make_todo(done=True)
        self.client.post("/api/todos/", json={"text": "책 반납"})
        self.assertEqual(
            [todo["id"] for todo in self.client.get("/api/todos/?done=true").get_json()],
            [1],
        )
        self.assertEqual(
            [todo["id"] for todo in self.client.get("/api/todos/?done=false").get_json()],
            [2],
        )
        self.assertEqual(len(self.client.get("/api/todos/").get_json()), 2)

    def test_put_replaces_all_fields(self):
        self.make_todo(done=True, note="기존 설명")
        response = self.client.put("/api/todos/1", json={"text": "책 반납"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {"id": 1, "text": "책 반납", "done": False, "note": ""},
        )

    def test_patch_changes_only_sent_field(self):
        self.make_todo(note="2리터짜리로")
        response = self.client.patch("/api/todos/1", json={"done": True})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["text"], "우유 사기")
        self.assertEqual(response.get_json()["note"], "2리터짜리로")
        self.assertTrue(response.get_json()["done"])

        response = self.client.patch("/api/todos/1", json={"note": "1리터짜리로"})
        self.assertEqual(response.get_json()["note"], "1리터짜리로")
        self.assertTrue(response.get_json()["done"])

    def test_delete_returns_empty_204_then_404(self):
        self.make_todo()
        response = self.client.delete("/api/todos/1")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data, b"")
        self.assertEqual(self.client.get("/api/todos/1").status_code, 404)

    def test_missing_id_returns_json_404(self):
        response = self.client.get("/api/todos/999")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json(), {"message": "999번 할 일이 없습니다"})

    def test_swagger_docs_expose_filter_and_note(self):
        self.assertEqual(self.client.get("/api/docs").status_code, 200)
        schema = self.client.get("/api/swagger.json").get_json()
        self.assertIn("note", schema["definitions"]["Todo"]["properties"])
        self.assertIn("note", schema["definitions"]["TodoInput"]["properties"])
        parameters = schema["paths"]["/todos/"]["get"]["parameters"]
        self.assertTrue(any(param["name"] == "done" for param in parameters))

    def test_web_form_accepts_note(self):
        response = self.client.post(
            "/", data={"todo": "과제 제출", "note": "목요일까지"}
        )
        self.assertEqual(response.status_code, 302)
        page = self.client.get("/")
        self.assertIn("과제 제출".encode(), page.data)
        self.assertIn("목요일까지".encode(), page.data)


if __name__ == "__main__":
    unittest.main()
