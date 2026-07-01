import pytest
from app.config import settings

# Test API Key Authentication
def test_authentication_missing_key(client):
    response = client.post("/tickets", json={})
    assert response.status_code == 401
    assert "API Key is missing" in response.json()["message"]

def test_authentication_invalid_key(client):
    headers = {"X-API-Key": "wrong-key"}
    response = client.post("/tickets", json={}, headers=headers)
    assert response.status_code == 401
    assert "Invalid API Key" in response.json()["message"]


# Test CRUD Operations
def test_create_ticket_success(client):
    headers = {"X-API-Key": settings.API_KEY}
    payload = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "subject": "Printer issue",
        "description": "Printer is jammed and displaying error code 500."
    }
    response = client.post("/tickets", json=payload, headers=headers)
    assert response.status_code == 201
    
    root_data = response.json()
    assert root_data["success"] is True
    assert "Ticket created successfully" in root_data["message"]
    
    data = root_data["data"]
    assert data["customer_name"] == "John Doe"
    assert data["customer_email"] == "john@example.com"
    assert data["subject"] == "Printer issue"
    assert data["description"] == "Printer is jammed and displaying error code 500."
    assert data["status"] == "open"  # default value
    assert data["priority"] == "low"  # default value
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_create_ticket_validation_failures(client):
    headers = {"X-API-Key": settings.API_KEY}
    
    # Invalid email
    payload = {
        "customer_name": "John Doe",
        "customer_email": "not-an-email",
        "subject": "Printer issue",
        "description": "Details here"
    }
    response = client.post("/tickets", json=payload, headers=headers)
    assert response.status_code == 422
    assert "validation_error" in response.json()["status"]
    
    # Invalid status
    payload = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "subject": "Printer issue",
        "description": "Details here",
        "status": "invalid_status"
    }
    response = client.post("/tickets", json=payload, headers=headers)
    assert response.status_code == 422
    
    # Invalid priority
    payload = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "subject": "Printer issue",
        "description": "Details here",
        "priority": "very_high"
    }
    response = client.post("/tickets", json=payload, headers=headers)
    assert response.status_code == 422

def test_read_ticket_by_id(client):
    headers = {"X-API-Key": settings.API_KEY}
    
    # Create a ticket first
    create_response = client.post("/tickets", json={
        "customer_name": "Alice Smith",
        "customer_email": "alice@example.com",
        "subject": "Login Failure",
        "description": "Unable to log in using Google OAuth.",
        "priority": "high"
    }, headers=headers)
    ticket_id = create_response.json()["data"]["id"]
    
    # Fetch it
    response = client.get(f"/tickets/{ticket_id}", headers=headers)
    assert response.status_code == 200
    
    root_data = response.json()
    assert root_data["success"] is True
    
    data = root_data["data"]
    assert data["customer_name"] == "Alice Smith"
    assert data["priority"] == "high"

def test_read_ticket_not_found(client):
    headers = {"X-API-Key": settings.API_KEY}
    response = client.get("/tickets/non-existent-uuid", headers=headers)
    assert response.status_code == 404
    assert "not found" in response.json()["message"]


def test_update_ticket_success(client):
    headers = {"X-API-Key": settings.API_KEY}
    
    # Create ticket
    create_response = client.post("/tickets", json={
        "customer_name": "Bob Jones",
        "customer_email": "bob@example.com",
        "subject": "Slow performance",
        "description": "Dashboard takes 10s to load.",
        "status": "open"
    }, headers=headers)
    ticket_id = create_response.json()["data"]["id"]
    
    # Patch status and priority
    update_payload = {
        "status": "in_progress",
        "priority": "medium",
        "description": "Dashboard takes 10s to load. Escalated to tier 2."
    }
    response = client.patch(f"/tickets/{ticket_id}", json=update_payload, headers=headers)
    assert response.status_code == 200
    
    root_data = response.json()
    assert root_data["success"] is True
    
    data = root_data["data"]
    assert data["status"] == "in_progress"
    assert data["priority"] == "medium"
    assert data["description"] == "Dashboard takes 10s to load. Escalated to tier 2."
    assert data["customer_name"] == "Bob Jones" # Unchanged field remains the same

