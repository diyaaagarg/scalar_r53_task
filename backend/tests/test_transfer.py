from tests.test_hosted_zones import create_zone


def test_bind_import_and_exports(authenticated_client):
    zone = create_zone(authenticated_client)
    zone_id = zone["id"]
    bind = """$ORIGIN example.com.
$TTL 300
www IN A 192.0.2.10
mail 600 IN MX 10 mail.example.com.
"""
    imported = authenticated_client.post(
        f"/api/v1/hosted-zones/{zone_id}/import",
        json={"format": "BIND", "content": bind},
    )
    assert imported.status_code == 201, imported.text
    assert imported.json()["created_count"] == 2
    exported_json = authenticated_client.get(
        f"/api/v1/hosted-zones/{zone_id}/export?format=json"
    )
    assert exported_json.status_code == 200
    assert {record["type"] for record in exported_json.json()["records"]} >= {
        "A",
        "MX",
        "NS",
        "SOA",
    }
    exported_bind = authenticated_client.get(
        f"/api/v1/hosted-zones/{zone_id}/export?format=bind"
    )
    assert exported_bind.status_code == 200
    assert "www" in exported_bind.text
