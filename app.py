from flask import Flask, Response, request, render_template
from pytube import YouTube
from pytube.exceptions import RegexMatchError
# import requests, json
import urllib.parse
import mimetypes
import io

app = Flask(__name__)


@app.route("/", methods=["GET","POST"])
def index():
    global yt
    global details
    mesage = ''
    errorType = 0
    if request.method == 'POST' and 'video_url' in request.form:
        
        video_url = request.form["video_url"]
        try:
            yt = YouTube(video_url)
            details = {
                "title" : yt.title,
                "thumb" : yt.thumbnail_url,
                "author": yt.author,
                "length": f"{yt.length//60}m{(yt.length%(60))%60}s"
            }
            # stream = yt.streams.get_by_itag(22)
            video_streams = yt.streams.filter(progressive=True)
            audio_streams = yt.streams.filter(only_audio=True)
            stream_info = []
            for str in video_streams:
                # Convert file size to MB

                size_mb = str.filesize / (1024 * 1024)
                # Append resolution and size (in MB) to the list
                stream_info.append({"res": f"MP4 {str.resolution} ({'{:.1f}'.format(size_mb)}MB)", 'itag': str.itag})

            for audio_stream in audio_streams:
                # Convert file size to MB
                size_mb = audio_stream.filesize / (1024 * 1024)
                # Append resolution and size (in MB) to the list
                stream_info.append({"res": f"MP3 {audio_stream.abr} ({'{:.1f}'.format(size_mb)}MB)", 'itag': audio_stream.itag})

            return render_template('youtube.html', options = stream_info, details = details)
        except RegexMatchError:
            mesage = 'URL Error!'
            errorType = 0
    return render_template('index.html', mesage = mesage, errorType = errorType) 


@app.route("/download", methods=["GET","POST"])
def downloadVideo():
    mesage = ''
    errorType = 0
    if request.method == 'POST' and 'dropdown' in request.form:
        itag = request.form["dropdown"]
        try:
            if(itag):
                
                buffer = io.BytesIO()
                stream = yt.streams.get_by_itag(itag)
                filename = stream.default_filename
                file_extension = filename.split('.')[-1]

                if stream.mime_type.startswith('video/'):
                    mimetype = mimetypes.types_map.get('.mp4', 'application/octet-stream')
                    file_name = filename.split('.')[0]+".mp4"
                elif stream.mime_type.startswith('audio/'):
                    mimetype = mimetypes.types_map.get('.mp3', 'application/octet-stream')
                    file_name = filename.split('.')[0]+".mp3"
                else:
                    mimetype = mimetypes.types_map.get(f'.{file_extension}', 'application/octet-stream')
                    file_name = filename

                stream.stream_to_buffer(buffer)
                buffer.seek(0)
                
                # Function to generate video stream chunks
                def generate():
                    while True:
                        # Read chunk of video data
                        chunk = buffer.read(5*1024*1024)
                        if not chunk:
                            break
                        yield chunk
                
                # Return response with video stream using chunked transfer encoding
                encoded_filename = urllib.parse.quote(file_name)
                return Response(generate(), mimetype=mimetype, headers={'Content-Disposition': f'attachment; filename={encoded_filename}'})
            else:
                mesage = 'No Video/Audio for Selected Resolution'
                errorType = 0
        except:
            return render_template('index.html', mesage = mesage, errorType = errorType) 
    return render_template('index.html', mesage = mesage, errorType = errorType) 

# if __name__ == '__main__':
#     app.run(debug=True)