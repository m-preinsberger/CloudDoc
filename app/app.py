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
        # List files in the uploads directory
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        return render_template('index.html', files=files)

    @app.route('/delete', methods=['POST'])
    def delete_file():
        file_name = request.json.get('file_name')
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
            return jsonify({'success': f'File {file_name} deleted successfully'}), 200
        return jsonify({'error': 'File not found'}), 404

    @app.route('/commit', methods=['POST'])
    def commit_files():
        zip_path = os.path.join(app.instance_path, 'uploads.zip')
        shutil.make_archive(zip_path.replace('.zip', ''), 'zip', app.config['UPLOAD_FOLDER'])
        return jsonify({'download_url': '/download/uploads.zip'})

    @app.route('/download/<filename>', methods=['GET'])
    def download_file(filename):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        return jsonify({'error': 'File not found'}), 404


    @app.route('/upload', methods=['POST'])
    def upload_file():
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        files = request.files.getlist('file')
        for file in files:
            if file.filename == '':
                continue
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        return jsonify({'success': 'Files uploaded successfully'}), 200

    @app.route('/files', methods=['GET'])
    def get_files():
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        return jsonify({'files': files})


    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
