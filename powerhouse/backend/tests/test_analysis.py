def test_run_business_analysis(client):
    # Create profile
    profile_payload = {
        "business_name": "Precision Dynamics Ltd",
        "business_type": "Public Limited Company",
        "industry": "Manufacturing",
        "sector": "Industrial Valves",
        "company_size": "Medium Enterprise",
        "employee_count": 85,
        "city": "Mumbai",
        "state": "Maharashtra",
        "country": "India",
        "manufacturing_activity": True,
        "import_activities": True,
        "export_activities": False,
        "environmental_impact": "Moderate",
        "operating_status": "Active",
        "has_gst": True,
        "has_msme_registration": True,
        "has_udyam_registration": True,
        "gstin": "27AAACP4821K1ZV",
        "udyam_number": "UDYAM-MH-19-0024891"
    }

    create_res = client.post("/api/v1/business-profile", json=profile_payload)
    assert create_res.status_code == 201
    profile_id = create_res.json()["id"]

    # Run Analysis
    analysis_res = client.post(f"/api/v1/business-analysis/{profile_id}")
    assert analysis_res.status_code == 201
    analysis_data = analysis_res.json()

    assert analysis_data["business_profile_id"] == profile_id
    assert analysis_data["total_approvals"] >= 8
    assert analysis_data["total_compliance_tasks"] >= 5
    assert analysis_data["total_recommended_schemes"] >= 3
    assert analysis_data["risk_level"] in ["Low", "Medium", "High"]
    assert "insights" in analysis_data["analysis_result"]

    # Retrieve latest analysis
    latest_res = client.get(f"/api/v1/business-analysis/{profile_id}/latest")
    assert latest_res.status_code == 200
    assert latest_res.json()["id"] == analysis_data["id"]

    # Verify populated Approvals in Approvals API
    appr_res = client.get(f"/api/v1/approvals?business_profile_id={profile_id}")
    assert appr_res.status_code == 200
    assert len(appr_res.json()) >= 8

    # Verify populated Tasks in Tasks API
    task_res = client.get(f"/api/v1/tasks?business_profile_id={profile_id}")
    assert task_res.status_code == 200
    assert len(task_res.json()) >= 5
