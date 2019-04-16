#!/usr/bin/env python2.7



"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)



# XXX: The Database URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "pil2104"#os.environ['username']
DB_PASSWORD = "2DJrhu9AoT" #os.environ['password']

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"

global rev_error
rev_error = False
global quant_error
quant_error = False
global login_error
login_error = False
global num_cust_error
num_cust_error = False
global income_error
income_error = False
global is_salesperson
is_salesperson = False
global is_high
is_high = False

#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)




#creating tables for viewing


engine.execute("""DROP TABLE IF EXISTS viewData;""")
engine.execute("""CREATE TABLE IF NOT EXISTS viewData (
  location text,
  manager_id text,
  address text,
  branch_profit float,
  no_customers int,
  quant_sold int,
  salesrevenue float
);""")

engine.execute("""DROP TABLE IF EXISTS viewEmployee;""")
engine.execute("""CREATE TABLE IF NOT EXISTS viewEmployee (
  ID text,
  name text,
  salary int,
  level text
);""")


engine.execute("""DROP TABLE IF EXISTS salesorder_temp;""")
engine.execute("""CREATE TABLE IF NOT EXISTS salesorder_temp (
  customer_name text,
  order_num int, 
  salesorder_revenue float,
  quantity int
);""")


engine.execute("""DROP TABLE IF EXISTS other_roles_tmp;""")
engine.execute("""CREATE TABLE IF NOT EXISTS other_roles_tmp (
  ID text,
  job_function text
);""")




#engine.execute("""INSERT INTO salesorder_temp SELECT salesorder.customer_name, salesorder.order_num, salesorder.salesorder_revenue, salesorder.quantity FROM salesorder);""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print (request.args)


  #
  # example of a database query

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  
  
    

  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  context = dict(error = login_error)
  
  return render_template("index.html", **context)


@app.route('/loginDM', methods=['POST'])
def loginDM():
    
    g.conn.execute("DELETE FROM salesorder_temp")
    g.conn.execute("DELETE FROM viewEmployee")
    g.conn.execute("DELETE FROM viewData")
    g.conn.execute("DELETE FROM other_roles_tmp")
    
    global userid_input
    global is_salesperson
    global is_high
    global login_error
    
    userid_input = request.form['username']
    password_input = request.form['password']
    password = ''
    cursor = g.conn.execute(text('''SELECT password FROM employee WHERE id = :userid'''),userid = userid_input)
    
    for result in cursor:
        password = result[0]
    cursor.close()
        
    
    if len(userid_input)>0 and len(password) > 0:

        
        cursor = g.conn.execute(text('''SELECT level FROM employee WHERE id = :userid'''),userid = userid_input)
        
        for result in cursor:
            level = result[0]
        cursor.close()
        
        cursor = g.conn.execute(text('''SELECT id FROM salesperson WHERE id = :userid'''),userid = userid_input)
        
        salesperson = 0
        
        for result in cursor:
            salesperson = result[0]
        cursor.close()
        
        if level == 'High':
            is_high = True
        
        else:
            is_high = False
        
        if salesperson == userid_input:
            is_salesperson = True
        
        else:
            is_salesperson = False
        
        
        if password_input == password :
            login_error = False
            return redirect("/homepage")
        else:
            login_error = True
            return redirect("/")
    else:
        #
        login_error = True
        return redirect("/")
#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
@app.route('/another')
def another():
  return render_template("another.html")

@app.route('/homepage')
def homepage():
  
  
    
  context = dict(status1 = is_high, status2 = is_salesperson)
  return render_template("homepage.html", **context)



@app.route('/dataview')
def dataview():

  cursor = g.conn.execute('''SELECT * FROM viewData''')
  view = []
  for result in cursor:
    view.append(result)  # can also be accessed using result[0]
  cursor.close()

  cursor = g.conn.execute("SELECT location FROM branch")
  locations = []
  for result in cursor:
    locations.append(result[0])
  cursor.close()

  context = dict(data = view, data2 = locations)

  return render_template("dataview.html", **context)


# Example of adding new data to the database
#@app.route('/add', methods=['POST'])
#def add():
#  name = request.form['name']
#  print(name)
#  cmd = 'INSERT INTO test(name) VALUES (:name1), (:name2)';
#  g.conn.execute(text(cmd), name1 = name, name2 = name);
#  return redirect('/test')

