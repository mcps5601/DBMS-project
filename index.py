from flask import Flask, request, render_template
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'debian-sys-maint'
app.config['MYSQL_PASSWORD'] = 'dean5601'
app.config['MYSQL_DB'] = 'dbmsproject'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template("index.html")
    if request.method == "POST":
        details = request.form
        option = request.form['search_options']
        if option == 'ID':
            cur = mysql.connection.cursor()
            if request.form['keywords']=='all':
                cur.execute("SELECT * FROM users, cost WHERE users.id=cost.userid")
            else:
                cur.execute("SELECT * FROM users, cost WHERE users.id=cost.userid AND users.id={}".format(int(request.form['keywords'])))
            results = cur.fetchall()

        if option == 'Username':
            cur = mysql.connection.cursor()
            if request.form['keywords']=='all':
                cur.execute("SELECT * FROM users, cost WHERE users.id=cost.userid")
            else:
                cur.execute("SELECT * FROM users, cost WHERE users.id=cost.userid AND users.username='{}'".format(str(request.form['keywords'])))
            results = cur.fetchall()

        if option == 'Nickname':
            cur = mysql.connection.cursor()
            if request.form['keywords']=='all':
                cur.execute("SELECT * FROM users, cost WHERE users.id=cost.userid")
            else:
                cur.execute("SELECT * FROM users, cost WHERE users.id=cost.userid AND users.nickname='{}'".format(str(request.form['keywords'])))
            results = cur.fetchall()
        output_text = []
        output_text.append(results[0].keys())
        for i in range(len(results)):
            tmp = []
            for j in results[0].keys():
                tmp.append(results[i][j])
            output_text.append(tmp)
        #return render_template('index.html', output_text=results)
        return render_template('index.html', output_text=output_text, search_options=option)

@app.route("/sql", methods=['GET', 'POST'])
def sql():
    if request.method == 'GET':
        return render_template('sql.html')

@app.route("/new", methods=['GET', 'POST'])
def new():
    if request.method == 'GET':
        return render_template('new.html')

@app.route("/new_user", methods=['GET', 'POST'])
def new_user():
    if request.method == 'GET':
        return render_template('new_user.html')
    if request.method == "POST":
        userid = request.form["id"]
        username = request.form["username"]
        nickname = request.form["nickname"]

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(id, username, nickname) VALUES (%s, %s, %s)", (userid, username, nickname))
        mysql.connection.commit()
        cur.close()
        output_text = 'Success!'
        return render_template('new_user.html', output_text=output_text)

@app.route("/new_cost", methods=['GET', 'POST'])
def new_cost():
    if request.method == 'GET':
        return render_template('new_cost.html')
    if request.method == "POST":
        record_number = request.form["record_number"]
        userid = request.form["id"]
        price = request.form["price"]
        item = request.form["item"]

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO cost(record_number, userid, price, item) VALUES (%s, %s, %s, %s)", (record_number, userid, price, item))
        mysql.connection.commit()
        cur.close()
        output_text = 'Success!'
        return render_template('new_cost.html', output_text=output_text)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
