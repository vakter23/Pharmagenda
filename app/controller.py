from app import app
from flask import render_template
from flask import jsonify
from flask_session import Session
import json
from .database import *

app.secret_key = "27eduCBA09"
from flask import Flask, render_template, redirect, request, session
from flask_session import Session

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# /**
#  * Get the employees and the work days of the company
#  * Then render the calendar with all the infos if the user is connected
#  * @return template
#  */
@app.route("/")
def index():
    if not session.get("name"):
        return redirect("/login")
    else:
        if session.get("idCompany"):
            #
            cur = conn.cursor()
            cur.execute("SELECT idEmployee, employee_name, employee_surname, color FROM employee WHERE idCompany=?",
                        (session.get("idCompany"),))
            rowsEmployees = cur.fetchall()
            cur = conn.cursor()
            cur.execute("SELECT idEmployee, employee_name, employee_surname, color FROM employee WHERE idCompany=?",
                        (session.get("idCompany"),))
            rowsEmployees = cur.fetchall()
            list_accumulator = []
            for item in rowsEmployees:
                list_accumulator.append({k: item[k] for k in item.keys()})
            rowsEmployees = list_accumulator
            rowsWorkDay = get_all_days_work(session.get("idCompany"))
        else:
            rowsEmployees = []
        return render_template('index.html', title='Calendrier', utilisateur=session["name"], employees=rowsEmployees,
                               daysWork=rowsWorkDay)


# /**
#  * Verify if the user exists
#  * create session with name, surname, idCompany and idUser
#  * Then redirect to the index page
#  * @return error if the user don't exist
#  * else return to the index
#  */
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        name = request.form.get("name")
        surname = request.form.get("surname")
        cur = conn.cursor()
        cur.execute("SELECT name, surname, idCompany, idUser FROM user WHERE name=? AND surname=?", (name, surname))
        rows = cur.fetchall()
        if (rows):
            session["name"] = rows[0][0]
            session["surname"] = rows[0][1]
            session["idCompany"] = rows[0][2]
            session["idUser"] = rows[0][3]
            return redirect("/")
        else:
            return render_template("login.html", error="true")
    return render_template("login.html", title="Login")


# /**
#  * Disconnect the user
#  */
@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/")


# /**
#  * Render the create_account template
#  */
@app.route('/account/createAccount')
def create_account_page():
    return render_template("create_account.html", title="Creation de compte")


# /**
#  * Get the infos entered by the user
#  * Insert the new user and the new company in the database
#  * @return to the login page
#  */
@app.route('/account/createAccount/create', methods=["POST", "GET"])
def create_account():
    if request.method == "POST":
        name = request.form.get("name")
        surname = request.form.get("surname")
        company_name = request.form.get("company_name")
        company_address = request.form.get("company_address")
        cur = conn.cursor()
        cur.execute("INSERT INTO company (company_name,company_address) VALUES(?, ?)", (company_name, company_address))
        idCompany = cur.lastrowid
        cur.execute("INSERT INTO user (name,surname,idCompany) VALUES(?, ?, ?)", (name, surname, idCompany))
        idUser = cur.lastrowid
        cur.execute("UPDATE company SET idUser = ? WHERE idCompany = ?", (idUser, idCompany,))
        conn.commit()
        return redirect("/login")


# /**
#  * Get the infos of the new date add to the calendar
#  * Insert the new day in the database
#  * @return to the home page
#  */
@app.route('/calendar/addDay', methods=["POST", "GET"])
def add_event():
    if request.method == "POST":
        idCompany = session["idCompany"]
        idEmployee = request.form.get("iddddd")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        cur = conn.cursor()
        cur.execute("INSERT INTO workDay (idCompany,idEmployee,start_date,end_date) VALUES(?, ?, ?, ?)",
                    (idCompany, idEmployee, start_date, end_date))
        conn.commit()
        return redirect("/")


