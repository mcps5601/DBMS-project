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
                cur.execute("SELECT `userid`, `username`, `record_number`, `price`, `item` FROM users, cost, user_info WHERE users.id=cost.userid AND users.id=user_info.id AND user_info.nickname='{}'".format(str(request.form['keywords'])))
            results = cur.fetchall()

        if option == 'Itemname':
            cur = mysql.connection.cursor()
            if request.form['keywords']=='all':
                cur.execute("SELECT `userid`, `username`, `record_number`, `price`, `item` FROM users, cost WHERE users.id=cost.userid")
            else:
                cur.execute("SELECT `userid`, `username`, `record_number`, `price`, `item` FROM users, cost WHERE users.id=cost.userid AND cost.item='{}'".format(str(request.form['keywords'])))
            results = cur.fetchall()
        
        ## 不包含某人的資料查詢 (NOT IN)
        if option == '不包含人名':
            cur = mysql.connection.cursor()
            cur.execute("SELECT `userid`, `username`, `record_number`, `price`, `item` FROM users, cost WHERE users.id=cost.userid AND users.username NOT IN ('{}')".format(str(request.form['keywords'])))
            results = cur.fetchall()

        ## 有填寫詳細資料的 (EXIST)
        if option =="有填寫商品細節":
            cur = mysql.connection.cursor()
            cur.execute("SELECT `userid`, `username`, `record_number`, `price`, `item` FROM users, cost WHERE EXISTS (SELECT record_number FROM item_details WHERE cost.record_number=item_details.record_number) AND users.id=cost.userid")
            results = cur.fetchall() 

        if option =="有填寫購物細節":
            cur = mysql.connection.cursor()
            cur.execute("SELECT `userid`, `username`, `record_number`, `price`, `item` FROM users, cost WHERE EXISTS (SELECT record_number FROM purchase_info WHERE cost.record_number=purchase_info.record_number) AND users.id=cost.userid")
            results = cur.fetchall()                

        ## 沒有填寫詳細資料的 (NOT EXISTS)
        if option =="沒有填寫商品細節":
            cur = mysql.connection.cursor()
            cur.execute("SELECT `userid`, `username`, `record_number`, `price`, `item` FROM users, cost WHERE NOT EXISTS (SELECT record_number FROM item_details WHERE cost.record_number=item_details.record_number) AND users.id=cost.userid")
            results = cur.fetchall()
        
        if option =="沒有填寫購物細節":
            cur = mysql.connection.cursor()
            cur.execute("SELECT `userid`, `username`, `record_number`, `price`, `item` FROM users, cost WHERE NOT EXISTS (SELECT record_number FROM purchase_info WHERE cost.record_number=purchase_info.record_number) AND users.id=cost.userid")
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
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(id) FROM `users`;")
        number = cur.fetchone().get('COUNT(id)')
        print("Number:", number)
        userid = number+1

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(id, username, password) VALUES (%s, %s, %s)", (userid, username, password))
        mysql.connection.commit()
        cur.close()
        output_text = 'Success!'
        return render_template('new_user.html', output_text=output_text)

