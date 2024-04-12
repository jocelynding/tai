from pytube import Playlist, YouTube
import os
from moviepy.editor import AudioFileClip
from VideoProcess import process_video_scenes
from TranscriptProcess import transcribe_audio_with_whisper
import tiktoken
import openai
import pickle
def title_with_chat_completion(model, text):
    if model == 'local' or model == 'zephyr':
        openai.api_key = "empty"
        openai.api_base = "http://localhost:8000/v1"
    elif model == 'openai':
        openai.api_key = os.getenv("OPENAI_API_KEY")
    system_prompt = "Generate a title for the following text. Only give one title."
    # Construct the messages list with the current system prompt, documents, and user question
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": f"text:{text}"
        },
    ]

    # Get the response from OpenAI's model for the current set of messages
    openai_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )

    # Add the response to the responses list

    return openai_response["choices"][0]["message"]["content"]
def convert_mp4_to_wav(mp4_path, wav_path):
    audio_clip = AudioFileClip(mp4_path)  # Load the audio track from the MP4 file
    audio_clip.write_audiofile(wav_path)  # Save the audio as a WAV file
    audio_clip.close()  # Close the clip to free resources

def token_size(sentence):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    return len(encoding.encode(sentence))
def get_playlist_urls(playlist_url):
    playlist = Playlist(playlist_url)
    return list(playlist.video_urls)

def process_paragraphs(paragraphs):
    for i in range(len(paragraphs) - 1):
        # Check if the current paragraph does not end with a period
        if not paragraphs[i].endswith('.'):
            # Split the next paragraph into sentences
            sentences = paragraphs[i + 1].split('.')
            # Append the first sentence from the next paragraph to the current one
            paragraphs[i] += ' ' + sentences[0] + '.'
            # Join the remaining sentences with a period, adding a period at the start if there are remaining sentences
            if len(sentences) > 1:
                paragraphs[i + 1] = '.'.join(sentences[1:])
                # Add a leading period to the joined string if it's not empty
                if paragraphs[i + 1]:
                    paragraphs[i + 1] = '.' + paragraphs[i + 1]
            else:
                paragraphs[i + 1] = ''
    return paragraphs

def download_videos(video_urls, base_path):
    for url in video_urls:
        video = YouTube(url)
        stream = video.streams.get_highest_resolution()

        # Create a unique folder for each video based on its title
        safe_title = "".join(x for x in video.title if x.isalnum() or x in " -_").strip()
        video_path = os.path.join(base_path, safe_title)
        os.makedirs(video_path, exist_ok=True)

        download_filename = stream.download(output_path=video_path)

        # Construct WAV filename in the same unique folder
        wav_filename = os.path.join(video_path, os.path.splitext(os.path.basename(download_filename))[0] + '.wav')

        # Convert to WAV
        convert_mp4_to_wav(download_filename, wav_filename)

def paragraph_generator(transcript, seg_time):
    paragraphs = []
    for seg_start, seg_end in seg_time:
        paragraph = []
        for chunk in transcript:
            if chunk['start'] >= seg_start and chunk['end'] <= seg_end:
                paragraph.append(chunk['text'])
        paragraphs.append((paragraph, seg_start))
    return paragraphs
def save_content_to_pkl(dict_list, filename='filename.pkl'):
    with open(filename, 'wb') as file:
        pickle.dump(dict_list, file)
def process_video_audio(base_dir, video_urls):
    for (root, dirs, files), video_url in zip(os.walk(base_dir), video_urls):
        if not files:
            continue
        dict_list = []
        folder = os.path.basename(root)
        print(f"Traversing Folder: {folder}")
        video = None
        audio = None
        for file in files:
            if file.endswith('.mp4'):
                video = file  # Store the MP4 filename
            elif file.endswith('.wav'):
                audio = file  # Store the WAV filename

        if video is not None and audio is not None:
            video_path = os.path.join(root, video)
            audio_path = os.path.join(root, audio)
            print(video_path)
            print(audio_path)

            seg_time = process_video_scenes(video_path)
            transcript = transcribe_audio_with_whisper(audio_path)
            print(seg_time)
            print(transcript)

            paragraphs = paragraph_generator(transcript, seg_time)
            for i, time in paragraphs:
                paragraph = ''.join(i)
                if paragraph:
                    title = title_with_chat_completion("zephyr", paragraph)
                    print(int(time))
                    print(paragraph)
                    print(token_size(paragraph))
                    print("-------------------")
                    print(title)
                    print("-------------------")
                    print(f"url = {video_url}&t={int(time)}s")
                    dict_list.append({'Page_table': '', 'Page_path': title, 'Segment_print': paragraph, 'url': video_url, 'time': int(time)})
            print(root)
            print(os.getcwd())
            save_path = os.path.join(root, f'{folder}_content.pkl')
            print(f"content saved to: {save_path}")
            save_content_to_pkl(dict_list, save_path)
    else:
            print(f"No video or audio files found in {root}. Skipping.")



# Example usage
base_path = 'Denero'
os.makedirs(base_path, exist_ok=True)
playlist_url = 'https://www.youtube.com/watch?v=31EDjrN1x5k&list=PL6BsET-8jgYUA8ryM_zeRA3H_RAMNBrN3&ab_channel=JohnDeNero'
video_urls = get_playlist_urls(playlist_url)

download_videos(video_urls, base_path)
process_video_audio(base_path, video_urls)
