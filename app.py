from flask import Flask, render_template, request, send_file
from pytube import YouTube
import io

app = Flask(__name__)

@app.route('/download_video', methods=['GET'])
def download_video():
    buffer= io.BytesIO()
    # Get the YouTube video URL from the form
    video_url = 'https://www.youtube.com/watch?v=_DDg0urz9NU&t=1s'

    # Download the video using pytube
    yt = YouTube(video_url)
    stream = yt.streams.get_by_itag(251)

    # Get the video content as bytes
    stream.stream_to_buffer(buffer)
    buffer.seek(0)
    # Create an in-memory file-like object
    # in_memory_file = io.BytesIO(video_content)

    # Serve the in-memory file as a response
    return send_file(buffer, as_attachment=True, download_name='video.mp4', mimetype='video/mp4')

if __name__ == '__main__':
    app.run(debug=True)