@app.route("/profile", methods=['GET', 'POST'])
def profile():
    if request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM `user_info` WHERE user_info.id={};".format(session['id']))
        search_results = cur.fetchone()
        if search_results is not None:
            sex = search_results["sex"]
            nickname = search_results["nickname"]
            return render_template('profile.html', display_name=session['username'], userid=session['id'], sex=sex, nickname=nickname)
        else:
            return render_template('profile.html', display_name=session['username'], userid=session['id'])

    if request.method == "POST":
        sex = request.form["sex"]
        nickname = request.form["nickname"]

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM `user_info` WHERE `id`={}".format(session['id']))
        result = cur.fetchone()
        if result==None:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO user_info(id, sex, nickname) VALUES (%s, %s, %s)", (session['id'], sex, nickname))
            mysql.connection.commit()
            cur.close()
            output_text = 'Success!'
        if result==True:
            cur = mysql.connection.cursor()
            cur.execute("UPDATE `user_info` SET `sex`={}, `nickname`='{}' WHERE `id`={}".format(sex, nickname, session['id']))
            mysql.connection.commit()
            cur.close()
            output_text = 'Success!'
        return render_template('profile.html', output_text=output_text, display_name=session['username'], userid=session['id'], sex=sex, nickname=nickname)



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
        cur.execute("SELECT * FROM `cost` WHERE `record_number`={};".format(record_number))
        #cur.execute("SELECT * FROM `cost`, `item_details`, `purchase_info` WHERE cost.record_number=item_details.record_number AND cost.record_number=purchase_info.record_number AND cost.record_number={};".format(record_number))
        absolute_results = cur.fetchone()
        price = absolute_results['price']
        item = absolute_results['item']
        editer = absolute_results['edit_userid']

        # search the `item_details` table
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM `item_details` WHERE `record_number`={};".format(record_number))
        item_results = cur.fetchone()

        # search the `purchase_info` table
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM `purchase_info` WHERE `record_number`={};".format(record_number))
        purchase_results = cur.fetchone()

        if item_results is not None and purchase_results is None:
            itemtype = item_results['type']
            brand = item_results['brand']
            return render_template('edit1.html', display_name=session['username'],
                                    record_number=record_number, price=price, item=item, editer=editer, itemtype=itemtype, brand=brand)

        elif item_results is None and purchase_results is not None:
            date = purchase_results['purchase_date']
            place = purchase_results['place']
            return render_template('edit1.html', display_name=session['username'],
                                    record_number=record_number, price=price, item=item, editer=editer, date=date, place=place)         

        elif item_results is not None and purchase_results is not None:
            itemtype = item_results['type']
            brand = item_results['brand']
            date = purchase_results['purchase_date']
            place = purchase_results['place']
            return render_template('edit1.html', display_name=session['username'],
                                    record_number=record_number, price=price, item=item, editer=editer, itemtype=itemtype, brand=brand, date=date, place=place)
        else:
            return render_template('edit1.html', display_name=session['username'], record_number=record_number, price=price, item=item, editer=editer)
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
        date = str(request.form["date"])
        place = request.form["place"]

        # Update the cost table
        cur = mysql.connection.cursor()
        cur.execute("UPDATE `cost` SET `price`={}, `item`='{}', `edit_userid`={} WHERE `record_number`={}".format(price, item, editer, record_number))
        mysql.connection.commit()
        cur.close()

        # search the `item_details` table
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM `item_details` WHERE `record_number`={}".format(record_number))
        item_results = cur.fetchone()

        # search the `purchase_info` table
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM `purchase_info` WHERE `record_number`={}".format(record_number))
        purchase_results = cur.fetchone()

        if item_results is not None and purchase_results is None:
            # Update the `item_details` table
            cur = mysql.connection.cursor()
            cur.execute("UPDATE `item_details` SET `type`='{}', `brand`='{}' WHERE `record_number`={}".format(itemtype, brand, record_number))
            mysql.connection.commit()
            cur.close()
            output_text = 'Success!'
            return render_template('edit1.html', display_name=session['username'],
                                record_number=record_number, price=price, item=item, editer=editer, itemtype=itemtype, brand=brand, output_text=output_text)

        elif purchase_results is not None and item_results is None:
            # Update the `purchase_info` table
            cur = mysql.connection.cursor()
            print("UPDATE `purchase_info` SET `date`='{}', `place`='{}' WHERE `record_number`={}".format(date, place, record_number))
            cur.execute("UPDATE `purchase_info` SET `purchase_date`='{}', `place`='{}' WHERE `record_number`={}".format(date, place, record_number))
            mysql.connection.commit()
            cur.close()
            output_text = 'Success!'
            return render_template('edit1.html', display_name=session['username'],
                                record_number=record_number, price=price, item=item, editer=editer, date=date, place=place, output_text=output_text)

        elif item_results is not None and purchase_results is not None:
            # Update the `item_details` table
            cur = mysql.connection.cursor()
            cur.execute("UPDATE `item_details` SET `type`='{}', `brand`='{}' WHERE `record_number`={}".format(itemtype, brand, record_number))
            mysql.connection.commit()
            cur.close()

            # Update the `purchase_info` table
            cur = mysql.connection.cursor()
            cur.execute("UPDATE `purchase_info` SET `purchase_date`='{}', `place`='{}' WHERE `record_number`={}".format(date, place, record_number))
            mysql.connection.commit()
            cur.close()
            output_text = 'Success!'
            return render_template('edit1.html', display_name=session['username'],
                                record_number=record_number, price=price, item=item, editer=editer, itemtype=itemtype, brand=brand, date=date, place=place, output_text=output_text)

@app.route("/statistic", methods=['GET'])
def statistic():
    if request.method == 'GET':
        # COUNT: 計算目前所有筆數
        cur = mysql.connection.cursor()
        cur.execute('SELECT COUNT(`record_number`) FROM `cost`')
        numbers_record = cur.fetchone().get('COUNT(`record_number`)')
        cur.close()

        # SUM: 統計目前記帳所有金額
        cur = mysql.connection.cursor()
        cur.execute('SELECT SUM(`price`) FROM `cost`')
        sum_record = cur.fetchone().get('SUM(`price`)')
        cur.close()

        # MAX: 取出金額最大的紀錄
        cur = mysql.connection.cursor()
        cur.execute('SELECT `userid`, `username`, `record_number`, `price`, `item` FROM users, cost WHERE cost.price=( SELECT MAX(`price`) FROM cost ) AND users.id=cost.userid')
        max_record = cur.fetchone()
        cur.close()

        # MIN: 取出金額最小的紀錄
        cur = mysql.connection.cursor()
        cur.execute('SELECT `userid`, `username`, `record_number`, `price`, `item` FROM users, cost WHERE cost.price=( SELECT MIN(`price`) FROM cost ) AND users.id=cost.userid')
        min_record = cur.fetchone()
        cur.close()

        # AVG: 平均花費
        cur = mysql.connection.cursor()
        cur.execute('SELECT AVG(`price`) FROM `cost`')
        avg_record = cur.fetchone().get('AVG(`price`)')
        cur.close()

        # HAVING: 取出花費超過10000的人
        cur = mysql.connection.cursor()
        cur.execute('SELECT `username`, SUM(`price`) FROM users, cost WHERE users.id=cost.userid GROUP BY users.username HAVING SUM(`price`) > 10000')
        results = cur.fetchall()

        people = []
        for i in range(len(results)):
            people.append(results[i]['username'])
        cur.close()
        return render_template('statistic.html', display_name=session['username'], numbers_record=numbers_record, sum_record=sum_record,
                            max_record=max_record, min_record=min_record, avg_record=avg_record, people=people)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
