import json
import threading
import unittest
import urllib.error
import urllib.request

from tasks_api.server import create_server


class ApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = create_server(port=0)
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def call(self, method, path, body=None):
        data = None if body is None else json.dumps(body).encode()
        req = urllib.request.Request(self.base + path, data=data, method=method)
        try:
            with urllib.request.urlopen(req) as r:
                raw = r.read()
                return r.status, json.loads(raw) if raw else None
        except urllib.error.HTTPError as e:
            raw = e.read()
            return e.code, json.loads(raw) if raw else None

    def test_crud_flow(self):
        status, task = self.call("POST", "/tasks", {"title": "  Write tests "})
        self.assertEqual(status, 201)
        self.assertEqual(task["title"], "Write tests")
        self.assertFalse(task["done"])
        tid = task["id"]

        status, task = self.call("PATCH", f"/tasks/{tid}", {"done": True})
        self.assertEqual((status, task["done"]), (200, True))

        status, task = self.call("GET", f"/tasks/{tid}")
        self.assertEqual(status, 200)

        status, tasks = self.call("GET", "/tasks")
        self.assertIn(tid, [t["id"] for t in tasks])

        self.assertEqual(self.call("DELETE", f"/tasks/{tid}")[0], 204)
        self.assertEqual(self.call("GET", f"/tasks/{tid}")[0], 404)

    def test_validation(self):
        self.assertEqual(self.call("POST", "/tasks", {"title": ""})[0], 400)
        self.assertEqual(self.call("POST", "/tasks", {})[0], 400)
        self.assertEqual(self.call("PATCH", "/tasks/9999", {"done": True})[0], 404)
        self.assertEqual(self.call("GET", "/nope")[0], 404)

    def test_patch_rejects_bad_types(self):
        _, task = self.call("POST", "/tasks", {"title": "x"})
        status, _ = self.call("PATCH", f"/tasks/{task['id']}", {"done": "yes"})
        self.assertEqual(status, 400)


if __name__ == "__main__":
    unittest.main()
