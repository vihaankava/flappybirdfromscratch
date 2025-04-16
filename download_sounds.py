import os
import requests
import json
from urllib.parse import quote_plus

# Create sounds directory if it doesn't exist
os.makedirs('sounds', exist_ok=True)

# Freesound API key (you can get one by registering at https://freesound.org/apiv2/apply/)
API_KEY = "YOUR_API_KEY"  # Replace with your API key

# Sound effects to download
sounds_to_download = {
    'jump.wav': 'flap wing bird',
    'score.wav': 'point collect',
    'collision.wav': 'thud impact',
    'game_over.wav': 'game over fail'
}

def download_sound(query, filename):
    # Search for sounds
    search_url = f"https://freesound.org/apiv2/search/text/?query={quote_plus(query)}&token={API_KEY}"
    response = requests.get(search_url)
    
    if response.status_code == 200:
        results = response.json()
        if results['count'] > 0:
            # Get the first result
            sound_id = results['results'][0]['id']
            
            # Get the sound file URL
            sound_url = f"https://freesound.org/apiv2/sounds/{sound_id}/?token={API_KEY}"
            sound_response = requests.get(sound_url)
            
            if sound_response.status_code == 200:
                sound_data = sound_response.json()
                download_url = sound_data['previews']['preview-hq-mp3']
                
                # Download the sound
                sound_file = requests.get(download_url)
                if sound_file.status_code == 200:
                    with open(f'sounds/{filename}', 'wb') as f:
                        f.write(sound_file.content)
                    print(f"Downloaded {filename}")
                    return True
    
    print(f"Failed to download {filename}")
    return False

def main():
    print("Downloading sound effects...")
    for filename, query in sounds_to_download.items():
        download_sound(query, filename)
    print("Done!")

if __name__ == "__main__":
    main() 