# /**
#  *  Delete a day in the database
#  * @return to the home page after the deletion
#  */
@app.route('/calendar/deleteWorkDay/<int:dayWork_id>')
def delete_event(dayWork_id):
    cur = conn.cursor()
    dayWork_id = dayWork_id
    cur.execute("DELETE FROM workDay WHERE idWorkDay=?", (dayWork_id,))
    conn.commit()
    return redirect("/")


# /**
#  * Modify the information of a day work
#  * Modify the day work in the database by his id
#  * @return to the home page
#  */
@app.route('/calendar/modifyWorkDay', methods=["POST", "GET"])
def modify_event():
    if request.method == "POST":
        idWorkDay = request.form.get("idWorkDay")
        new_start_date = request.form.get("start_date")
        new_end_date = request.form.get("end_date")
        cur = conn.cursor()
        cur.execute("UPDATE workDay SET start_date = ?, end_date = ? WHERE idWorkDay = ?",
                    (new_start_date, new_end_date, idWorkDay))
        conn.commit()
        return redirect("/")


# /**
#  * Get all the days work of a company
#  * Select all the days work by the id company
#  * @return a list of days work
#  */
@app.route('/calendar/<int:company_id>/getDaysWork')
def get_all_days_work(company_id):
    cur = conn.cursor()
    company_id = company_id
    cur.execute(
        "SELECT idWorkDay,employee.idEmployee,start_date,end_date,employee_name,employee_surname,color FROM workDay INNER JOIN employee ON workDay.idEmployee=employee.idEmployee AND workDay.idCompany=employee.idCompany WHERE workDay.idCompany=?",
        (company_id,))
    rowsEmployees = cur.fetchall()
    list_accumulator = []
    for item in rowsEmployees:
        list_accumulator.append({k: item[k] for k in item.keys()})
    return (list_accumulator)


# /**
#  * Get all the employees of company
#  * Then render the template with all the workers
#  * @return a template with all the employees
#  */
@app.route('/employees')
def list_employees():
    cur = conn.cursor()
    cur.execute("SELECT * FROM employee WHERE idCompany=?", (session.get("idCompany"),))
    rowsEmployees = cur.fetchall()
    list_accumulator = []
    for item in rowsEmployees:
        list_accumulator.append({k: item[k] for k in item.keys()})
    rowsEmployees = list_accumulator
    return render_template('employees.html', title='Employees', employees=rowsEmployees)


# /**
#  * Get employee info and display it in the template
#  * Get employee infos and his work day then transfer it to the template
#  * @return a template with employee info and his work days
#  */
@app.route('/employee/<int:idEmployee>', methods=["POST", "GET"])
def employee(idEmployee):
    rowEmployee = get_employee_infos(idEmployee)
    rowEmployeeWorkDay = get_employee_work_days(idEmployee)
    return render_template('employee.html', title='Employee', employee=rowEmployee, workDays=rowEmployeeWorkDay)


# /**
#  * Modify the employee infos entered by the user
#  * Get new employee infos then modify in the DB
#  * @return the employee page after the modification
#  */
@app.route('/employee/<int:idEmployee>/modify_infos', methods=["POST", "GET"])
def employee_modify(idEmployee):
    if request.method == "POST":
        idEmployee = idEmployee
        name = request.form.get("name")
        surname = request.form.get("surname")
        color = request.form.get("color")
        cur = conn.cursor()
        cur.execute("UPDATE employee SET  employee_name = ?, employee_surname = ?, color = ? WHERE idEmployee = ?",
                    (name, surname, color, idEmployee))
        conn.commit()
        return redirect("/employee/" + str(idEmployee))


# /**
#  * Return all infos of an employee by his ID
#  * Retrieve the infos by the employee id
#  * @return the infos of an employee in a list
#  */
@app.route('/employee/get_infos/<int:idEmployee>')
def get_employee_infos(idEmployee):
    idEmployee = idEmployee
    cur = conn.cursor()
    cur.execute("SELECT * FROM employee WHERE idEmployee=?", (idEmployee,))
    rowEmployee = cur.fetchall()
    list_accumulator = []
    for item in rowEmployee:
        list_accumulator.append({k: item[k] for k in item.keys()})
    rowEmployee = list_accumulator
    return rowEmployee


