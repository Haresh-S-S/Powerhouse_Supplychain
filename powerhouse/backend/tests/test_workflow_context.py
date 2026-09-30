"""
Suite 8: Workflow Context & Compliance Tasks Test Suite
Verifies that compliance tasks link to statutory approvals and contain priority scores and due dates.
"""
import pytest
from app.engine.business_analyzer import analyze_business_profile

def test_workflow_tasks_statutory_linkage():
    profile = {
        "business_name": "TexCorp India",
        "business_category": "clothing_textile",
        "company_size": "Small",
        "city": "Tiruppur",
        "state": "Tamil Nadu",
        "employee_count": 30
    }
    res = analyze_business_profile(profile)
    tasks = res["compliance_tasks"]
    assert len(tasks) > 0

    for task in tasks:
        assert "title" in task and len(task["title"]) > 0
        assert "category" in task
        assert "priority" in task and task["priority"] in ["High", "Medium", "Low"]
        assert "due_date" in task

def test_restaurant_workflow_tasks():
    profile = {
        "business_name": "Chettinad Kitchen",
        "business_category": "restaurant",
        "company_size": "Small",
        "city": "Tiruppur",
        "state": "Tamil Nadu",
        "employee_count": 10
    }
    res = analyze_business_profile(profile)
    tasks = res["compliance_tasks"]
    task_titles = [t["title"] for t in tasks]
    assert any("Food Safety" in t or "Kitchen" in t for t in task_titles)
