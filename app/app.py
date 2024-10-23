import os
import shutil
from flask import Flask, request, jsonify, render_template, send_file

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        UPLOAD_FOLDER=os.path.join(app.instance_path, 'uploads'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    try:
        os.makedirs(app.config['UPLOAD_FOLDER'])
    except OSError:
        pass

    uploaded_files = []

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/upload', methods=['POST'])
    def upload_file():
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            uploaded_files.append(filename)
            return jsonify({'success': 'File uploaded successfully'}), 200

    @app.route('/files', methods=['GET'])
    def get_files():
        return jsonify({'files': uploaded_files})

    @app.route('/commit', methods=['POST'])
    def commit_files():
        zip_path = os.path.join(app.instance_path, 'uploads.zip')
        shutil.make_archive(zip_path.replace('.zip', ''), 'zip', app.config['UPLOAD_FOLDER'])
        return jsonify({'download_url': '/download/uploads.zip'})

    @app.route('/download/<filename>', methods=['GET'])
    def download_file(filename):
        file_path = os.path.join(app.instance_path, filename)
        return send_file(file_path, as_attachment=True)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)