# /**
#  * Return all days work of an employee by his ID
#  * Retrieve the days by the employee id
#  * @return the all days of an employee in a list
#  */
@app.route('/employee/get_work_days/<int:idEmployee>')
def get_employee_work_days(idEmployee):
    idEmployee = idEmployee
    cur = conn.cursor()
    cur.execute("SELECT * FROM workDay WHERE idEmployee=?", (idEmployee,))
    rowEmployeeWorkDay = cur.fetchall()
    list_accumulator = []
    for item in rowEmployeeWorkDay:
        list_accumulator.append({k: item[k] for k in item.keys()})
    rowEmployeeWorkDay = list_accumulator
    return rowEmployeeWorkDay


# /**
#  * Create a new employee of a company
#  * Get the infos entered by thge user and then insert in the DB
#  * @return the employees page with the new worker
#  */
@app.route('/employee/createEmployee', methods=["POST", "GET"])
def create_employee():
    if request.method == "POST":
        idCompany = session["idCompany"]
        name = request.form.get("name")
        surname = request.form.get("surname")
        color = request.form.get("color")
        cur = conn.cursor()
        cur.execute("INSERT INTO employee (idCompany,employee_name,employee_surname,color) VALUES(?, ?, ?, ?)",
                    (idCompany, name, surname, color))
        conn.commit()
        return redirect("/employees")


# /**
#  * Delete a employee by his id
#  * Delete in the DB by employee id
#  * @return the employees page
#  */
@app.route('/employee/delete/<int:idEmployee>', methods=["POST", "GET"])
def delete_employee(idEmployee):
    if request.method == "POST":
        idEmployee = idEmployee
        cur = conn.cursor()
        cur.execute("DELETE FROM employee WHERE idEmployee=?", (idEmployee,))
        conn.commit()
        return redirect("/employees")


# /**
#  * Display the infos of the user and his company
#  * Get the user infos and his company in the DB and then display it
#  * @return the template with the user infos and his company
#  */
@app.route('/infos/')
def infos():
    cur = conn.cursor()
    cur.execute("SELECT * FROM user WHERE idUser=?", (session.get("idUser"),), )
    rowUser = cur.fetchall()
    cur = conn.cursor()
    cur.execute("SELECT * FROM company WHERE idCompany=?", (session.get("idCompany"),))
    rowCompany = cur.fetchall()
    list_accumulator = []
    for item in rowCompany:
        list_accumulator.append({k: item[k] for k in item.keys()})
    rowCompany = list_accumulator
    return render_template('infos.html', title='Informations', utilisateur=session["name"], user=rowUser,
                           company=rowCompany)


# /**
#  * Modify the company infos entered by the user
#  * Get new company infos and then insert in the DB
#  * @return the template with the new infos
#  */
@app.route('/infos/modify_company/<int:idCompany>', methods=["POST", "GET"])
def modify_company(idCompany):
    if request.method == "POST":
        idCompany = idCompany
        name = request.form.get("name")
        address = request.form.get("address")
        cur = conn.cursor()
        cur.execute("UPDATE company SET company_name = ?, company_address = ? WHERE idCompany = ?",
                    (name, address, idCompany))
        conn.commit()
        return redirect("/infos")



# /**
#  * Modify the user infos entered by the user
#  * Get new user infos and then insert in the DB
#  * @return the template with the new infos
#  */
@app.route('/infos/modify_user/<int:idUser>', methods=["POST", "GET"])
def modify_user(idUser):
    if request.method == "POST":
        idUser = idUser
        name = request.form.get("name")
        surname = request.form.get("surname")
        cur = conn.cursor()
        cur.execute("UPDATE user SET name = ?, surname = ? WHERE idUser = ?", (name, surname, idUser))
        conn.commit()
        return redirect("/infos")
