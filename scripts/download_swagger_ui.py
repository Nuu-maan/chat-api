import os
import requests
import shutil

def download_file(url, filename):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(filename, 'wb') as f:
        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, f)

def main():
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)

    # Swagger UI files to download
    files = {
        'https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.11.0/swagger-ui-bundle.js': 'static/swagger-ui-bundle.js',
        'https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.11.0/swagger-ui.css': 'static/swagger-ui.css',
        'https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.11.0/favicon-32x32.png': 'static/favicon.png',
    }

    # Download each file
    for url, filename in files.items():
        print(f'Downloading {filename}...')
        download_file(url, filename)

    print('All files downloaded successfully!')

if __name__ == '__main__':
    main() 