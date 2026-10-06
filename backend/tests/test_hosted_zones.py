def create_zone(client, **overrides):
    body = {
        "name": "example.com",
        "description": "Demo zone",
        "type": "PUBLIC",
        "tags": [{"key": "env", "value": "test"}],
    }
    body.update(overrides)
    response = client.post("/api/v1/hosted-zones", json=body)
    assert response.status_code == 201, response.text
    return response.json()


def test_hosted_zone_crud_and_default_records(authenticated_client):
    client = authenticated_client
    zone = create_zone(client)
    listing = client.get("/api/v1/hosted-zones?search=example")
    assert listing.json()["pagination"]["total"] == 1
    records = client.get(f"/api/v1/hosted-zones/{zone['id']}/records").json()["items"]
    assert {item["record_type"] for item in records} == {"NS", "SOA"}
    changed = client.patch(
        f"/api/v1/hosted-zones/{zone['id']}", json={"description": "Changed"}
    )
    assert changed.json()["description"] == "Changed"
    assert (
        client.request(
            "DELETE",
            f"/api/v1/hosted-zones/{zone['id']}",
            json={"confirmation": "delete"},
        ).status_code
        == 204
    )


def test_private_zone_requires_vpc(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/hosted-zones", json={"name": "internal.example", "type": "PRIVATE"}
    )
    assert response.status_code == 400
    vpc = authenticated_client.get("/api/v1/vpcs").json()["items"][0]
    response = authenticated_client.post(
        "/api/v1/hosted-zones",
        json={"name": "internal.example", "type": "PRIVATE", "vpc_ids": [vpc["id"]]},
    )
    assert response.status_code == 201
