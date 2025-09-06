from flask import Flask, render_template, request, jsonify, send_file
from pydub import AudioSegment
import sqlite3
import os
import json
from config import COLORS, SIZES, LAYOUT, AUDIO

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Create uploads directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
def init_db():
    conn = sqlite3.connect('songs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS songs
                 (id INTEGER PRIMARY KEY, title TEXT, lyrics TEXT, 
                  notes TEXT, audio_files TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html', 
                         colors=COLORS, 
                         sizes=SIZES, 
                         layout=LAYOUT)

@app.route('/upload', methods=['POST'])
def upload_files():
    files = request.files.getlist('audio_files')
    uploaded = []
    
    for file in files:
        if file.filename:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            uploaded.append({
                'name': filename,
                'path': filepath,
                'size': os.path.getsize(filepath)
            })
    
    return jsonify({'success': True, 'files': uploaded})

@app.route('/splice', methods=['POST'])
def splice_audio():
    data = request.json
    file_list = data.get('files', [])
    
    combined = AudioSegment.empty()
    
    for file_path in file_list:
        if os.path.exists(file_path):
            try:
                audio = AudioSegment.from_file(file_path)
                combined += audio
            except Exception as e:
                return jsonify({'error': f'Error processing {file_path}: {str(e)}'})
    
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'spliced_output.mp3')
    combined.export(output_path, format="mp3")
    
    return jsonify({'success': True, 'output_file': output_path})

@app.route('/save_song', methods=['POST'])
def save_song():
    data = request.json
    
    conn = sqlite3.connect('songs.db')
    c = conn.cursor()
    c.execute("INSERT INTO songs (title, lyrics, notes, audio_files) VALUES (?, ?, ?, ?)",
              (data['title'], data['lyrics'], data['notes'], json.dumps(data['audio_files'])))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
