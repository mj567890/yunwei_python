from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/test/import', methods=['POST'])
def test_import():
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400
        
        # 简单读取文件内容
        content = file.read()
        return jsonify({
            'success': True,
            'message': f'收到文件: {file.filename}',
            'size': len(content)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test/status', methods=['GET'])
def test_status():
    return jsonify({'status': 'ok', 'routes': ['/test/import', '/test/status']})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)