from app import create_app

app = create_app()

if __name__ == "__main__":
    #host="192.168.236.232"
    #host="192.168.1.14"
    app.run(host="192.168.236.232", port=5000, debug=True)