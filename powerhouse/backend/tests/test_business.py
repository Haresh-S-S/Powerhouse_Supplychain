def test_create_and_get_business_profile(client):
    payload = {
        "business_name": "Apex Engineering Works",
        "business_type": "Private Limited Company",
        "industry": "Manufacturing",
        "sector": "Heavy Machining",
        "established_date": "2019-01-10",
        "company_size": "Small Enterprise",
        "employee_count": 45,
        "annual_turnover": "₹12 Crores",
        "registered_address": "Plot 10, MIDC Thane",
        "city": "Thane",
        "state": "Maharashtra",
        "country": "India",
        "postal_code": "400601",
        "manufacturing_activity": True,
        "import_activities": False,
        "export_activities": False,
        "environmental_impact": "Moderate",
        "operating_status": "Active",
        "has_gst": True,
        "has_msme_registration": True,
        "has_udyam_registration": True,
        "cin": "U28113MH2019PTC123456",
        "pan": "AABCA1234E",
        "gstin": "27AABCA1234E1Z5",
        "udyam_number": "UDYAM-MH-33-0012345"
    }

    # 1. Create
    res = client.post("/api/v1/business-profile", json=payload)
    assert res.status_code == 201
    created_data = res.json()
    assert "id" in created_data
    assert created_data["business_name"] == "Apex Engineering Works"
    profile_id = created_data["id"]

    # 2. Get by ID
    get_res = client.get(f"/api/v1/business-profile/{profile_id}")
    assert get_res.status_code == 200
    assert get_res.json()["city"] == "Thane"

    # 3. Update
    update_res = client.put(f"/api/v1/business-profile/{profile_id}", json={"employee_count": 50, "annual_turnover": "₹15 Crores"})
    assert update_res.status_code == 200
    assert update_res.json()["employee_count"] == 50
    assert update_res.json()["annual_turnover"] == "₹15 Crores"


def test_get_non_existent_profile(client):
    res = client.get("/api/v1/business-profile/non-existent-uuid")
    assert res.status_code == 404
