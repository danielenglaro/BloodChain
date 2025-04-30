from app import create_app

connection = mysql.connector.connect(host='localhost', port='3307', database='BloodBase', user='root', password='polpetta')
cursor = connection.cursor()
app.secret_key = "AlessioSvejate"
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)