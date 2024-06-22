from flask import Flask, request, jsonify, send_from_directory
from pytube import YouTube
import os
import subprocess

app = Flask(__name__)

def combine_audio_video(video_path, audio_path, output_path):
    command = f'ffmpeg -i "{video_path}" -i "{audio_path}" -c:v copy -c:a aac "{output_path}"'
    subprocess.run(command, shell=True)

@app.route('/')
def index():
    return send_from_directory('', 'index.html')

@app.route('/download', methods=['POST'])
def download_video():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        yt = YouTube(url)
        video_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True).order_by('resolution').desc().first()
        audio_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).order_by('abr').desc().first()

        video_path = video_stream.download(filename='video.mp4')
        audio_path = audio_stream.download(filename='audio.mp4')

        output_filename = yt.title + '.mp4'
        output_path = os.path.join('downloads', output_filename)
        combine_audio_video(video_path, audio_path, output_path)

        os.remove(video_path)
        os.remove(audio_path)

        return jsonify({"message": "Download successful", "filename": output_filename}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(host='0.0.0.0', port=5000)
