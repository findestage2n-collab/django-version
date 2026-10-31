import pytest

URL = "/api/v1/patients/"
PAYLOAD = {"nom": "Ndongo", "prenom": "Paul", "sexe": "M", "date_naissance": "1985-03-12"}


def test_unauthenticated_is_401(api_client):
    assert api_client.get(URL).status_code == 401


def test_role_without_permission_is_403(auth_client):
    client = auth_client()  # aucun rôle
    assert client.get(URL).status_code == 403
    assert client.post(URL, PAYLOAD).status_code == 403


def test_medecin_can_read_but_not_write(auth_client):
    client = auth_client("MEDECIN")
    assert client.get(URL).status_code == 200
    assert client.post(URL, PAYLOAD).status_code == 403


def test_secretaire_creates_patient(auth_client):
    response = auth_client("SECRETAIRE").post(URL, PAYLOAD)
    assert response.status_code == 201
    body = response.json()
    assert body["numero_dossier"].startswith("P")
    assert "id" not in body  # seul l'identifiant public est exposé
    assert body["age"] is not None


def test_validation_error_uses_standard_envelope(auth_client):
    response = auth_client("SECRETAIRE").post(URL, {"nom": "X"})
    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    assert "prenom" in error["details"]


def test_future_birth_date_is_refused(auth_client):
    response = auth_client("SECRETAIRE").post(URL, {**PAYLOAD, "date_naissance": "2999-01-01"})
    assert response.status_code == 400


def test_duplicate_returns_409(auth_client):
    client = auth_client("SECRETAIRE")
    assert client.post(URL, PAYLOAD).status_code == 201
    response = client.post(URL, PAYLOAD)
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "duplicate_patient"
    assert client.post(URL, {**PAYLOAD, "allow_duplicate": True}).status_code == 201


def test_list_search_and_pagination(auth_client):
    client = auth_client("SECRETAIRE")
    for i in range(3):
        client.post(URL, {**PAYLOAD, "nom": f"Nom{i}"})
    listing = client.get(URL, {"page_size": 2}).json()
    assert listing["count"] == 3 and len(listing["results"]) == 2 and listing["next"]
    found = client.get(URL, {"q": "Nom1"}).json()
    assert found["count"] == 1


def test_unknown_public_id_is_404_and_integer_id_not_routable(auth_client):
    client = auth_client("SECRETAIRE")
    assert client.get(URL + "00000000-0000-0000-0000-000000000000/").status_code == 404
    assert client.get(URL + "1/").status_code == 404


def test_patch_and_archive(auth_client):
    client = auth_client("SECRETAIRE")
    public_id = client.post(URL, PAYLOAD).json()["public_id"]
    patched = client.patch(f"{URL}{public_id}/", {"telephone": "+237 650 00 00 00"})
    assert patched.status_code == 200
    assert patched.json()["telephone"] == "+237 650 00 00 00"
    assert client.delete(f"{URL}{public_id}/").status_code == 204
    assert client.get(f"{URL}{public_id}/").status_code == 404


def test_mass_assignment_is_blocked(auth_client):
    client = auth_client("SECRETAIRE")
    response = client.post(URL, {**PAYLOAD, "numero_dossier": "HACK", "created_by": 1})
    assert response.status_code == 201
    assert response.json()["numero_dossier"] != "HACK"


@pytest.mark.parametrize("phone", ["abc", "12"])
def test_invalid_phone_is_refused(auth_client, phone):
    response = auth_client("SECRETAIRE").post(URL, {**PAYLOAD, "telephone": phone})
    assert response.status_code == 400


def test_actions_are_audited(auth_client):
    from apps.audit.public import audit_entries_for_target

    client = auth_client("SECRETAIRE")
    public_id = client.post(URL, PAYLOAD).json()["public_id"]
    entry = next(
        e
        for e in audit_entries_for_target("patient", public_id)
        if e.action == "patient.registered"
    )
    assert entry.request_id  # corrélation avec les journaux applicatifs
