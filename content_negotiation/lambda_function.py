import json
import os
import re

path_map = {
    'ontology/v1': {
        'text/turtle':          'resources/ontology-shacl.ttl',
        'application/rdf+xml':  'resources/ontology-shacl.rdf',
        'text/xml':             'resources/ontology-shacl.rdf',
        'application/ld+json':  'resources/ontology-shacl.json',
        'application/json':     'resources/ontology-shacl.json',
        'text/html':            'resources/ontology-shacl.html',
        'text/plain':           'resources/ontology-shacl.ttl',
        '*/*':                  'resources/ontology-shacl.html',
    }
}

def lambda_handler(event, context):
    """
    Lambda function to handle content negotiation for ontology resources.
    
    - Redirects to specs.quality-link.eu/{path} according to map
    """
    # Get the Accept header from the request
    request_headers = event.get('headers', {})
    accept_header = request_headers.get('Accept', '') or request_headers.get('accept', '')
    
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
    
    # Base URLs
    specs_base_url = os.environ.get('SPECS_BASE_URL', 'https://specs.quality-link.eu')

    # Default response headers with CORS
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type,Accept'
    }
    body = ''
    
    # Handle OPTIONS requests for CORS
    if event.get('httpMethod', '') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }

    if path in path_map:
        # default target if available
        if '*/*' in path_map[path]:
            status_code = 303
            headers['Location'] = f"{specs_base_url}/{path_map[path]['*/*']}"
        else:
            status_code = 406
            body = 'No agreeable content type found.'
        # negotiate content type to deliver
        for content_type in path_map[path]:
            if content_type in accept_header:
                status_code = 303
                headers['Location'] = f"{specs_base_url}/{path_map[path][content_type]}"
                body = ''
                break
    else:
        # pass through unknown paths
        status_code = 303
        headers['Location'] = f"{specs_base_url}/{path}"

    # Log request details for debugging (will appear in CloudWatch)
    print(f"Path: {path}")
    print(f"Accept header: {accept_header}")
    print(f"Redirecting to: {headers.get('Location', '-- n/a --')}")
    
    # Return the redirect response
    return {
        'statusCode': status_code,
        'headers': headers,
        'body': body
    }

