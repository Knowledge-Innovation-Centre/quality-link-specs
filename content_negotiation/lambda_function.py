import json
import os
import re

def lambda_handler(event, context):
    """
    Lambda function to handle content negotiation for ontology resources.
    
    - Redirects to specs.quality-link.eu/{path}.html for browser requests
    - Redirects to specs.quality-link.eu/resources/{path}.ttl for semantic web clients
    """
    # Get the Accept header from the request
    request_headers = event.get('headers', {})
    accept_header = request_headers.get('Accept', '') or request_headers.get('accept', '')
    
    # Define our content types and preferences
    html_types = ['text/html', '*/*']
    semantic_web_types = ['text/turtle', 'application/rdf+xml', 'application/n-triples', 
                         'application/ld+json', 'application/rdf+json']
    
    # Get the requested path from the event
    path = ""
    
    # Extract path from different possible event structures
    if 'pathParameters' in event and event['pathParameters']:
        path = event['pathParameters'].get('proxy', '')
    elif 'path' in event:
        # Remove leading slash if present
        path = event['path'].lstrip('/')
    elif 'resource' in event and '{proxy+}' in event['resource'] and 'pathParameters' in event:
        path = event['pathParameters'].get('proxy', '')
    
    # Remove any trailing slashes
    path = path.rstrip('/')
    
    # If no path is found, default to root
    if not path:
        path = "ontology"  # Default path
    
    # Base URLs
    specs_base_url = os.environ.get('SPECS_BASE_URL', 'https://specs.quality-link.eu')
    
    # URLs for redirects
    ttl_url = f"{specs_base_url}/resources/{path}.ttl"
    html_url = f"{specs_base_url}/{path}.html"
    
    # Default response headers with CORS
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type,Accept'
    }
    
    # Simple browser detection
    user_agent = request_headers.get('User-Agent', '') or request_headers.get('user-agent', '')
    common_browsers = ['Mozilla', 'Chrome', 'Safari', 'Edge', 'MSIE', 'Firefox']
    
    is_browser_request = any(html_type in accept_header for html_type in html_types) or \
                         any(browser in user_agent for browser in common_browsers)
    
    # Semantic web client detection
    is_semantic_web_client = any(sw_type in accept_header for sw_type in semantic_web_types)
    
    # Handle OPTIONS requests for CORS
    if event.get('httpMethod', '') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    # Set default status code for redirects
    status_code = 303  # See Other
    
    # Serve the appropriate content based on the request
    if is_semantic_web_client and not is_browser_request:
        # For semantic web clients, redirect to the TTL file
        headers['Location'] = ttl_url
    else:
        # For browsers, redirect to the HTML page
        headers['Location'] = html_url
    
    # Log request details for debugging (will appear in CloudWatch)
    print(f"Path: {path}")
    print(f"Accept header: {accept_header}")
    print(f"User agent: {user_agent}")
    print(f"Redirecting to: {headers.get('Location')}")
    
    # Return the redirect response
    return {
        'statusCode': status_code,
        'headers': headers,
        'body': ''
    }