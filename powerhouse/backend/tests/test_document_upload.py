import io
import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.business import BusinessProfile
from app.models.approval import Approval
from app.dependencies.database import get_db

client = TestClient(app)

SAMPLE_PDF_BYTES = b"%PDF-1.4\n1 0 obj\n<< /Title (Textile Committee Certificate) /Producer (Powerhouse) >>\nendobj\n2 0 obj\n<< /Type /Catalog /Pages 3 0 R >>\nendobj\n3 0 obj\n<< /Type /Pages /Kids [4 0 R] /Count 1 >>\nendobj\n4 0 obj\n<< /Type /Page /Parent 3 0 R /MediaBox [0 0 612 792] /Contents 5 0 R >>\nendobj\n5 0 obj\n<< /Length 120 >>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Textile Committee Statutory Registration Proof GSTIN 33AAAAA0000A1Z5 PAN ABCDE1234F) Tj\nET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000084 00000 n \n0000000135 00000 n \n0000000192 00000 n \n0000000281 00000 n \ntrailer\n<< /Size 6 /Root 2 0 R >>\nstartxref\n452\n%%EOF"


def create_authenticated_user_and_business(email: str, business_name: str, category: str = "clothing_textile"):
    client.post("/api/v1/auth/signup", json={
        "email": email,
        "password": "Password123!",
        "full_name": "Test User",
    })
    login_res = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "Password123!",
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    profile_res = client.post("/api/v1/business-profile", json={
        "business_name": business_name,
        "business_type": "Private Limited Company",
        "industry": category,
        "company_size": "Small",
        "business_category": category,
        "city": "Tiruppur",
        "state": "Tamil Nadu",
        "employee_count": 25,
        "onboarding_completed": True,
    }, headers=headers)
    profile_id = profile_res.json()["id"]

    return headers, profile_id


def test_valid_pdf_upload_and_intelligence():
    headers, profile_id = create_authenticated_user_and_business("doc_user1@powerhouse.io", "Apex Textile Mill")

    files = {
        "file": ("textile_cert.pdf", io.BytesIO(SAMPLE_PDF_BYTES), "application/pdf")
    }
    data = {
        "business_profile_id": profile_id,
        "title": "Textile Committee Statutory Registration",
        "category": "Statutory License",
        "related_approval": "Textile Committee / Ministry of Textiles Compliance"
    }

    res = client.post("/api/v1/documents/upload", files=files, data=data, headers=headers)
    assert res.status_code == 201
    doc = res.json()
    assert doc["name"] == "Textile Committee Statutory Registration"
    assert doc["business_profile_id"] == profile_id
    assert doc["file_type"] == "PDF"
    assert doc["status"] in ["Verified", "Uploaded", "Needs Review"]
    assert doc["analysis_status"] in ["Analyzed", "Uploaded"]
    assert "content_hash" in doc and doc["content_hash"] is not None

    doc_id = doc["id"]

    # Test file retrieval / download
    file_res = client.get(f"/api/v1/documents/{doc_id}/file", headers=headers)
    assert file_res.status_code == 200
    assert file_res.content == SAMPLE_PDF_BYTES

    # Test intelligence endpoint
    intel_res = client.get(f"/api/v1/documents/{doc_id}/intelligence", headers=headers)
    assert intel_res.status_code == 200
    intel = intel_res.json()
    assert intel["document_id"] == doc_id
    assert "intelligence" in intel


def test_upload_missing_title_rejected():
    headers, profile_id = create_authenticated_user_and_business("doc_user2@powerhouse.io", "Title Test Co")

    files = {
        "file": ("test.pdf", io.BytesIO(SAMPLE_PDF_BYTES), "application/pdf")
    }
    data = {
        "business_profile_id": profile_id,
        "title": "   ",  # blank title
        "category": "Statutory License"
    }

    res = client.post("/api/v1/documents/upload", files=files, data=data, headers=headers)
    assert res.status_code == 422
    assert "Enter a document title" in res.json()["detail"]


def test_upload_unsupported_format_rejected():
    headers, profile_id = create_authenticated_user_and_business("doc_user3@powerhouse.io", "Format Test Co")

    files = {
        "file": ("malicious.exe", io.BytesIO(b"MZ\x90\x00executable content"), "application/x-msdownload")
    }
    data = {
        "business_profile_id": profile_id,
        "title": "Suspicious Executable",
        "category": "Statutory License"
    }

    res = client.post("/api/v1/documents/upload", files=files, data=data, headers=headers)
    assert res.status_code == 415


def test_upload_mismatched_magic_bytes_rejected():
    headers, profile_id = create_authenticated_user_and_business("doc_user4@powerhouse.io", "Magic Byte Test Co")

    files = {
        "file": ("fake.pdf", io.BytesIO(b"This is just plain text, not a real PDF file!"), "application/pdf")
    }
    data = {
        "business_profile_id": profile_id,
        "title": "Fake PDF File",
        "category": "Statutory License"
    }

    res = client.post("/api/v1/documents/upload", files=files, data=data, headers=headers)
    assert res.status_code == 415
    assert "signature does not match" in res.json()["detail"]


def test_upload_tenant_isolation_forbidden():
    headers_user_a, profile_a = create_authenticated_user_and_business("owner_a@powerhouse.io", "Owner A Business")
    headers_user_b, profile_b = create_authenticated_user_and_business("intruder_b@powerhouse.io", "Intruder B Business")

    # User B attempts to upload document to User A's profile
    files = {
        "file": ("intruder.pdf", io.BytesIO(SAMPLE_PDF_BYTES), "application/pdf")
    }
    data = {
        "business_profile_id": profile_a,
        "title": "Malicious Intruder Doc",
        "category": "Statutory License"
    }

    res = client.post("/api/v1/documents/upload", files=files, data=data, headers=headers_user_b)
    assert res.status_code == 403
    assert "Access forbidden" in res.json()["detail"]


