from flask import Flask, request, render_template, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'dean'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'debian-sys-maint'
app.config['MYSQL_PASSWORD'] = 'dean5601'
app.config['MYSQL_DB'] = 'dbmsproject'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route("/", methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'GET':
        return render_template("login.html")
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password,))
        users = cursor.fetchone()
        if users:
            session['loggedin'] = True
            session['id'] = users['id']
            session['username'] = users['username']
            #return 'Logged in successfully!'
            return render_template('index.html', display_name=session['username'])

@app.route("/logout", methods=['GET'])
def logout():
    if request.method == 'GET':
        session.pop('loggedin', None)
        session.pop('id', None)
        session.pop('username', None)
        return 'Log out successfully!'


@app.route("/index", methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template("index.html", display_name=session['username'])
        #return render_template("login.html")
    if request.method == "POST":
        details = request.form
        option = request.form['search_options']
        if option == 'ID':
            cur = mysql.connection.cursor()
            if request.form['keywords']=='all':
                cur.execute("SELECT `userid`, `username`, `record_number`, `price`, `item` FROM users, cost WHERE users.id=cost.userid")
            else:
                cur.execute("SELECT `userid`, `username`, `record_number`, `price`, `item` FROM users, cost WHERE users.id=cost.userid AND users.id={}".format(int(request.form['keywords'])))
            results = cur.fetchall()

        if option == 'Username':
            cur = mysql.connection.cursor()
            if request.form['keywords']=='all':
                cur.execute("SELECT `userid`, `username`, `record_number`, `price`, `item` FROM users, cost WHERE users.id=cost.userid")
            else:
                cur.execute("SELECT `userid`, `username`, `record_number`, `price`, `item` FROM users, cost WHERE users.id=cost.userid AND users.username='{}'".format(str(request.form['keywords'])))
            results = cur.fetchall()

        if option == 'Nickname':
            cur = mysql.connection.cursor()
            if request.form['keywords']=='all':
                cur.execute("SELECT `userid`, `username`, `record_number`, `price`, `item` FROM users, cost WHERE users.id=cost.userid")
            else:
                cur.execute("SELECT `userid`, `username`, `record_number`, `price`, `item` FROM users, cost WHERE users.id=cost.userid AND users.nickname='{}'".format(str(request.form['keywords'])))
            results = cur.fetchall()
        output_text = []
        col_names = results[0].keys()
        new_col = 'actions'
        #output_text.append(results[0].keys())
        for i in range(len(results)):
            tmp = []
            for j in col_names:
                tmp.append(results[i][j])
            output_text.append(tmp)
        #return render_template('index.html', output_text=results)
        return render_template('index.html', display_name=session['username'], output_text=output_text, col_names=col_names, search_options=option, new_col=new_col)

@app.route("/sql", methods=['GET', 'POST'])
def sql():
    if request.method == 'GET':
        return render_template('sql.html')
    if request.method == "POST":
        input_text = request.form['input_text']
        cur = mysql.connection.cursor()
        cur.execute("{}".format(input_text))
        results = cur.fetchall()

        output_text = []
        output_text.append(results[0].keys())
        for i in range(len(results)):
            tmp = []
            for j in results[0].keys():
                tmp.append(results[i][j])
            output_text.append(tmp)
        
        return render_template('sql.html', input_text=input_text, output_text=output_text)

@app.route("/del", methods=['GET', 'POST'])
def delete():
    if request.method == 'GET':
        return 'Hello'
    if request.method == "POST":
        cur = mysql.connection.cursor()
        print("DELETE FROM cost WHERE cost.record_number={};".format(int(request.data)))
        cur.execute("DELETE FROM `cost` WHERE cost.record_number={};".format(int(request.data)))
        mysql.connection.commit()
        cur.close()
        return 'Good'

@app.route("/new", methods=['GET', 'POST'])
def new():
    if request.method == 'GET':
        return render_template('new.html')

@app.route("/new_user", methods=['GET', 'POST'])
def new_user():
    if request.method == 'GET':
        return render_template('new_user.html')

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        nickname = request.form["nickname"]
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(id) FROM `users`;")
        number = cur.fetchone().get('COUNT(id)')
        print("Number:", number)
        userid = number+1

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(id, username, nickname, password) VALUES (%s, %s, %s, %s)", (userid, username, nickname, password))
        mysql.connection.commit()
        cur.close()
        output_text = 'Success!'
        return render_template('new_user.html', output_text=output_text)

@app.route("/new_cost", methods=['GET', 'POST'])
def new_cost():
    if request.method == 'GET':
        return render_template('new_cost.html')
    if request.method == "POST":
        userid = session['id']
        price = request.form["price"]
        item = request.form["item"]
        editer = request.form["editer"]
        cur = mysql.connection.cursor()
        cur.execute("SELECT MAX(record_number) FROM `cost`;")
        record_number = cur.fetchone().get('MAX(record_number)') + 1
        #print(results)
        #print(cur.fetchone()['record_number'])

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO cost(record_number, userid, price, item, edit_userid) VALUES (%s, %s, %s, %s, %s)", (record_number, userid, price, item, editer))
        mysql.connection.commit()
        cur.close()
        output_text = 'Success!'
        return render_template('new_cost.html', output_text=output_text)

@app.route("/purchase", methods=['GET', 'POST'])
def purchase():
    if request.method == 'GET':
        return render_template('purchase.html')
    if request.method == "POST":
        userid = session['id']
        record_number = request.form["record_number"]
        date = request.form["date"]
        place = request.form["place"]

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO purchase_info(record_number, purchase_date, place) VALUES (%s, %s, %s)", (record_number, date, place))
        mysql.connection.commit()
        cur.close()
        output_text = 'Success!'
        return render_template('purchase.html', output_text=output_text)

@app.route("/item", methods=['GET', 'POST'])
def new_item():
    if request.method == 'GET':
        return render_template('item.html')
    if request.method == "POST":
        userid = session['id']
        itemtype = request.form["itemtype"]
        brand = request.form["brand"]
        record_number = request.form["record_number"]

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO item_details(record_number, type, brand) VALUES (%s, %s, %s)", (record_number, itemtype, brand))
        mysql.connection.commit()
        cur.close()
        output_text = 'Success!'
        return render_template('item.html', output_text=output_text)

@app.route("/edit1", methods=['GET', 'POST'])
def edit1():
    if request.method == 'GET':
        record_number = request.args.get('record_number')
        session['record_number'] = record_number
        cur = mysql.connection.cursor()
        #cur.execute("SELECT * FROM `cost` WHERE `record_number`={};".format(record_number))
        cur.execute("SELECT * FROM `cost`, `item_details`, `purchase_info` WHERE cost.record_number=item_details.record_number AND cost.record_number=purchase_info.record_number AND cost.record_number={};".format(record_number))
        search_results = cur.fetchone()
        price = search_results['price']
        item = search_results['item']
        editer = search_results['edit_userid']
        itemtype = search_results['type']
        brand = search_results['brand']
        date = search_results['purchase_date']
        place = search_results['place']
        return render_template('edit1.html', display_name=session['username'],
                                record_number=record_number, price=price, item=item, editer=editer, itemtype=itemtype, brand=brand, date=date, place=place)
    if request.method == "POST":
        #record_number = int(request.data)
        #session['record_number'] = record_number
        return redirect(f"http://localhost:5000/edit1?record_number={record_number}", code=302)
        #return render_template('edit1.html', display_name=session['username'], record_number=record_number)

@app.route("/edit2", methods=['GET', 'POST'])
def update():
    if request.method == "POST":
        record_number = int(session['record_number'])
        price = request.form["price"]
        item = str(request.form["item"])
        editer = request.form["editer"]
        itemtype = str(request.form["itemtype"])
        brand = str(request.form["brand"])
        
        # Update the cost table
        cur = mysql.connection.cursor()
        cur.execute("UPDATE `cost` SET `price`={}, `item`='{}', `edit_userid`={} WHERE `record_number`={}".format(price, item, editer, record_number))
        mysql.connection.commit()
        cur.close()

        # Update the item table
        cur = mysql.connection.cursor()
        cur.execute("UPDATE `item_details` SET `type`='{}', `brand`='{}' WHERE `record_number`={}".format(itemtype, brand, record_number))
        mysql.connection.commit()
        cur.close()

        output_text = 'Success!'
        return render_template('edit1.html', display_name=session['username'],
                                record_number=record_number, price=price, item=item, editer=editer, itemtype=itemtype, brand=brand, output_text=output_text)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