@app.route('/editemployee')
def editemployee():
  
    
  cursor = g.conn.execute("SELECT id FROM employee")
  ids = []
  for result in cursor:
    ids.append(result[0])
  cursor.close()

  cursor = g.conn.execute("SELECT DISTINCT level FROM employee")
  levels = []
  for result in cursor:
    levels.append(result[0])
  cursor.close()


  g.conn.execute("""INSERT INTO other_roles_tmp(ID, job_function)
               VALUES( (SELECT manager.ID FROM manager WHERE
               (SELECT ID from viewEmployee LIMIT 1) = manager.ID), 'Manager');""")
  
  g.conn.execute("""INSERT INTO other_roles_tmp(ID, job_function)
               VALUES( (SELECT other_roles.ID FROM other_roles WHERE
               (SELECT ID from viewEmployee LIMIT 1) = other_roles.ID), 
  
              (SELECT other_roles.job_function FROM other_roles WHERE
               (SELECT ID from viewEmployee LIMIT 1) = other_roles.ID));""")
  
  
  g.conn.execute("""INSERT INTO other_roles_tmp(ID, job_function)
               VALUES( (SELECT salesperson.ID FROM salesperson WHERE
               (SELECT ID from viewEmployee LIMIT 1) = salesperson.ID), 'Salesperson');""")

  cursor = g.conn.execute('''SELECT viewEmployee.ID, viewEmployee.name,
                          viewEmployee.salary, viewEmployee.level,
                          other_roles_tmp.job_function FROM viewEmployee 
                         
                          INNER JOIN other_roles_tmp ON viewEmployee.ID = other_roles_tmp.ID
                        
                          LIMIT 1''')
  empdata = []
  for result in cursor:
    empdata.append(result)
  cursor.close()
  
    
  context = dict(data1 = ids, data2 = levels, data3 = empdata, error = income_error)

  

  return render_template("editemployee.html", **context)

@app.route('/editcustomer')
def editcustomer():
  
  cmd = '''SELECT customer.customer_name,
                          customer.company_size,
                          customer.location
                          
                          FROM customer, salesperson_customer_R
                          
                          WHERE customer.customer_name = salesperson_customer_R.customer_name
                          AND salesperson_customer_R.ID = (:idval)'''
                          
  cursor = g.conn.execute(text(cmd), idval = userid_input)

  names = []
  for result in cursor:
    names.append(result)
  cursor.close()

  #cursor = g.conn.execute("SELECT id FROM salesperson")
  #ids = []
  #for result in cursor:
  #  ids.append(result[0])
  #cursor.close()
  
  cursor = g.conn.execute("SELECT location FROM branch")
  locations = []
  for result in cursor:
    locations.append(result[0])
  cursor.close()
  
    
  context = dict(data1 = names, data3 = locations, error = num_cust_error)

  

  return render_template("editcustomer.html", **context)

@app.route('/addsalesorder')
def addsalesorder():



  cursor = g.conn.execute("SELECT id FROM salesperson")
  ids = []
  for result in cursor:
    ids.append(result[0])
  cursor.close()
  

  cmd = '''SELECT * FROM salesorder WHERE ID = (:idval)'''
  cursor = g.conn.execute(text(cmd), idval = userid_input)
  salesorder = []
  for result in cursor:
    salesorder.append(result)
  cursor.close()
  
  
  cmd = '''SELECT DISTINCT customer_name FROM salesorder WHERE id = (:idval)'''
  cursor = g.conn.execute(text(cmd), idval = userid_input)
  customername = []
  for result in cursor:
    customername.append(result[0])
  cursor.close()


  context = dict(data2 = salesorder,
                 data3 = customername,
                 error1 = rev_error,
                 error2 = quant_error)

  return render_template("addsalesorder.html", **context)



@app.route('/view', methods=['POST'])
def view():
  
  locations = request.form.getlist('locations')
  
  g.conn.execute("DELETE FROM viewData")
  for inp, loc in enumerate(locations):
    cmd = '''INSERT INTO viewData select x.location, m.id as Manager_Id,t.address, sum(x.profit) as Branch_profit,y.no_customers as No_customers, z.Quantsold, z.salesRevenue
from
	((select location,department_name, (dept_revenue - dept_cost) as profit
	from department_branch_r) as x
	left outer join
	(select location, count(*) as no_customers
	from customer
	group by location) as y on y.location = x.location)
	left outer join 
	(select j.location, sum(p.quantity) as Quantsold, sum(p.salesorder_revenue) as salesRevenue
	 from salesorder as p left outer join customer as j on p.customer_name = j.customer_name
	 group by j.location) as z on z.location = y.location
	left outer join branch as t on t.location = z.location
    left outer join manager as m on m.location = z.location
where x.location = :branchloc
group by x.location, y.no_customers, z.Quantsold, z.salesRevenue,t.address,m.id
order by z.salesRevenue desc''';
    var1=g.conn.execute(text(cmd), branchloc = loc);
  return redirect('/dataview')
#

@app.route('/viewemployee', methods=['POST'])
def viewemployee():
  
  id_input = request.form['selectID']
  
  #deleting everything during view so it will not bleed into next view
  g.conn.execute("DELETE FROM viewEmployee")
  
  #inserting new employee info into view
  cmd = 'INSERT INTO viewEmployee SELECT ID, name, salary, level FROM employee WHERE ID = (:idval)';
  g.conn.execute(text(cmd), idval = id_input);
  return redirect('/editemployee')


