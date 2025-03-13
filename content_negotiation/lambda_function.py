import json
import os
import re

# Function to create path mappings for different content types
def create_resource_map(base_name):
    """
    Create a map of content types to resource paths for a given base name.
    HTML files are placed at the root, other formats in resources/ directory.
    
    Args:
        base_name (str): The base name for the resource files
        
    Returns:
        dict: Mapping of content types to resource paths
    """
    return {
        'text/turtle':          f'resources/{base_name}.ttl',
        'application/rdf+xml':  f'resources/{base_name}.rdf',
        'text/xml':             f'resources/{base_name}.rdf',
        'application/ld+json':  f'resources/{base_name}.json',
        'application/json':     f'resources/{base_name}.json',
        'text/html':            f'{base_name}.html',  # HTML at root
        'text/plain':           f'resources/{base_name}.ttl',
        '*/*':                  f'{base_name}.html',  # Default is HTML at root
    }

# Path to resource mappings
# The key is the URL path, the value is a dictionary of content types
# 
# IMPORTANT: To add a new path mapping, add a new entry to this dictionary.
# For example, to map 'new/path' to files named 'new-resource':
#   'new/path': create_resource_map('new-resource')
#
# This will automatically create mappings for all supported content types:
# - HTML file at root: new-resource.html
# - Other formats in resources/: resources/new-resource.ttl, resources/new-resource.json, etc.
path_map = {
    # This maps the URL path 'ontology/v1' to files with base name 'ontology-shacl'
    'ontology/v1': create_resource_map('ontology-shacl'),
    
    # Add more mappings below as needed
}

# Function to get base name from path for unknown paths
def get_base_name_from_path(path):
    """
    Extract a base name from a path to use for unknown paths.
    
    Args:
        path (str): The path to extract a base name from
        
    Returns:
        str: The extracted base name
    """
    # Get the last part of the path
    parts = path.split('/')
    return parts[-1] if parts else path

def lambda_handler(event, context):
    """
    Lambda function to handle content negotiation for ontology resources.
    
    - Maps known paths to their resources according to content type
    - For unknown paths, redirects to [path].html
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
        # Known path - use the configured mapping
        # Set default target if available
        if '*/*' in path_map[path]:
            status_code = 303
            headers['Location'] = f"{specs_base_url}/{path_map[path]['*/*']}"
        else:
            status_code = 406
            body = 'No agreeable content type found.'
            
        # Content negotiation - check for specific content type matches
        for content_type in path_map[path]:
            if content_type in accept_header:
                status_code = 303
                headers['Location'] = f"{specs_base_url}/{path_map[path][content_type]}"
                body = ''
                break
    else:
        # Unknown path - redirect to [path].html
        status_code = 303
        base_name = get_base_name_from_path(path)
        
        # For unknown paths, we can either:
        # 1. Simply append .html to the path
        headers['Location'] = f"{specs_base_url}/{path}.html"
        
        # 2. Or we could dynamically choose based on Accept header (optional)
        # This would allow content negotiation for unknown paths too
        if 'text/html' in accept_header or '*/*' in accept_header:
            headers['Location'] = f"{specs_base_url}/{path}.html"
        elif 'text/turtle' in accept_header:
            headers['Location'] = f"{specs_base_url}/resources/{path}.ttl"
        elif 'application/json' in accept_header or 'application/ld+json' in accept_header:
            headers['Location'] = f"{specs_base_url}/resources/{path}.json"
        elif 'application/rdf+xml' in accept_header or 'text/xml' in accept_header:
            headers['Location'] = f"{specs_base_url}/resources/{path}.rdf"
        
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