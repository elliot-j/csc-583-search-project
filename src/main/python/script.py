from flask import Flask, request

app = Flask(__name__)

@app.route('/hello', methods=['POST', 'GET'])
def index():
   if request.method == 'POST':
      value1 = request.form.get('value1')
      value2 = request.form.get('value2')
      return 'OK'
   else:
      return 'Use POST requests'

if __name__ == '__main__':
    #app.debug = True
    app.run(host='0.0.0.0', port=8000)