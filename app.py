import pymysql
from flask import Flask, render_template, request, redirect

app = Flask(__name__)
app.secret_key = "keysecret"

try:
    connection = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='LAUGHING',
        database='warehouse',
        cursorclass=pymysql.cursors.DictCursor
    )
    print("success")
except Exception as ex:
    print("failure")
    print(ex)


def get_shipments():
    with connection.cursor() as cursor:
        select_query = "SELECT * FROM `warehouse`.`shipment`"
        cursor.execute(select_query)
        shipments = cursor.fetchall()
        connection.commit()
    return shipments


def get_outcomings():
    with connection.cursor() as cursor:
        select_query = "SELECT * FROM `warehouse`.`outcoming`"
        cursor.execute(select_query)
        outcomings = cursor.fetchall()
        connection.commit()
    return outcomings


def get_incomings():
    with connection.cursor() as cursor:
        select_query = "SELECT * FROM `warehouse`.`incoming`"
        cursor.execute(select_query)
        incomings = cursor.fetchall()
        connection.commit()
    return incomings


def get_writeoffs():
    with connection.cursor() as cursor:
        select_query = "SELECT * FROM `warehouse`.`writeoff`"
        cursor.execute(select_query)
        writeoffs = cursor.fetchall()
        connection.commit()
    return writeoffs


@app.route('/', methods=["POST", "GET"])
def index():
    return render_template('login.html')


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            return redirect('/shipments')
        else:
            return redirect('/')

@app.route('/shipments')
def shipments():
    return render_template('shipments.html', shipments=get_shipments())


@app.route('/incomings')
def incomings():
    return render_template('incomings.html', incomings=get_incomings())


@app.route('/outcomings')
def outcomings():
    return render_template('outcomings.html', outcomings=get_outcomings())


@app.route('/writeoffs')
def writeoffs():
    return render_template('writeoffs.html', writeoffs=get_writeoffs())


@app.route('/out/<string:id>', methods = ['POST','GET'])
def out_shipment(id):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM `warehouse`.`writeoff` WHERE (`shipment_id` = {0})'.format(id))
        check = cursor.fetchall()
        if len(check) == 0:
            cursor.execute('INSERT INTO `warehouse`.`outcoming`(`shipment_id`, `name`)SELECT `id`, `name` FROM `warehouse`.`shipment` WHERE (`id` = {0})'.format(id))
            connection.commit()
        else:
            return render_template('tooutcomingerror.html')
    return redirect('/shipments')


@app.route('/off/<string:id>', methods = ['POST','GET'])
def off_shipment(id):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM `warehouse`.`outcoming` WHERE (`shipment_id` = {0})'.format(id))
        check = cursor.fetchall()
        if len(check) == 0:
            cursor.execute('INSERT INTO `warehouse`.`writeoff`(`shipment_id`, `name`)SELECT `id`, `name` FROM `warehouse`.`shipment` WHERE (`id` = {0})'.format(id))
            connection.commit()
        else:
            return render_template('towriteofferror.html')
    return redirect('/shipments')


@app.route('/revert/<string:id>', methods = ['POST','GET'])
def revert_shipment(id):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM `warehouse`.`outcoming` WHERE (`shipment_id` = {0})'.format(id))
        check_out = cursor.fetchall()
        cursor.execute('SELECT * FROM `warehouse`.`writeoff` WHERE (`shipment_id` = {0})'.format(id))
        check_off = cursor.fetchall()
        if len(check_out) > 0:
            return render_template('outexistserror.html')
        if len(check_off) > 0:
            return render_template('offexistserror.html')
        cursor.execute('INSERT INTO `warehouse`.`incoming`(`name`)SELECT `name` FROM `warehouse`.`shipment` WHERE (`id` = {0})'.format(id))
        connection.commit()
        cursor.execute('DELETE FROM `warehouse`.`shipment` WHERE `id` = {0}'.format(id))
        connection.commit()
    return redirect('/shipments')


@app.route('/delete/<string:id>', methods = ['POST','GET'])
def delete_shipment(id):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM `warehouse`.`outcoming` WHERE (`shipment_id` = {0})'.format(id))
        check_out = cursor.fetchall()
        cursor.execute('SELECT * FROM `warehouse`.`writeoff` WHERE (`shipment_id` = {0})'.format(id))
        check_off = cursor.fetchall()
        if len(check_out) > 0:
            return render_template('outexistserror.html')
        if len(check_off) > 0:
            return render_template('offexistserror.html')
        cursor.execute('DELETE FROM `warehouse`.`shipment` WHERE id = {0}'.format(id))
        connection.commit()
    return redirect('/shipments')


@app.route('/incomplete/<string:id>', methods = ['POST','GET'])
def complete_incoming(id):
    with connection.cursor() as cursor:
        cursor.execute('INSERT INTO `warehouse`.`shipment`(`name`)SELECT `name` FROM `warehouse`.`incoming` WHERE (id = {0})'.format(id))
        connection.commit()
        cursor.execute('DELETE FROM `warehouse`.`incoming` WHERE `id` = {0}'.format(id))
        connection.commit()
    return redirect('/incomings')


@app.route('/indelete/<string:id>', methods = ['POST','GET'])
def delete_incoming(id):
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM `warehouse`.`incoming` WHERE id = {0}'.format(id))
        connection.commit()
    return redirect('/incomings')


@app.route('/outdelete/<string:id>', methods = ['POST','GET'])
def delete_outcoming(id):
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM `warehouse`.`outcoming` WHERE id = {0}'.format(id))
        connection.commit()
    return redirect('/outcomings')


@app.route('/outcomplete/<string:id>', methods = ['POST','GET'])
def complete_outcoming(id):
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM `warehouse`.`outcoming` WHERE shipment_id = {0}'.format(id))
        connection.commit()
        cursor.execute('DELETE FROM `warehouse`.`shipment` WHERE id = {0}'.format(id))
        connection.commit()
    return redirect('/outcomings')


@app.route('/offdelete/<string:id>', methods = ['POST','GET'])
def delete_writeoff(id):
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM `warehouse`.`writeoff` WHERE id = {0}'.format(id))
        connection.commit()
    return redirect('/writeoffs')


@app.route('/offcomplete/<string:id>', methods = ['POST','GET'])
def complete_writeoff(id):
    with connection.cursor() as cursor:
        cursor.execute('DELETE FROM `warehouse`.`writeoff` WHERE shipment_id = {0}'.format(id))
        connection.commit()
        cursor.execute('DELETE FROM `warehouse`.`shipment` WHERE id = {0}'.format(id))
        connection.commit()
    return redirect('/writeoffs')


@app.route('/add', methods=["POST", "GET"])
def add():
    if request.method == "POST":
        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO `warehouse`.`incoming` (`name`) VALUES(%s)', (request.form['name']))
            connection.commit()
    return render_template('add.html')


if __name__ == '__main__':
    app.run()
