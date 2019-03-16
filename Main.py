from flask import Flask, request, Response







@app.route('/', methods=['POST'])
def incoming():
    

    return Response(status=200)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=443, debug=True)