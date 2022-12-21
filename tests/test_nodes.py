

class TestGetNode:
    def test_existing_node(self, client):
        resp = client.get("/nodes/info/SN0")
        assert resp.status_code == 200
        assert resp.json["user"]["id"] == "001"
    def test_remove_raw(self, client):
        resp = client.get("/nodes/info/SN1")
        assert resp.status_code == 200
        assert resp.json["position"].get("raw") == None
    def test_non_existant_node(self, client):
        resp = client.get("/nodes/info/fakeSerial")
        assert resp.status_code == 404