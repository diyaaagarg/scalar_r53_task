from tests.test_hosted_zones import create_zone


def test_record_validation_cname_conflict_and_zone_delete_guard(authenticated_client):
    client = authenticated_client
    zone = create_zone(client)
    base = f"/api/v1/hosted-zones/{zone['id']}/records"
    created = client.post(
        base,
        json={
            "name": "www.example.com",
            "record_type": "A",
            "ttl": 60,
            "values": ["192.0.2.44"],
        },
    )
    assert created.status_code == 201
    conflict = client.post(
        base,
        json={
            "name": "www.example.com",
            "record_type": "CNAME",
            "ttl": 60,
            "values": ["target.example.com."],
        },
    )
    assert conflict.status_code == 409
    deletion = client.request(
        "DELETE", f"/api/v1/hosted-zones/{zone['id']}", json={"confirmation": "delete"}
    )
    assert deletion.status_code == 409
    assert client.delete(f"{base}/{created.json()['id']}").status_code == 204
    assert (
        client.request(
            "DELETE",
            f"/api/v1/hosted-zones/{zone['id']}",
            json={"confirmation": "delete"},
        ).status_code
        == 204
    )


def test_invalid_values_are_rejected(authenticated_client):
    zone = create_zone(authenticated_client)
    response = authenticated_client.post(
        f"/api/v1/hosted-zones/{zone['id']}/records",
        json={"name": "x.example.com", "record_type": "A", "values": ["not-an-ip"]},
    )
    assert response.status_code == 400