@app.route('/changelevel', methods=['POST'])
def changelevel():
  
  level_input = request.form['selectLevel']
  
  #updating value in employee (actual database)
  cmd = 'UPDATE employee SET level = (:levelval) WHERE ID IN (SELECT ID FROM viewEmployee)';
  
  g.conn.execute(text(cmd), levelval = level_input);
  
  #inserting new value into view employee (what will be viewed on webapp)
  g.conn.execute('INSERT INTO viewEmployee SELECT ID, name, salary, level FROM employee WHERE ID IN (SELECT ID FROM viewEmployee)')
  
  
  #deleting old value
  cmd = 'DELETE FROM viewEmployee WHERE level != (:levelval)'
  
  g.conn.execute(text(cmd), levelval = level_input);


  
  return redirect('/editemployee')

@app.route('/changesal', methods=['POST'])
def changesal():
  
  global income_error
  salary_input = request.form['newsal']
  #checking if number is parsable
  if isParsableNum(salary_input) and int(float(salary_input)) >= 20:
  
    #updating value in employee (actual database)
    cmd = 'UPDATE employee SET salary = (:salaryval) WHERE ID IN (SELECT ID FROM viewEmployee)';
  
    g.conn.execute(text(cmd), salaryval = int(float(salary_input)));
  
    #inserting new value into view employee (what will be viewed on webapp)
    g.conn.execute('INSERT INTO viewEmployee SELECT ID, name, salary, level FROM employee WHERE ID IN (SELECT ID FROM viewEmployee)')
  
    #deleting old value
    cmd = 'DELETE FROM viewEmployee WHERE salary != (:salaryval)'
  
    g.conn.execute(text(cmd), salaryval = int(float(salary_input)));
    
    income_error = False


  else:
      
      
      income_error = True

  
    
  return redirect('/editemployee')


@app.route('/deletecustomer', methods=['POST'])
def deletecustomer():
  
  nameinput = request.form['deletecustomer']
  nameinput.replace(' ','_')
  
  #deleteing employee with name
  cmd1 = 'DELETE FROM salesperson_customer_R WHERE customer_name = (:nameval) AND id = (:idval)';
  cmd2 = '''DELETE FROM customer, salesperson_customer_R
  WHERE customer.customer_name = (:nameval)
  AND salesperson_customer_R.customer_name = customer.customer_name
  AND salesperson_customer_R.id = (:idval)''';
  g.conn.execute(text(cmd1), nameval = nameinput, idval = user_input_id);
  g.conn.execute(text(cmd2), nameval = nameinput, idval = user_input_id);
  return redirect('/editcustomer')


@app.route('/addcustomer', methods=['POST'])
def addcustomer():
  
  global num_cust_error
  nameinput = request.form['customername'].replace(' ', '_')
  companysize = request.form['companysize']
  location = request.form['selectlocation']
  
  if isParsableNum(companysize) and int(float(companysize)) >= 1 and (nameinput[0] != ')'and nameinput[1]!=';'):
      
      cmd = 'INSERT INTO customer VALUES((:nameval), (:sizeval), (:locval))';
      g.conn.execute(text(cmd),
                     nameval = nameinput,
                     sizeval = int(float(companysize)),
                     locval = location);
      
      cmd = 'INSERT INTO salesperson_customer_R VALUES((:idval), (:nameval))'
      
      g.conn.execute(text(cmd),
                     nameval = nameinput,
                     idval = userid_input);
        
      num_cust_error = False
  else:

      num_cust_error = True
  
  
  return redirect('/editcustomer')

@app.route('/viewsalesorder', methods=['POST'])
def viewsalesorder():
  
  #id_input = request.form['selectID']
  
  #deleting everything during view so it will not bleed into next view
  g.conn.execute("DELETE FROM salesorder_temp")
  
  #inserting new employee info into view
  cmd = '''INSERT INTO salesorder_temp SELECT customer_name, order_num, 
  salesorder_revenue, quantity FROM salesorder WHERE ID = (:idval)''';
  g.conn.execute(text(cmd), idval = userid_input);
  return redirect('/addsalesorder')


@app.route('/addsale', methods=['POST'])
def addsale():
    
  
  nameinput = request.form['selectcustomer']
  revenue = request.form['revenue']
  quantity = request.form['quantity']
  
  global rev_error
  global quant_error
  
  if isParsableNum(revenue) and isParsableNum(quantity) and float(revenue) > 0 and int(float(quantity)) > 0 :
      
      cmd = '''INSERT INTO salesorder VALUES(
      (SELECT ID from salesperson_customer_R WHERE customer_name = (:nameval)),
      (:nameval), 
      (SELECT order_num + 1 FROM salesorder ORDER BY -order_num LIMIT 1),
      (:revenueval), 
      (:quantval))'''
      
      
      g.conn.execute(text(cmd), nameval = nameinput,
                     revenueval = float(revenue),
                     quantval = int(float(quantity)));
      rev_error = False
      quant_error = False
                     
  
  
  else:
  
      if ~isParsableNum(revenue) or float(revenue) <= 0:
          rev_error = True
      
      if ~isParsableNum(quantity) or int(float(quantity)) <= 0:
          quant_error = True
    
  return redirect('/addsalesorder')



@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()
    

def isParsableNum(num):
    try:
        int(float(num))
        return True
    except:
        return False



if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print ("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