def test_document_download_tenant_isolation_forbidden():
    headers_user_a, profile_a = create_authenticated_user_and_business("file_owner_a@powerhouse.io", "File Owner Business")
    headers_user_b, profile_b = create_authenticated_user_and_business("file_intruder_b@powerhouse.io", "File Intruder Business")

    # User A uploads
    files = {
        "file": ("confidential.pdf", io.BytesIO(SAMPLE_PDF_BYTES), "application/pdf")
    }
    data = {
        "business_profile_id": profile_a,
        "title": "Confidential Tax Document",
        "category": "Taxation"
    }
    upload_res = client.post("/api/v1/documents/upload", files=files, data=data, headers=headers_user_a)
    assert upload_res.status_code == 201
    doc_id = upload_res.json()["id"]

    # User B attempts to download User A's file
    res = client.get(f"/api/v1/documents/{doc_id}/file", headers=headers_user_b)
    assert res.status_code == 403

    # User B attempts to get intelligence
    res_intel = client.get(f"/api/v1/documents/{doc_id}/intelligence", headers=headers_user_b)
    assert res_intel.status_code == 403


def test_business_switching_document_isolation():
    # Single user with two distinct business profiles
    client.post("/api/v1/auth/signup", json={
        "email": "multibiz_owner@powerhouse.io",
        "password": "Password123!",
        "full_name": "Multi Owner",
    })
    login_res = client.post("/api/v1/auth/login", json={
        "email": "multibiz_owner@powerhouse.io",
        "password": "Password123!",
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create Textile profile
    res_textile = client.post("/api/v1/business-profile", json={
        "business_name": "Multi Textile Works",
        "business_type": "Sole Proprietorship",
        "industry": "Textile",
        "company_size": "Small",
        "business_category": "clothing_textile",
        "city": "Coimbatore",
        "state": "Tamil Nadu",
        "onboarding_completed": True,
    }, headers=headers)
    textile_id = res_textile.json()["id"]

    # 2. Create Restaurant profile
    res_rest = client.post("/api/v1/business-profile", json={
        "business_name": "Multi Spice Diner",
        "business_type": "Sole Proprietorship",
        "industry": "Food & Beverage",
        "company_size": "Small",
        "business_category": "restaurant",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "onboarding_completed": True,
    }, headers=headers)
    restaurant_id = res_rest.json()["id"]

    # Upload document to Textile
    files = {
        "file": ("textile_pollution.pdf", io.BytesIO(SAMPLE_PDF_BYTES), "application/pdf")
    }
    data = {
        "business_profile_id": textile_id,
        "title": "TNPCB ETP Consent Certificate",
        "category": "Environmental"
    }
    client.post("/api/v1/documents/upload", files=files, data=data, headers=headers)

    # Query Restaurant documents -> MUST be empty / not contain Textile doc
    rest_docs = client.get(f"/api/v1/documents?business_profile_id={restaurant_id}", headers=headers).json()
    assert not any(d["name"] == "TNPCB ETP Consent Certificate" for d in rest_docs)

    # Query Textile documents -> MUST contain Textile doc
    textile_docs = client.get(f"/api/v1/documents?business_profile_id={textile_id}", headers=headers).json()
    assert any(d["name"] == "TNPCB ETP Consent Certificate" for d in textile_docs)


def test_duplicate_document_upload_deduplication():
    headers, profile_id = create_authenticated_user_and_business("dedup_user@powerhouse.io", "Dedup Enterprise")

    files = {
        "file": ("dedup_test.pdf", io.BytesIO(SAMPLE_PDF_BYTES), "application/pdf")
    }
    data = {
        "business_profile_id": profile_id,
        "title": "Initial Registration Certificate",
        "category": "Statutory License"
    }

    # First upload
    res1 = client.post("/api/v1/documents/upload", files=files, data=data, headers=headers)
    assert res1.status_code == 201
    doc1_id = res1.json()["id"]

    # Second upload with identical file bytes
    files2 = {
        "file": ("dedup_test_copy.pdf", io.BytesIO(SAMPLE_PDF_BYTES), "application/pdf")
    }
    res2 = client.post("/api/v1/documents/upload", files=files2, data=data, headers=headers)
    assert res2.status_code == 200 or res2.status_code == 201
    doc2 = res2.json()
    assert doc2["id"] == doc1_id
    assert doc2["content_hash"] == res1.json()["content_hash"]


def test_document_deletion_cleanup():
    headers, profile_id = create_authenticated_user_and_business("delete_user@powerhouse.io", "Delete Test Co")

    files = {
        "file": ("delete_me.pdf", io.BytesIO(SAMPLE_PDF_BYTES), "application/pdf")
    }
    data = {
        "business_profile_id": profile_id,
        "title": "Temporary Clearance Note",
        "category": "Safety"
    }

    res = client.post("/api/v1/documents/upload", files=files, data=data, headers=headers)
    assert res.status_code == 201
    doc_id = res.json()["id"]

    # Delete the document
    del_res = client.delete(f"/api/v1/documents/{doc_id}", headers=headers)
    assert del_res.status_code == 200

    # Ensure get returns 404
    get_res = client.get(f"/api/v1/documents/{doc_id}", headers=headers)
    assert get_res.status_code == 404