def test_delete_ticket_success(client):
    headers = {"X-API-Key": settings.API_KEY}
    
    # Create ticket
    create_response = client.post("/tickets", json={
        "customer_name": "Charlie",
        "customer_email": "charlie@example.com",
        "subject": "Delete me",
        "description": "Temporary ticket."
    }, headers=headers)
    ticket_id = create_response.json()["data"]["id"]
    
    # Delete ticket
    delete_response = client.delete(f"/tickets/{ticket_id}", headers=headers)
    assert delete_response.status_code == 200
    
    root_data = delete_response.json()
    assert root_data["success"] is True
    assert root_data["data"]["id"] == ticket_id
    
    # Verify it is deleted
    get_response = client.get(f"/tickets/{ticket_id}", headers=headers)
    assert get_response.status_code == 404

# Test Pagination
def test_tickets_pagination(client):
    headers = {"X-API-Key": settings.API_KEY}
    
    # Create 5 tickets
    for i in range(5):
        client.post("/tickets", json={
            "customer_name": f"User {i}",
            "customer_email": f"user{i}@example.com",
            "subject": f"Issue {i}",
            "description": f"Description of issue {i}"
        }, headers=headers)
        
    # Get page 1 with page_size = 3
    response_p1 = client.get("/tickets?page=1&page_size=3", headers=headers)
    assert response_p1.status_code == 200
    
    root_p1 = response_p1.json()
    assert root_p1["success"] is True
    assert root_p1["pagination"]["page"] == 1
    assert root_p1["pagination"]["page_size"] == 3
    assert root_p1["pagination"]["total_items"] == 5
    assert root_p1["pagination"]["total_pages"] == 2
    
    data_p1 = root_p1["data"]
    assert len(data_p1) == 3
    
    # Get page 2 with page_size = 3
    response_p2 = client.get("/tickets?page=2&page_size=3", headers=headers)
    assert response_p2.status_code == 200
    
    root_p2 = response_p2.json()
    data_p2 = root_p2["data"]
    assert len(data_p2) == 2  # remaining 2 tickets

# Test Search and Filters
def test_tickets_search_filters(client):
    headers = {"X-API-Key": settings.API_KEY}
    
    # Create a couple of distinct tickets
    client.post("/tickets", json={
        "customer_name": "Alice Developer",
        "customer_email": "alice.dev@company.com",
        "subject": "Deployment breakdown",
        "description": "Production environment is down after last release.",
        "status": "closed",
        "priority": "urgent"
    }, headers=headers)
    
    client.post("/tickets", json={
        "customer_name": "Charlie Manager",
        "customer_email": "charlie@company.com",
        "subject": "Billing inquiry",
        "description": "How do we upgrade our plan?",
        "status": "open",
        "priority": "low"
    }, headers=headers)

    # Search by status
    resp = client.get("/tickets?status=closed", headers=headers)
    assert resp.status_code == 200
    
    root_status = resp.json()
    assert root_status["success"] is True
    assert len(root_status["data"]) == 1
    assert root_status["data"][0]["customer_name"] == "Alice Developer"
    
    # Search by general query matching email
    resp = client.get("/tickets?search=dev@company.com", headers=headers)
    assert resp.status_code == 200
    
    root_search = resp.json()
    assert len(root_search["data"]) == 1
    assert root_search["data"][0]["customer_name"] == "Alice Developer"
    
    # Search by subject
    resp = client.get("/tickets?subject=billing", headers=headers)
    assert resp.status_code == 200
    
    root_subject = resp.json()
    assert len(root_subject["data"]) == 1
    assert root_subject["data"][0]["customer_name"] == "Charlie Manager"

    # Search using a wildcard character "%" that should be escaped and return 0 matches
    resp = client.get("/tickets?search=%", headers=headers)
    assert resp.status_code == 200
    root_wildcard = resp.json()
    assert len(root_wildcard["data"]) == 0

