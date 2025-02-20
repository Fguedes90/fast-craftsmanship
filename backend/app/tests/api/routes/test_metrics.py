from fastapi.testclient import TestClient
import pytest
from app.main import app, APP_NAME
from fastapi import Request, Response
from app.observability import PrometheusMiddleware

# Add test endpoints for error simulation
@app.get("/trigger-500", tags=["test-endpoints"])
async def trigger_500():
    from fastapi import HTTPException
    raise HTTPException(status_code=500, detail="Internal server error simulation")

@app.get("/trigger-403", tags=["test-endpoints"])
async def trigger_403():
    return Response(status_code=403)

client = TestClient(app)

def test_metrics_endpoint():
    """Test if metrics endpoint returns 200 and correct content type"""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; version=0.0.4; charset=utf-8"

def test_app_info_metric():
    """Test if app_info metric is present"""
    response = client.get("/metrics")
    assert f'fastapi_app_info{{app_name="{APP_NAME}"}}' in response.text

@pytest.mark.asyncio
async def test_request_counter():
    """Test if requests are counted correctly"""
    # Make a request to trigger the counter
    response = client.get("/api/v1/docs")
    
    # Get metrics
    metrics_response = client.get("/metrics")
    
    # Check if request was counted
    assert 'fastapi_requests_total{' in metrics_response.text
    assert 'method="GET"' in metrics_response.text

@pytest.mark.asyncio
async def test_request_in_progress():
    """Test if requests in progress are tracked correctly"""
    # Make a request to check in-progress metrics
    response = client.get("/api/v1/docs")
    
    # Get metrics
    metrics_response = client.get("/metrics")
    
    # Verify requests_in_progress metric exists
    assert 'fastapi_requests_in_progress{' in metrics_response.text

@pytest.mark.asyncio
async def test_request_processing_time():
    """Test if request processing time is being measured"""
    # Make a request to measure processing time
    response = client.get("/api/v1/docs")
    
    # Get metrics
    metrics_response = client.get("/metrics")
    
    # Verify processing time metric exists
    assert 'fastapi_requests_duration_seconds_bucket{' in metrics_response.text

@pytest.mark.asyncio
async def test_response_status_counter():
    """Test if response status codes are counted correctly"""
    # Make a request
    response = client.get("/api/v1/docs")
    
    # Get metrics
    metrics_response = client.get("/metrics")
    
    # Verify response counter metric exists
    assert 'fastapi_responses_total{' in metrics_response.text
    assert f'status_code="{response.status_code}"' in metrics_response.text

@pytest.mark.asyncio
async def test_exception_counter():
    """Test if exceptions are counted correctly"""
    # Make a request to a non-existent endpoint to trigger 404
    response = client.get("/non-existent-path")
    
    # Get metrics
    metrics_response = client.get("/metrics")
    
    # Verify that the 404 response was counted
    assert 'fastapi_responses_total{' in metrics_response.text
    assert 'status_code="404"' in metrics_response.text

@ pytest.mark.asyncio
async def test_exception_counter_500():
    """Test if 500 exceptions are counted correctly"""
    # Trigger a 500 error using a dedicated endpoint
    response = client.get("/trigger-500")

    # Get metrics
    metrics_response = client.get("/metrics")

    # Verify that the 500 response was counted
    assert 'fastapi_responses_total{' in metrics_response.text
    assert 'status_code="500"' in metrics_response.text


@ pytest.mark.asyncio
async def test_exception_counter_403():
    """Test if 403 exceptions are counted correctly"""
    # Trigger a 403 error using a dedicated endpoint
    response = client.get("/trigger-403")

    # Get metrics
    metrics_response = client.get("/metrics")

    # Verify that the 403 response was counted
    assert 'fastapi_responses_total{' in metrics_response.text
    assert 'status_code="403"' in metrics_response.text

def test_prometheus_middleware_path_matching():
    """Test the path matching functionality of PrometheusMiddleware"""
    middleware = PrometheusMiddleware(app)
    client = TestClient(app)
    
    # Test with existing endpoint
    response = client.get("/metrics")
    assert response.status_code == 200
    
    # Test with non-existent endpoint
    response = client.get("/non-existent")
    assert response.status_code == 404
