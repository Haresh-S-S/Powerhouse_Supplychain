"""
Suite 2: Category Isolation Test Suite
Verifies strict cross-category isolation and divergence between business sectors.
"""
import pytest
from app.engine.business_analyzer import analyze_business_profile, compare_business_categories

def test_textile_vs_restaurant_divergence():
    comparison = compare_business_categories("factory", "restaurant", city="Tiruppur", state="Tamil Nadu")
    summary = comparison["comparison_summary"]
    assert summary["divergence_percentage"] >= 70.0
    assert summary["divergence_percentage"] == 73.0

    # Approvals exclusive to restaurant
    rest_exclusive = summary["exclusive_to_category_b"]
    assert any("FSSAI" in a for a in rest_exclusive)
    assert any("Eating House" in a for a in rest_exclusive)
    assert any("Fire Safety NOC (Kitchen / Dining)" in a for a in rest_exclusive)

    # Approvals exclusive to factory / textile
    fact_exclusive = summary["exclusive_to_category_a"]
    assert any("Pollution" in a or "Factory" in a or "Textile" in a for a in fact_exclusive)

def test_jewellery_vs_retail_divergence():
    jewellery_profile = {
        "business_name": "Kalyan Jewellers Demo",
        "business_category": "jewellery",
        "industry": "Jewellery",
        "company_size": "Small",
        "city": "Coimbatore",
        "state": "Tamil Nadu",
        "employee_count": 15,
        "annual_turnover": "₹12.0 Cr"
    }
    retail_profile = {
        "business_name": "Nilgiris Supermarket Demo",
        "business_category": "retail",
        "industry": "Retail & Supermarket",
        "company_size": "Small",
        "city": "Coimbatore",
        "state": "Tamil Nadu",
        "employee_count": 15,
        "annual_turnover": "₹12.0 Cr"
    }

    res_j = analyze_business_profile(jewellery_profile)
    res_r = analyze_business_profile(retail_profile)

    j_approvals = [a["name"] for a in res_j["approvals"]]
    r_approvals = [a["name"] for a in res_r["approvals"]]

    # BIS Hallmarking and PMLA must only appear in jewellery
    assert any("BIS Hallmarking" in a for a in j_approvals)
    assert any("PMLA" in a for a in j_approvals)
    assert not any("BIS Hallmarking" in a for a in r_approvals)
    assert not any("PMLA" in a for a in r_approvals)

def test_all_five_categories_mutually_distinct():
    categories = ["clothing_textile", "restaurant", "jewellery", "retail", "manufacturing"]
    workspaces = {}
    for cat in categories:
        profile = {
            "business_name": f"Enterprise {cat}",
            "business_category": cat,
            "company_size": "Small",
            "city": "Tiruppur",
            "state": "Tamil Nadu",
            "employee_count": 20
        }
        res = analyze_business_profile(profile)
        workspaces[cat] = set(a["name"] for a in res["approvals"])

    # Verify no two categories have identical approval sets
    for i in range(len(categories)):
        for j in range(i + 1, len(categories)):
            cat_a, cat_b = categories[i], categories[j]
            assert workspaces[cat_a] != workspaces[cat_b], f"Overlap between {cat_a} and {cat_b}"
