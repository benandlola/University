from flask import Flask, session, render_template, redirect, url_for, request, flash
import mysql.connector
from datetime import timedelta, datetime

app = Flask('app')
app.secret_key = 'Hi mom'

mydb = mysql.connector.connect(
  host = "phase-2-group2.cnleqhafy7wq.us-east-1.rds.amazonaws.com",
  user = "admin",
  password = "adminpass",
  database = "university"
)

def mydbfunc():
  mydb = mysql.connector.connect(
    host = "phase-2-group2.cnleqhafy7wq.us-east-1.rds.amazonaws.com",
    user = "admin",
    password = "adminpass",
    database = "university"
  ) 
  return mydb

########################################################################################################################################
  #LOGOUT FUNCTION (does not have an HTML page) (ALL)
    #clears all session variables and returns user to login page
########################################################################################################################################
@app.route("/logout")
def Logout():
  session.clear()
  return redirect("/")


########################################################################################################################################
  #PORTAL FUNCTION (does not have an HTML page) (ALL)
    #redirects users to the appropriate portal page based on their role
      #included in the navbar which is why it is it's own function
########################################################################################################################################
@app.route("/Portal")
def portal():
  mydb = mydbfunc()

  # doesn't allow access if not logged in
  if "user_type" not in session:
    return redirect(url_for("login"))


  if session["user_type"] == "Student":
    return redirect(url_for("All_Student_Portal"))
  elif session["user_type"] == "GS":
    return redirect(url_for("All_GS_Portal"))
  elif session["user_type"] == "Faculty":
    return redirect(url_for("All_Faculty_Portal"))
  elif session["user_type"] == "Admin":
    return redirect(url_for("Sysadmin_Portal"))
  elif session["user_type"] == "Applicant":
    return redirect('/homeapps')
  elif session["user_type"] == "Alumni":
    return redirect(url_for('All_Alumni_Portal'))
  elif session["user_type"] == "Registrar":
    print("registrar")
    return redirect(url_for("Registrar_Portal"))
  else:
    print("error with user type in database")

  return redirect(url_for("login"))

########################################################################################################################################
  #ALL_STUDENT_PORTAL PAGE (ALL)
    #renders the All_Student_Portal HTML page which will have links to the REGS and ARGS student portals
########################################################################################################################################
@app.route("/All_Student_Portal",methods = ["GET", "POST"])
def All_Student_Portal():
  mydb=mydbfunc()
  cur = mydb.cursor(dictionary=True)
  id = session["uid"]
  print("student id: ", id )
  if session["user_type"] != "Student":
    return redirect(url_for("login"))
  
  # Fetch student information with user_id=id
  cur.execute("SELECT * FROM students JOIN users ON students.uid = users.uid WHERE students.uid = (%s)", (id,))
  student_info = cur.fetchone()

  if student_info is not None:
      cur.execute("SELECT fname, lname FROM users WHERE uid = (%s)", (student_info['advisor_id'],))
      advisor_info = cur.fetchone()
  else:
        advisor_info = None

  cur.execute("SELECT * FROM form1 WHERE user_id = (%s) LIMIT 1", (id,))
  form1_info = cur.fetchone()
  print ("Do they have any Form 1 info? ", form1_info)
  has_requested_grad = False
  print ("Has Requested Grad: ", has_requested_grad)
  if not form1_info:
      # If id not found, return an error message
      has_form1=False
  else:
      has_form1=True
  
  # Check if there is a grad_request for the student
  print("Do they have form 1?" ,has_form1)
  if has_form1 == True:
      
    cur.execute("SELECT * FROM grad_requests WHERE student_id = (%s)", (id,))
    grad_request_info = cur.fetchone()
    if not grad_request_info:
      has_requested_grad = False
    else:
      has_requested_grad = True
  return render_template("All_Student_Portal.html", x=student_info, 
                            adname=advisor_info,
                            has_form1 = has_form1,
                            has_requested_grad = has_requested_grad,  user_type=session['user_type'])

########################################################################################################################################
  #ALL_GS_PORTAL PAGE (ALL)
    #renders the All_GS_Portal HTML page which will have links to the APPS, REGS and ARGS student portals
########################################################################################################################################
@app.route("/All_GS_Portal")
def All_GS_Portal():
  if "user_type" not in session:
    return redirect('/')
  if session["user_type"] != "GS":
    return redirect(url_for("login"))
  return render_template("All_GS_Portal.html")

########################################################################################################################################
  #ALL_ALUMNI_PORTAL PAGE (ALL)
    #renders theALL_ALUMNI_PORTAL PAGE HTML page which will have links to their trancsripts APPS
########################################################################################################################################
@app.route('/All_Alumni_Portal', methods=['GET'])
def All_Alumni_Portal():
    mydb = mydbfunc()
    id = session["uid"]
    cur = mydb.cursor(dictionary=True)
    cur.execute("SELECT * FROM users WHERE uid = (%s)", (id,))
    y = cur.fetchone()
    
    return render_template("All_Alumni_Portal.html", x=y)
########################################################################################################################################
  #ALL_FACULTY_PORTAL PAGE (ALL)
    #renders the All_Faculty_Portal HTML page which will have links to the APPS, REGS and ARGS student portals
    #slightly different to the GS and Student portals as what is on the HTML page will depend on what privileges the faculty has
########################################################################################################################################
@app.route("/All_Faculty_Portal")
def All_Faculty_Portal():
  mydb = mydbfunc()
  if "user_type" not in session:
    return redirect('/')
  if session["user_type"] != "Faculty":
    return redirect(url_for("login"))
  mydb = mydbfunc()
  cursor = mydb.cursor(dictionary = True)

  cursor.execute("SELECT * FROM faculty WHERE uid = (%s)", (session["uid"], ))
  privileges = cursor.fetchall()

  return render_template("All_Faculty_Portal.html", privileges = privileges[0])

########################################################################################################################################
  #REGS GS PORTAL PAGE (REGS)
    #portal for the REGS functionality of the GS (linked to on the All_GS_Portal page)
      #allows GS to look for all students
########################################################################################################################################
@app.route("/GS_Portal", methods = ["GET", "POST"])
def GS_Portal():
  mydb = mydbfunc()
  if "user_type" not in session:
    return redirect('/')
  #redirects to login if user not gradsec
  if session["user_type"] != "GS":
    return redirect(url_for("login"))

  cursor = mydb.cursor(dictionary = True)

  # setup for looking up students
  session["GS_Lookup_Results"] = []
  first_name = "%"
  last_name = "%"
  uid = "%"
  program1 = "student_p"
  program2 = "student_m"

  # edit first name
  if request.method == 'POST' and 'edit_first_name' in request.form:
    if request.form['new_first_name'] != '':
      cursor.execute('UPDATE users SET fname = %s WHERE uid = %s', (request.form['new_first_name'], session['uid']))
      session['first_name'] = request.form['new_first_name']
      mydb.commit()
      cursor.close()
  
  # edit last name
  elif request.method == 'POST' and 'edit_last_name' in request.form:
    if request.form['new_last_name'] != '':
      cursor.execute('UPDATE users SET lname = %s WHERE uid = %s', (request.form['new_last_name'], session['uid']))
      session['last_name'] = request.form['new_last_name']
      mydb.commit()
      cursor.close()   
  # edit address
  elif request.method == 'POST' and 'edit_address' in request.form:
    if request.form['new_address'] != '':
      cursor.execute('UPDATE users SET address = %s WHERE uid = %s', (request.form['new_address'], session['uid']))
      mydb.commit()
      cursor.close()
      session['address'] = request.form['new_address']
  # edit password
  elif request.method == 'POST' and 'edit_password' in request.form:
    if request.form['new_password'] != '':
      cursor.execute('UPDATE users SET password = %s WHERE uid = %s', (request.form['new_password'], session['uid']))
      mydb.commit()
      cursor.close()
      session['password'] = request.form['new_password']
  
  # allows grad sec to look up students
    # TODO: maybe add error display for form validation?
  elif request.method == 'POST':
    lookup_results = None
    first_name = "%"
    last_name = "%"
    uid = "%"

    if request.form['first_name'] != '':
      first_name = request.form['first_name']
    if request.form['last_name'] != '':
      last_name = request.form['last_name']
    if request.form['uid'] != '':
      uid = request.form['uid']
    
    # if searching based on program needs to run a different query to access student table
    if request.form['program'] != '':
      req = request.form["program"]
      if req == "PHD" or req == "phd" or req == "Phd":
        cursor.execute("SELECT * FROM users LEFT JOIN students ON users.uid = students.uid WHERE users.fname LIKE (%s) and users.lname LIKE (%s) and users.uid LIKE (%s) AND students.degree LIKE (%s)", (first_name, last_name, uid, "PHD"))
        lookup_results = cursor.fetchall()
      elif req == "Master" or req == "Masters" or req == "master" or req == "masters" or req == "MS" or req == "ms":
        program = "student_m"
        cursor.execute("SELECT * FROM users LEFT JOIN students ON users.uid = students.uid WHERE users.fname LIKE (%s) and users.lname LIKE (%s) and users.uid LIKE (%s) AND students.degree LIKE (%s)", (first_name, last_name, uid, "Masters"))
        lookup_results = cursor.fetchall()
      else:
        print("error, invalid program input")
        # TODO: add error display in HTML

    # searching for all students (doesnt need to access student table) 
    else:
      cursor.execute("SELECT * FROM users WHERE fname LIKE (%s) and lname LIKE (%s) and uid LIKE (%s) and user_type LIKE (%s)", (first_name, last_name, uid, "Student"))
      lookup_results = cursor.fetchall()
      #lookup_results = cursor.fetchall()

    if lookup_results != None:
      for student in lookup_results:
        session["GS_Lookup_Results"].append(student)

  return render_template("GS_Portal.html")

########################################################################################################################################
  #MANAGE COURSE CATALOGUE PAGE (REGS)
    #lets the user manage the course catalogue (not individual sections) by editing, adding, or deleting whole classes
      #both sysadmin and registrar can do this
      #TODO: (for REGS) make sure errors display and clear correctly
########################################################################################################################################
@app.route("/Class_Add", methods = ["GET", "POST"])
def Add_Class():
  # redirects if user not sysadmin
  if "user_type" not in session:
    return redirect('/')
  if not (session["user_type"] == "Admin" or session["user_type"] == "Registrar"):
    return redirect(url_for("login"))

  mydb = mydbfunc()
  cursor = mydb.cursor(dictionary = True)

  cursor.execute("SELECT * FROM classes")
  all_classes = cursor.fetchall()

  session["ClassAddError"] = ""
  session["ClassEditError"] = ""

  if request.method == "POST":
    # FUNCTIONALITY FOR EDITING AN EXISTING CLASS
    if "edit classes" in request.form:
      dept = request.form["dept"]
      num = request.form["num"]
      title = request.form["title"]
      credit = request.form["credits"]

      cid = request.form["CID_cid"]
      cursor.execute("SELECT * FROM classes")
      all_classes = cursor.fetchall()

      conflict = False
      # checks if any fields were left empty
      if dept == "" or num == "" or title == "" or credit == "":
        conflict = True
        session["ClassEditError"] = "Please Fill in All Fields"
      else:
        # compares for conflicts with existing classes
        for class1 in all_classes:
          if dept == class1["department"] and num == str(class1["class_num"]) and cid != class1["cid"]:
            conflict = True
            session["ClassEditError"] = "A class already exists with that combination of department and class number. It is " + class1["class_title"] 
          elif title == class1["class_title"] and cid != class1["cid"]:
            conflict = True
            session["ClassEditError"] = "A class already exists with that title. It is " + class1["department"] + " " + str(class1["class_num"])

      if conflict == False:
        cursor.execute("UPDATE classes SET department = %s, class_num = %s, class_title = %s, credit_hours = %s WHERE cid = %s", (dept, num, title, credit, cid))
        mydb.commit()
        session["ClassEditError"] = ""
        return redirect(url_for("Add_Class"))

    # FUNCTIONALITY FOR ADDING A NEW CLASS
    else:
      cid = request.form["cid"]
      dept = request.form["dept"]
      num = request.form["class_num"]
      title = request.form["title"]
      credit = request.form["credits"]

      cursor.execute("SELECT * FROM classes")
      all_classes = cursor.fetchall()

      conflict = False
      # checks if any fields were left empty
      if cid == "" or dept == "" or num == "" or title == "" or credit == "":
        conflict = True
        session["ClassAddError"] = "Please Fill in All Fields"
      else:
        # compares for conflicts with existing classes
        for class1 in all_classes:
          if cid == str(class1["cid"]):
            conflict = True
            session["ClassAddError"] = "A class already exists with that CID"
          elif dept == class1["department"] and num == str(class1["class_num"]):
            conflict = True
            session["ClassAddError"] = "A class already exists with that combination of department and class number. It is " + class1["class_title"] 
          elif title == class1["class_title"]:
            conflict = True
            session["ClassAddError"] = "A class already exists with that title. It is " + class1["department"] + " " + str(class1["class_num"])

      # adds class if no conflicts
      if conflict == False:
        session["error"] = ""
        cursor.execute("INSERT INTO classes (cid, department, class_num, class_title, credit_hours) VALUES (%s, %s, %s, %s, %s)", (int(cid), dept, int(num), title, int(credit)))
        mydb.commit()
        return redirect(url_for("Add_Class"))

  return render_template("Class_Add.html", all_classes = all_classes)


################################################################
  #MAKES SURE THE valid_semesters DATABASE IS SET UP CORRECTLY
################################################################
def valid_sem_integrity():
  mydb = mydbfunc()
  cursor = mydb.cursor(dictionary = True)

  cursor.execute("SELECT * FROM valid_semesters")
  semesters = cursor.fetchall()

  at_current = False
  for sem in semesters:
    if sem["current_sem"] == "T" and at_current == False:
      at_current = True
      cursor.execute("UPDATE valid_semesters SET is_done = 'F', can_register = 'T' WHERE year = %s and semester = %s", (sem["year"], sem["semester"]))
    elif at_current == False:
      cursor.execute("UPDATE valid_semesters SET is_done = 'T', can_register = 'F' WHERE year = %s and semester = %s", (sem["year"], sem["semester"]))
    else:
      cursor.execute("UPDATE valid_semesters SET is_done = 'F', current_sem = 'F' WHERE year = %s and semester = %s", (sem["year"], sem["semester"]))
    mydb.commit()

########################################################################################################################################
  #MANAGE SECTIONS PAGE (REGS)
    #lets the user manage the sections being offered by editing, adding (from course catalogue) or deleting
      #both they sysadmin and registrar can do this
########################################################################################################################################
@app.route("/Section_Add", methods = ["GET", "POST"])
def Section_Add():
  if "user_type" not in session:
    return redirect('/')
  session["error"] = ""
  session["errorAdd"] = ""
  # redirects if user not sysadmin
  if not (session["user_type"] == "Admin" or session["user_type"] == "Registrar"):
    return redirect(url_for("login"))

  mydb = mydbfunc()
  cursor = mydb.cursor(dictionary = True)

  #GET POSSIBLE SEMESTERS AND YEARS AND SET CURRENT SEMESTER
  valid_sem_integrity()
  cursor.execute("SELECT * FROM valid_semesters")
  semesters = cursor.fetchall()
  cursor.execute("SELECT * FROM valid_semesters WHERE current_sem = 'T'")
  current_sem = cursor.fetchall()
  current_sem = current_sem[0]

  possible_years = []
  for sem in semesters:
    if sem["year"] not in possible_years:
      possible_years.append(sem["year"])


  if "section_sem" not in session:
    session["section_sem"] = current_sem["semester"]
  if "section_year" not in session:
    session["section_year"] = current_sem["year"]

  cursor.execute("SELECT * FROM valid_semesters WHERE year = %s and semester = %s", (session["section_year"], session["section_sem"]))
  can_edit = cursor.fetchall()
  can_edit = can_edit[0]
  if can_edit["is_done"] == "F" and can_edit["can_register"] == "F":
    can_edit = "T"
  elif can_edit["is_done"] == "T":
    can_edit = "can not edit semesters which have been completed"
  elif can_edit["can_register"] == "T":
    can_edit = "can not edit semesteres for which registration is open"

  cursor.execute("SELECT * FROM classes LEFT JOIN current_sections ON classes.cid = current_sections.cid WHERE (current_sections.year = %s and current_sections.semester = %s) or (current_sections.cid IS NULL)", (session["section_year"], session["section_sem"]))
  all_sections = cursor.fetchall()
  # print(all_sections)
  for section in all_sections:
    if section["cid"] == None:
      cursor.execute("SELECT * FROM classes WHERE department = %s and class_num = %s", (section["department"], section["class_num"]))
      cid = cursor.fetchone()
      section["cid"] = cid["cid"]

  if request.method == "POST":
    # SETS TO DESIRED YEAR AND SEMESTER
    if "set_sem_year" in request.form:
      session["section_year"] = request.form["year"]
      session["section_sem"] = request.form["sem"]
      print(session["section_year"])
      cursor.execute("SELECT * FROM classes LEFT JOIN current_sections ON classes.cid = current_sections.cid WHERE (current_sections.year = %s and current_sections.semester = %s) or (current_sections.cid IS NULL)", (session["section_year"], session["section_sem"]))
      all_sections = cursor.fetchall()
      for section in all_sections:
        if section["cid"] == None:
          cursor.execute("SELECT * FROM classes WHERE department = %s and class_num = %s", (section["department"], section["class_num"]))
          cid = cursor.fetchone()
          section["cid"] = cid["cid"]
      
      # cursor.execute("SELECT * FROM valid_semesters WHERE year = %s and semester = %s", (session["section_year"], session["section_sem"]))
      # can_edit = cursor.fetchone()
      # can_edit = can_edit["can_register"]
      return redirect(url_for("Section_Add"))
    # EDITING SECTION FUNCTIONALITY
    elif "edit" in request.form:
      sectid = request.form["sect_id"]
      profuid = request.form["prof_uid"]
      day = request.form["day"]
      time = request.form["time"]

      conflict = False
      cursor.execute("SELECT * FROM users WHERE uid = %s AND user_type = %s", (profuid, "faculty"))
      results = cursor.fetchall()

      if len(results) == 0:
        conflict = True
        session["error"] = "Invalid Professor ID"
      # else:
      #   cursor.execute("SELECT * FROM current_sections WHERE professor_uid = %s and year = %s and semester = %s", (profuid, session["section_year"], session["section_sem"]))
      #   prof_classes = cursor.fetchall()
      #   for class1 in prof_classes:
      #     if abs(class1["timeslot"] - int(time)) != 2 and sectid != class1["section_id"] and class1["day"] == day:
      #       conflict =  True
      #       print("overlap error")
      #       session["error"] = "The Professor is already teaching a class at that time"

      if conflict == False:
        cursor.execute("UPDATE current_sections SET professor_uid = %s, day = %s, timeslot = %s WHERE section_id = %s", (profuid, day, time, sectid))
        mydb.commit()
        return redirect(url_for("Section_Add"))

    else:
      session["errrorAdd"] = ""
      cid = int(request.form["cid"])
      sect = request.form["sect"]
      profuid = request.form["prof_uid"]
      year = session["section_year"]
      sem = session["section_sem"]
      day = request.form["day"]
      time = request.form["time"]
      section_id_frankenstein = str(year) + "-" + str(sem) + "-" + str(cid) + "-" + str(sect)

      conflict = False
      if cid == "" or sect == "" or profuid == "":
        conflict = True
        session["errorAdd"] = "Please Fill in All Fields"

      cursor.execute("SELECT * FROM current_sections")
      sections = cursor.fetchall()
      
      foundCID = False
      for section in sections:
        if section["cid"] == int(cid):
          foundCID = True
          # SPLICE SECTION_ID
          spliced = section["section_id"].split("-")
          splicedSection = spliced[3]

          if section["section_id"] == section_id_frankenstein:
            conflict = True
            session["errorAdd"] = "A Section already exists in the selected semester with that section. Please enter a different section"
    
      
      if foundCID == False:
        conflict = True
        session["errorAdd"] = "No Class Found With CID " + str(cid)

      if conflict == False:
        cursor.execute("INSERT INTO current_sections (cid, section_id, professor_uid, year, semester, day, timeslot) VALUES (%s, %s, %s, %s, %s, %s, %s)", (cid, section_id_frankenstein, profuid, year, sem, day, time))
        mydb.commit()
        session["error"] = ""
        return redirect(url_for("Section_Add"))
    


  return render_template("Section_Add.html", all_sections = all_sections, possible_years = possible_years, can_edit = can_edit) 

########################################################################################################################################
  #REGS SYSADMIN PORTAL PAGE (ALL)
    #portal for the REGS functionality of the Sysadmin
    #TODO: (for ALL) make sure this portal page has links to allow the sysadmin to do whatever anyone else can do
    #TODO: (for REGS) make sure this updates correctly
    #TODO: (for ALL) make sure add user works correctly
########################################################################################################################################
@app.route("/Sysadmin_Portal", methods = ["GET", "POST"])
def Sysadmin_Portal():
  mydb = mydbfunc()
  cursor = mydb.cursor(dictionary = True)
  if "user_type" not in session:
    return redirect('/')
  if session["user_type"] != 'Admin':
    return redirect('/')


  return render_template("Sysadmin_Portal.html")

@app.route("/manage_semesters", methods = ["GET", "POST"])
def manage_semesters():
  mydb = mydbfunc()
  cursor = mydb.cursor(dictionary = True)
  if "user_type" not in session:
    return redirect('/')
  if session["user_type"] not in ['Admin', 'Registrar']:
    return redirect('/')

  # lets sysadmin set current semester/year and which semesters can be registered for
  cursor.execute("SELECT * FROM valid_semesters ORDER BY year")
  valid_sems = cursor.fetchall()

  current_year = 0
  current_sem = "0"
  for sem in valid_sems:
    if sem["current_sem"] == "T":
      current_year = sem["year"]
      current_sem = sem["semester"]

  if request.method == "POST":
    #CHANGE CURRENT SEMESTER
    if request.form["Form_Type"] == "edit_current":
      year = request.form["year"]
      sem = request.form["sem"]
      #removes past current semester
      cursor.execute("UPDATE valid_semesters SET current_sem = 'F', can_register = 'F' WHERE current_sem = 'T'")
      #sets selected semester to current semester
      cursor.execute("UPDATE valid_semesters SET current_sem = 'T', can_register = 'T'  WHERE year = %s AND semester = %s", (year, sem))
      mydb.commit()
      valid_sem_integrity()
      return redirect(url_for("manage_semesters"))

    #CHANGE REGISTRATION POSSIBILITIES
    elif request.form["Form_Type"] == "set_registration":
      year = request.form["year"]
      sem = request.form["sem"]
      register = request.form["can_register"]
      cursor.execute("UPDATE valid_semesters SET can_register = %s WHERE year = %s AND semester = %s", (register, year, sem))
      mydb.commit()
      return redirect(url_for("manage_semesters"))


  return render_template("manage_semesters.html", valid_sems = valid_sems)
  
  # session["SysAdminError"] = ""
  
  # #redirects to login if user not sysadmin
  # if session["user_type"] != "Admin":
  #   return redirect("/")

  # #lets sysadmin set current semester/year and which semesters can be registered for
  # cursor.execute("SELECT * FROM valid_semesters ORDER BY year")
  # valid_sems = cursor.fetchall()

  # current_year = 0
  # current_sem = "0"
  # for sem in valid_sems:
  #   if sem["current_sem"] == "T":
  #     current_year = sem["year"]
  #     current_sem = sem["semester"]
      
  # session["sysadmin_Lookup_Results"] = []
  # first_name = "%"
  # last_name = "%"
  # uid = "%"
  # user_type = "%"

  # if request.method == 'POST':
  #   if request.form["Form_Type"] == "search":
  #     first_name = "%"
  #     last_name = "%"
  #     uid = "%"
  #     user_type = "%"

  #     if request.form['first_name'] != '':
  #       first_name = request.form['first_name']
  #     if request.form['last_name'] != '':
  #       last_name = request.form['last_name']
  #     if request.form['uid'] != '':
  #       uid = request.form['uid']
  #     if request.form['user_type'] != "":
  #       req = request.form["user_type"]
  #       if req == "faculty" or req =="Faculty":
  #         user_type = "faculty"
  #       elif req == "student" or req == "Student":
  #         user_type = "student%" 
  #       elif req == "GS" or req == "gs" or req == "Gs" or req == "grad sec" or req == "Grad Sec":
  #         user_type = "grad_sec"
  #       elif req == "sysadmin" or req == "sys admin":
  #         user_type = "sysadmin"
  #     if request.form['program'] != '':
  #       req = request.form["program"]
  #       if req == "PHD" or req == "phd" or req == "Phd":
  #         user_type = "student_p"
  #       elif req == "Master" or req == "Masters" or req == "master" or req == "masters" or req == "MS" or req == "ms":
  #         user_type = "student_m"
    
  #     cursor.execute("SELECT * FROM users WHERE fname LIKE (%s) and lname LIKE (%s) and uid LIKE (%s) and user_type LIKE (%s)", (first_name, last_name, uid, user_type))
  #     lookup_results = cursor.fetchall()
  #     for user in lookup_results:
  #       session["sysadmin_Lookup_Results"].append(user)
    
  #   elif request.form["Form_Type"] == "add user":
  #     uid = request.form["uid"]
  #     cursor.execute("SELECT uid FROM users")
  #     all_users = cursor.fetchall()
  #     error = False
  #     for user in all_users:
  #       if str(user["uid"]) == uid:
  #         error = True
  #         session["SysAdminError"] = "uid already taken"

  #     fn = request.form["fname"]
  #     mi = request.form["minit"]
  #     ln = request.form["lname"]
  #     ad = request.form["address"]
  #     ut = request.form["user_type"]
  #     pw = "pass"

  #     if error == False:
  #       cursor.execute("INSERT INTO users (uid, password, fname, minit, lname, address, user_type) VALUES (%s, %s, %s, %s, %s, %s, %s)", (uid, pw, fn, mi, ln, ad, ut))
  #       mydb.commit()
  #       session["SysAdminError"] = ""

  #   elif request.form["Form_Type"] == "delete user":
  #     cursor.execute("DELETE FROM users WHERE uid = %s", (request.form["userID"], ))
  #     mydb.commit()

  #   #CHANGE CURRENT SEMESTER
  #   elif request.form["Form_Type"] == "edit_current":
  #     year = request.form["year"]
  #     sem = request.form["sem"]
  #     #removes past current semester
  #     cursor.execute("UPDATE valid_semesters SET current_sem = 'F', can_register = 'F' WHERE current_sem = 'T'")
  #     #sets selected semester to current semester
  #     cursor.execute("UPDATE valid_semesters SET current_sem = 'T', can_register = 'T'  WHERE year = %s AND semester = %s", (year, sem))
  #     mydb.commit()
  #     valid_sem_integrity()
  #     return redirect(url_for("Sysadmin_Portal"))

  #   #CHANGE REGISTRATION POSSIBILITIES
  #   elif request.form["Form_Type"] == "set_registration":
  #     year = request.form["year"]
  #     sem = request.form["sem"]
  #     register = request.form["can_register"]
  #     cursor.execute("UPDATE valid_semesters SET can_register = %s WHERE year = %s AND semester = %s", (register, year, sem))
  #     mydb.commit()
  #     return redirect(url_for("Sysadmin_Portal"))

  #   else:
  #     user_id = request.form["userID"]
  #     fn = request.form["first_name"]
  #     mi = request.form["middle_initial"]
  #     ln = request.form["last_name"]
  #     ad = request.form["address"]
  #     ut = request.form["user_type"]
  #     cursor.execute("UPDATE users SET fname = (%s), minit = (%s), lname = (%s), address = (%s), user_type = (%s), WHERE uid = (%s)", (fn, mi, ln, ad, ut, user_id))
  #     mydb.commit()

  #     cursor.execute("SELECT * FROM users WHERE fname LIKE (%s) and lname LIKE (%s) and uid LIKE (%s) and user_type LIKE (%s)", (first_name, last_name, uid, user_type))
  #     lookup_results = cursor.fetchall()
  #     for user in lookup_results:
  #       session["sysadmin_Lookup_Results"].append(user)


  # # cursor.execute("SELECT * FROM users")
  # # users = cursor.fetchall()

  # return render_template("Sysadmin_Portal.html", users=users, valid_sems = valid_sems)

########################################################################################################################################
  #PRE-REQ CHECK FUNCTION (does not have an HTML page) (REGS)
   #is called on the REGS student portal page, determines wether or not a student is eligible to register for a class 
    #conflicts are: time, pre-req, and already taking
########################################################################################################################################
def prereq_check(section_id, sem, year):
  print()
  print("CHECKING FOR:")
  print(section_id)
  print(sem)
  print(year)
  print()
  mydb = mydbfunc()
  cursor = mydb.cursor(dictionary=True)

  ad_hold = advising_Hold_Status(session["uid"])

  cursor.execute('SELECT * FROM current_sections JOIN classes ON current_sections.cid = classes.cid WHERE current_sections.section_id = %s',
                (section_id, ))
  course = cursor.fetchone()

  eligable = "YES"
  cursor.execute('SELECT prereq_cid FROM prerequisites WHERE class_cid = %s', (course['cid'], ))
  prereqs = cursor.fetchall()

  if ad_hold == "no hold":
    cursor.execute('SELECT * FROM student_classes LEFT JOIN current_sections ON student_classes.section_id = current_sections.section_id WHERE student_uid = %s', (session['uid'], ))
    courses_taken = cursor.fetchall()
  else:
    cursor.execute("SELECT * FROM advisor_hold_classes LEFT JOIN current_sections ON advisor_hold_classes.section_id = current_sections.section_id WHERE student_uid = %s", (session["uid"],))
    courses_taken = cursor.fetchall()
  # print(section_id)
  # print(courses_taken)
  # print(prereqs)
  # print()

  cids_taken = []
  for course1 in courses_taken:
    cids_taken.append(course1["cid"])

  # for prereq in prereqs:
  #   if prereq["prereq_cid"] not in cids_taken:
  #     eligable = "MISSING PRE-REQ"
  for prereq in prereqs:
    found = False
    for course1 in courses_taken:
      print(course1)
      if (prereq["prereq_cid"] == course1["cid"]) and (int(course1["year"]) != int(year) and course1["semester"] != sem):
        found = True
    if found == False:
      eligable = "MISSING PRE-REQ"

          
  if course["cid"] in cids_taken:
    eligable = "ALREADY TOOK A CLASS WITH THIS COURSE NUMBER"
  
  if session['user_type'] == 'student_p' and int(course['class_num']) < 6000:
    eligable = "TOO LOW COURSE NUMBER"

  if ad_hold == "no hold":
    cursor.execute('''
    SELECT *
    FROM current_sections 
      JOIN classes ON classes.cid = current_sections.cid 
      JOIN users ON users.uid = current_sections.professor_uid
      JOIN student_classes ON student_classes.section_id = current_sections.section_id
    WHERE current_sections.year = %s 
      AND current_sections.semester = %s 
      AND student_classes.student_uid = %s''', 
                  (year, sem, session["uid"],))
    current_classes = cursor.fetchall()
  else:
    cursor.execute('''
    SELECT *
    FROM current_sections 
      JOIN classes ON classes.cid = current_sections.cid 
      JOIN users ON users.uid = current_sections.professor_uid
      JOIN advisor_hold_classes ON advisor_hold_classes.section_id = current_sections.section_id
    WHERE current_sections.year = %s 
      AND current_sections.semester = %s 
      AND advisor_hold_classes.student_uid = %s''', 
                  (year, sem, session["uid"],))
    current_classes = cursor.fetchall()
    
  print(course)
  for c in current_classes:
    if c['day'] == course['day'] and (abs(int(c['timeslot']) - int(course['timeslot'])) != 2):
      eligable = "TIME OVERLAP"
    if c['cid'] == course['cid']:
      eligable = "ALREADY TAKING CLASS"

  return eligable

########################################################################################################################################
  #CLASS SEARCH FUNCTION (does not have an HTML page) (REGS)
  #is called on the REGS student portal page when a student searches for a class
    #returns a list of classes that fit the criteria (does not include classes currently being taken)
########################################################################################################################################
def classes_search(sem, year, department = "%", title = "%", number = "%"):
  mydb = mydbfunc()
  cursor = mydb.cursor(dictionary=True)
    
  cursor.execute('''
  SELECT * 
  FROM current_sections 
    JOIN classes ON classes.cid = current_sections.cid 
    JOIN users ON users.uid = current_sections.professor_uid
  WHERE current_sections.year = %s 
    AND current_sections.semester = %s 
    AND classes.department LIKE (%s) 
    AND classes.class_title LIKE (%s) 
    AND classes.cid LIKE (%s)''',
                 (year, sem, department, title, number))
  all_classes = cursor.fetchall()

  cursor.execute('''
  SELECT current_sections.section_id 
  FROM current_sections 
    JOIN classes ON classes.cid = current_sections.cid 
    JOIN users ON users.uid = current_sections.professor_uid
    JOIN student_classes ON student_classes.section_id = current_sections.section_id
  WHERE current_sections.year = %s 
    AND current_sections.semester = %s 
    AND student_classes.student_uid = %s''', 
                 (year, sem, session["uid"],))
  current_classes = cursor.fetchall()

  session['lookup_results_classes'] = []
  for course in all_classes:
    if {'section_id': course['section_id']} not in current_classes:
      course['eligable'] = prereq_check(course['section_id'], sem, year)
      session['lookup_results_classes'].append(course)

#####################################################################################
  #CHECKS STATUS OF STUDENTS ADVISOR HOLD
    # options:
      # no hold --> normal student who has registered for classes in the past
      # hold submitted --> form has been submitted but has not been accepted
      # hold in progress --> form has not been submitted
      # hold approved --> hold has been accepted, button to register for all classes
#####################################################################################
def advising_Hold_Status(Student_UID):
  mydb = mydbfunc()
  cursor = mydb.cursor(dictionary=True)
  
  cursor.execute("SELECT * FROM student_classes WHERE student_uid = %s", (Student_UID,))
  classes = cursor.fetchall()

  if len(classes) > 0:
    return "no hold"

  cursor.execute("SELECT * FROM advisor_hold_classes WHERE student_uid = %s", (Student_UID,))
  hold_list = cursor.fetchall()
  
  if len(hold_list) == 0:
    return "hold in progress"
  
  if hold_list[0]["submitted"] == "F":
    return "hold in progress"
  
  if hold_list[0]["approved"] == "F":
    return "hold submitted"
  
  if hold_list[0]["approved"] == "T":
    return "hold approved"

  print("weird error shouldnt have gotten here")
  return "error"

#####################################################################################
  #CHECKS IF CURRENT USER IS A GIVEN STUDENTS ADVISOR
    #returns yes if user is students advisor
    #returns student if user is student
    #returns no if user is
    #TODO: using this for advising hold form rn, add that sysadmin, GS, and registrar can see?
#####################################################################################
def checkIfAdvisor(student_uid):
  mydb = mydbfunc()
  cursor = mydb.cursor(dictionary=True)
  cursor.execute("SELECT * FROM students WHERE uid = %s", (student_uid,))
  student_info = cursor.fetchone()
  if session["uid"] == student_info["advisor_id"]:
    print("advisor match")
    return "advisor"

  if session["user_type"] in ["Admin", "Registrar"]:
    return "admin"

  if str(session["uid"]) == str(student_uid):
    return "student"
  
  return "no"

########################################################################################################################################
  #ADVISING HOLD FORM PAGE (advisor view) (ADS + REGS)
    #allows an advisor (or student) to view the 
########################################################################################################################################
@app.route("/Advising_Hold_Form<student_uid>", methods = ["GET", "POST"])
def Advising_Hold_Form(student_uid):
  mydb = mydbfunc()
  cursor = mydb.cursor(dictionary=True)

  if "user_type" not in session:
    return redirect("/")
 

  if checkIfAdvisor(student_uid) == "no":
    print("not student or advisor")
    return redirect("/")
  
  if (advising_Hold_Status(student_uid) != "hold submitted" and session["user_type"] == "Student"):
    print("don't need access as a student")
    print(advising_Hold_Status(student_uid))
    return redirect("/")



  cursor.execute("SELECT * FROM advisor_hold_classes WHERE student_uid = %s", (student_uid,))
  student_classes = cursor.fetchall()

  cursor.execute("SELECT * FROM users LEFT JOIN students ON users.uid = students.uid WHERE users.uid = %s", (student_uid,))
  student_info = cursor.fetchone()

  if advising_Hold_Status(student_uid) == "no hold" or advising_Hold_Status(student_uid) == "hold in progress":
    print("huh")
    return render_template("View_Advisor_Hold_Form.html", student_info = student_info, sem = 0, year = 0, hold_status = "none")

  sem = student_classes[0]["semester"]
  year = student_classes[0]["year"]

  # Make the schedule
  session['schedule'] = []
  cursor.execute("SELECT * FROM advisor_hold_classes JOIN classes ON classes.cid = advisor_hold_classes.cid JOIN current_sections ON advisor_hold_classes.section_id = current_sections.section_id WHERE advisor_hold_classes.student_uid = %s AND current_sections.year = %s AND current_sections.semester = %s", (student_uid, year, sem))
  classes_taking = cursor.fetchall()
  for i in [1, 2, 3]:
    partial = []
    for j in ['M', 'T', 'W', 'R', 'F']:
      added = False
      for k in classes_taking:
        if int(k['timeslot']) == i and k['day'] == j:
          added = True
          partial.append([k['class_title'], k['section_id'], k['cid']])
      if added == False:
        partial.append(['free period', 'none', 'none'])
    session['schedule'].append(partial)
  session['different_periods'] = ['3-5:30pm', '4-6:30pm', '6-8:30pm']
  session['different_periods_2'] = ['blank', '3-5:30pm', '4-6:30pm', '6-8:30pm']

  classes_search(sem, year)

  ad_hold = advising_Hold_Status(student_uid)
  if ad_hold == "hold submitted":
    hold_status = "submitted"
  elif ad_hold == "hold accepted":
    hold_status = "accepted"
  else:
    hold_status = "none"

  if request.method == "POST":
    if "accepting form" in request.form:
      print("HELLO ACCEPTED")
      cursor.execute("UPDATE advisor_hold_classes SET approved = 'T' WHERE student_uid = %s", (student_uid,))
      mydb.commit()
      return redirect(url_for("Advising_Hold_Form", student_uid = student_uid))
    else:
      print("HELLO DELETED")
      cursor.execute("DELETE FROM advisor_hold_classes WHERE student_uid = %s", (student_uid, ))
      mydb.commit()
      return redirect(url_for("Advising_Hold_Form", student_uid = student_uid))

  return render_template("View_Advisor_Hold_Form.html", student_info = student_info, sem = sem, year = year, hold_status = hold_status)



########################################################################################################################################
  #REGS STUDENT PORTAL PAGE (REGS)
    #portal for the REGS functionality of students (linked to on the All_Student_Portal page)
    #SHOWS UP WHEN THE PROPOOSED ADVISING HOLD FORM HAS BEEN SUBMITTED
      #shows message to be patient
########################################################################################################################################
@app.route('/Student_Portal_Submitted', methods = ["GET", "POST"])
def Student_Portal_Submitted():
  if "user_type" not in session:
    return redirect("/")
  if (session["user_type"] != "Student" or advising_Hold_Status(session["uid"]) != "hold submitted"):
    return redirect("/")

  return render_template("Student_Portal_Submitted.html")

########################################################################################################################################
  #REGS STUDENT PORTAL PAGE (REGS)
    #portal for the REGS functionality of students (linked to on the All_Student_Portal page)
    #SHOWS UP WHEN ADVISING HOLD FORM HAS NOT BEEN SUBMITTED
      #allows students to add to their advisor hold form (similar to registering normally)
      #allows students to submit their form
########################################################################################################################################
@app.route('/Student_Portal_Progress', methods = ["GET", "POST"])
def Student_Portal_Progress():
  mydb = mydbfunc()
  cursor = mydb.cursor(dictionary=True)
  if "user_type" not in session:
    return redirect("/")
  if (session["user_type"] != "Student" or advising_Hold_Status(session["uid"]) != "hold in progress"):
    return redirect("/")
  
    
  #GET POSSIBLE SEMESTERS AND YEARS 
  valid_sem_integrity()

  cursor.execute("SELECT * FROM valid_semesters WHERE can_register = 'T'")
  valid_sems = cursor.fetchall()

  cursor.execute("SELECT * FROM applications WHERE uid = %s", (session["uid"],))
  applicationinfo = cursor.fetchall()
  applicationinfo = applicationinfo[0]
  year = applicationinfo["year"]
  sem = applicationinfo["semester"]


  if "reg_sem" not in session:
    session["reg_sem"] = valid_sems[0]["semester"]
    # session["reg_sem"] = sem
  if "reg_year" not in session:
    # session["reg_year"] = year
    session["reg_year"] = valid_sems[0]["year"]

  session['different_periods_2'] = ['blank', '3-5:30pm', '4-6:30pm', '6-8:30pm']

  # Make the schedule
  session['schedule'] = []
  cursor.execute("SELECT * FROM advisor_hold_classes JOIN classes ON classes.cid = advisor_hold_classes.cid JOIN current_sections ON advisor_hold_classes.section_id = current_sections.section_id WHERE advisor_hold_classes.student_uid = %s AND current_sections.year = %s AND current_sections.semester = %s", (session['uid'], str(session['reg_year']), str(session['reg_sem'])))
  classes_taking = cursor.fetchall()
  for i in [1, 2, 3]:
    partial = []
    for j in ['M', 'T', 'W', 'R', 'F']:
      added = False
      for k in classes_taking:
        if int(k['timeslot']) == i and k['day'] == j:
          added = True
          partial.append([k['class_title'], k['section_id'], k['cid']])
      if added == False:
        partial.append(['free period', 'none', 'none'])
    session['schedule'].append(partial)
  session['different_periods'] = ['3-5:30pm', '4-6:30pm', '6-8:30pm']
  session['different_periods_2'] = ['blank', '3-5:30pm', '4-6:30pm', '6-8:30pm']

  classes_search(session["reg_sem"], session["reg_year"])

  can_submit = False
  if len(classes_taking) > 0:
    can_submit = True

  #CLASS LOOKUP
  if request.method == 'POST' and 'class_lookup' in request.form:
    department = '%'
    title = '%'
    number = '%'

    if request.form['department'] != '':
      department = request.form['department']
    if request.form['title'] != '':
      title = request.form['title']
    if request.form['number'] != '':
      number = request.form['number']
    
    classes_search(session["reg_sem"], session["reg_year"], department, title, number)
  
  # Allow users to pick the semester they want to see their schedule for
  elif request.method == 'POST' and 'set_sem_year' in request.form:
    sem = request.form["set_sem_year"]
    session['reg_sem'] = sem["semester"]
    session['reg_year'] = sem["year"]
    
    classes_search(session["reg_sem"], session["reg_year"])

    session['schedule'] = []
    cursor.execute("SELECT * FROM advisor_hold_classes JOIN classes ON classes.cid = advisor_hold_classes.cid JOIN current_sections ON advisor_hold_classes.section_id = current_sections.section_id WHERE advisor_hold_classes.student_uid = %s AND current_sections.year = %s AND current_sections.semester = %s", (session['uid'], str(session['reg_year']), str(session['reg_sem'])))
    classes_taking = cursor.fetchall()
    for i in [1, 2, 3]:
      partial = []
      for j in ['M', 'T', 'W', 'R', 'F']:
        added = False
        for k in classes_taking:
          if int(k['timeslot']) == i and k['day'] == j:
            added = True
            partial.append([k['class_title'], k['section_id'], k['cid']])
        if added == False:
          partial.append(['free period', 'none', 'none'])
      session['schedule'].append(partial)

    return redirect(url_for("Student_Portal"))

  elif "THIS IS A DROP" in request.form:
    cursor.execute("SELECT * FROM advisor_hold_classes LEFT JOIN current_sections ON advisor_hold_classes.section_id = current_sections.section_id LEFT JOIN classes ON advisor_hold_classes.cid = classes.cid WHERE student_uid = %s", (session["uid"],))
    classes = cursor.fetchall()
  
    session["current_semester"] = classes[0]["semester"]
    session["current_year"] = classes[0]["year"]
    semester = session["current_semester"]
    year = session["current_year"]
    day = request.form["day"]
    time = request.form["period"]
    sectid = request.form["sectid"]

    cursor.execute("DELETE FROM advisor_hold_classes WHERE student_uid = %s and section_id = %s", (session["uid"], sectid))
    mydb.commit()
    return redirect(url_for("Student_Portal"))

  #SUBMITS FORM TO ADVISOR
  elif "submitting form" in request.form:
    cursor.execute("UPDATE advisor_hold_classes SET submitted = 'T' WHERE student_uid = %s", (session["uid"], ))
    mydb.commit()
    return redirect(url_for("Student_Portal"))

  # ADDING A CLASS
  elif request.method == 'POST':
    print("adding")
    sectid = request.form["sectid"]
    print(sectid)
    cursor.execute("SELECT * FROM current_sections WHERE section_id = %s", (sectid,))
    class_info = cursor.fetchall()
    class_info = class_info[0]
    print(class_info)
    cursor.execute("INSERT INTO advisor_hold_classes VALUES (%s, %s, %s, %s, %s, %s, %s)", (int(session["uid"]), class_info["cid"], sectid, 'F', 'F', session["reg_year"], session["reg_sem"]))
    mydb.commit()
    session['schedule'] = []
    cursor.execute("SELECT * FROM advisor_hold_classes JOIN classes ON classes.cid = advisor_hold_classes.cid JOIN current_sections ON advisor_hold_classes.section_id = current_sections.section_id WHERE advisor_hold_classes.student_uid = %s AND current_sections.year = %s AND current_sections.semester = %s", (session['uid'], str(session['reg_year']), str(session['reg_sem'])))
    classes_taking = cursor.fetchall()
    for i in [1, 2, 3]:
      partial = []
      for j in ['M', 'T', 'W', 'R', 'F']:
        added = False
        for k in classes_taking:
          if int(k['timeslot']) == i and k['day'] == j:
            added = True
            partial.append([k['class_title'], k['section_id'], k['cid']])
        if added == False:
          partial.append(['free period', 'none', 'none'])
      session['schedule'].append(partial)

    session['different_periods'] = ['3-5:30pm', '4-6:30pm', '6-8:30pm']
    session['different_periods_2'] = ['blank', '3-5:30pm', '4-6:30pm', '6-8:30pm']
    
    classes_search(session["reg_sem"], session["reg_year"])
    return redirect(url_for("Student_Portal_Progress"))


  return render_template("Student_Portal_Progress.html", valid_sems = valid_sems, semesters = ["Spring", "Summer", "Fall"], can_submit = can_submit)

########################################################################################################################################
  #REGS STUDENT PORTAL PAGE (REGS)
    #portal for the REGS functionality of students (linked to on the All_Student_Portal page)
    #SHOWS UP WHEN THE PROPOOSED ADVISING HOLD FORM HAS BEEN APPROVED
      #shows all classes on form
      #button to add all classes to schedule
      #TODO: error check
########################################################################################################################################
@app.route('/Student_Portal_Approved', methods = ["GET", "POST"])
def Student_Portal_Approved():
  mydb = mydbfunc()
  cursor = mydb.cursor(dictionary=True)

  if "user_type" not in session:
    return redirect("/")
  if (session["user_type"] != "Student" or advising_Hold_Status(session["uid"]) != "hold approved"):
    return redirect("/")

  cursor.execute("SELECT * FROM advisor_hold_classes LEFT JOIN current_sections ON advisor_hold_classes.section_id = current_sections.section_id LEFT JOIN classes ON advisor_hold_classes.cid = classes.cid WHERE student_uid = %s", (session["uid"],))
  classes = cursor.fetchall()

  session['schedule'] = []
  for i in [1, 2, 3]:
    partial = []
    for j in ['M', 'T', 'W', 'R', 'F']:
      added = False
      for k in classes:
        if int(k['timeslot']) == i and k['day'] == j:
          added = True
          print(k['cid'])
          partial.append([k['class_title'], k['section_id'], k['cid']])
      if added == False:
        partial.append(['free period', 'none', 'none'])
    session['schedule'].append(partial)
  
  session['different_periods'] = ['3-5:30pm', '4-6:30pm', '6-8:30pm']
  session['different_periods_2'] = ['blank', '3-5:30pm', '4-6:30pm', '6-8:30pm']

  if request.method == "POST" and "submit" in request.form:
    print("POSTING")
    cursor.execute("DELETE FROM advisor_hold_classes WHERE student_uid = %s", (session["uid"],))
    mydb.commit()
    for class1 in classes:
      print(class1)
      cursor.execute("INSERT INTO student_classes VALUES (%s, %s, %s, %s)", (session["uid"], class1["cid"], class1["section_id"], "IP"))
      mydb.commit()

    # cursor.execute("SELECT * FROM advisor_hold_classes LEFT JOIN current_sections ON advisor_hold_classes.section_id = current_sections.section_id LEFT JOIN classes ON advisor_hold_classes.cid = classes.cid WHERE student_uid = %s", (session["uid"],))
    # classes = cursor.fetchall()
  
    # session["current_semester"] = classes[0]["semester"]
    # session["current_year"] = classes[0]["year"]
    return redirect(url_for("Student_Portal"))


  return render_template("Student_Portal_Approved.html", classes = classes)

########################################################################################################################################
  #REGS STUDENT PORTAL PAGE (REGS)
    #portal for the REGS functionality of students (linked to on the All_Student_Portal page)
    #SHOWS UP WHEN THERE IS NO ADVISING HOLD
      #allows add/drop classes and view schedule
  #TODO: (for REGS) add error if dropping class not successful
########################################################################################################################################
@app.route('/Student_Portal', methods = ['GET', 'POST'])
def Student_Portal():
  mydb = mydbfunc()
  cursor = mydb.cursor(dictionary=True)
  # doesn't allow access if not logged in as student
  if "user_type" not in session:
    return redirect("/")

  if session["user_type"] != "Student":
    print("user type")
    return redirect("/")

  ad_hold = advising_Hold_Status(session["uid"])

  if ad_hold == "hold in progress":
    print("in progress")
    return redirect(url_for("Student_Portal_Progress"))
  elif ad_hold == "hold submitted":
    print("submitted")
    return redirect(url_for("Student_Portal_Submitted"))
  elif ad_hold == "hold approved":
    print("approved")
    return redirect(url_for("Student_Portal_Approved"))


  #GET POSSIBLE SEMESTERS AND YEARS AND SET CURRENT SEMESTER
  valid_sem_integrity()
  cursor.execute("SELECT * FROM valid_semesters")
  semesters = cursor.fetchall()
  cursor.execute("SELECT * FROM valid_semesters WHERE current_sem = 'T'")
  current_sem = cursor.fetchall()
  current_sem = current_sem[0]

  possible_years = []
  for sem in semesters:
    if sem["year"] not in possible_years:
      possible_years.append(sem["year"])


  if "current_semester" not in session:
    print("set")
    session["current_semester"] = current_sem["semester"]
  if "current_year" not in session:
    session["current_year"] = current_sem["year"]

  cursor.execute("SELECT * FROM valid_semesters WHERE year = %s and semester = %s", (session["current_year"], session["current_semester"]))
  can_reg = cursor.fetchall()
  can_reg = can_reg[0]
  if can_reg["can_register"] == "T":
    can_reg = "True"
  

  # Make the schedule
  session['schedule'] = []
  cursor.execute('SELECT * FROM student_classes JOIN classes ON classes.cid = student_classes.cid JOIN current_sections ON student_classes.section_id = current_sections.section_id WHERE student_classes.student_uid = %s AND current_sections.year = %s AND current_sections.semester = %s',
                    (session['uid'], str(session['current_year']), str(session['current_semester'])))
  classes_taking = cursor.fetchall()
  for i in [1, 2, 3]:
    partial = []
    for j in ['M', 'T', 'W', 'R', 'F']:
      added = False
      for k in classes_taking:
        if int(k['timeslot']) == i and k['day'] == j:
          added = True
          partial.append([k['class_title'], k['section_id'], k['cid']])
      if added == False:
        partial.append(['free period', 'none', 'none'])
    session['schedule'].append(partial)
  
  session['different_periods'] = ['3-5:30pm', '4-6:30pm', '6-8:30pm']
  session['different_periods_2'] = ['blank', '3-5:30pm', '4-6:30pm', '6-8:30pm']

  classes_search(session["current_semester"], session["current_year"])

  #CLASS LOOKUP
  if request.method == 'POST' and 'class_lookup' in request.form:
    department = '%'
    title = '%'
    number = '%'

    if request.form['department'] != '':
      department = request.form['department']
    if request.form['title'] != '':
      title = request.form['title']
    if request.form['number'] != '':
      number = request.form['number']
    
    classes_search(session["current_semester"], session["current_year"], department, title, number)
  
  # Allow users to pick the semester they want to see their schedule for
  elif request.method == 'POST' and 'sem' in request.form:
    session['current_semester'] = int(request.form['sem'])
    session['current_year'] = int(request.form['year'])
    
    classes_search(session["current_semester"], session["current_year"], )

    session['schedule'] = []
    cursor.execute('SELECT * FROM student_classes JOIN classes ON classes.cid = student_classes.cid JOIN current_sections ON student_classes.section_id = current_sections.section_id WHERE student_classes.student_uid = %s AND current_sections.year = %s AND current_sections.semester = %s',
                    (session['uid'], str(session['current_year']), str(session['current_semester'])))
    classes_taking = cursor.fetchall()
    for i in [1, 2, 3]:
      partial = []
      for j in ['M', 'T', 'W', 'R', 'F']:
        added = False
        for k in classes_taking:
          if int(k['timeslot']) == i and k['day'] == j:
            added = True
            partial.append([k['class_title'], k['section_id'], k['cid']])
        if added == False:
          partial.append(['free period', 'none', 'none'])
      session['schedule'].append(partial)

    return redirect(url_for("Student_Portal"))

  elif "THIS IS A DROP" in request.form:
    semester = session["current_semester"]
    year = session["current_year"]
    day = request.form["day"]
    time = request.form["period"]
    sectid = request.form["sectid"]

    cursor.execute("SELECT grade FROM student_classes WHERE student_uid = %s and section_id = %s", (session["uid"], sectid))
    grade = cursor.fetchone()
    grade = grade["grade"]

    if grade == "IP":
      cursor.execute("DELETE FROM student_classes WHERE student_uid = %s and section_id = %s", (session["uid"], sectid))
      mydb.commit()
      return redirect(url_for("Student_Portal"))
    else:
      print("NO DROP")


  elif request.method == 'POST' and "sectid" in request.form:
    print("adding")
    sectid = request.form["sectid"]
    print(sectid)
    cursor.execute("SELECT * FROM current_sections WHERE section_id = %s", (sectid,))
    class_info = cursor.fetchall()
    class_info = class_info[0]
    print(class_info)
    cursor.execute("INSERT INTO student_classes VALUES (%s, %s, %s, %s)", (session["uid"], class_info["cid"], sectid, "IP"))
    mydb.commit()
    session['schedule'] = []
    print(session['schedule'])
    cursor.execute('SELECT * FROM student_classes JOIN classes ON classes.cid = student_classes.cid JOIN current_sections ON student_classes.section_id = current_sections.section_id WHERE student_classes.student_uid = %s AND current_sections.year = %s AND current_sections.semester = %s',
                    (session['uid'], str(session['current_year']), str(session['current_semester'])))
    classes_taking = cursor.fetchall()
    for i in [1, 2, 3]:
      partial = []
      for j in ['M', 'T', 'W', 'R', 'F']:
        added = False
        for k in classes_taking:
          if int(k['timeslot']) == i and k['day'] == j:
            added = True
            partial.append([k['class_title'], k['section_id'], k['cid']])
        if added == False:
          partial.append(['free period', 'none', 'none'])
      session['schedule'].append(partial)


    classes_search(session["current_semester"], session["current_year"])
  
  return render_template('Student_Portal.html', possible_years = possible_years, can_reg = can_reg)


########################################################################################################################################
  #REGS FACULTY PORTAL PAGE (REGS)
    #portal for the REGS functionality of Faculty (linked to on the All_Faculty_Portal page)
      #shows faculty schedule, and has links to class page which allows for grades to be edited
########################################################################################################################################
@app.route('/Faculty_Portal', methods = ['GET', 'POST'])
def Faculty_Portal():
  mydb = mydbfunc()
  cursor = mydb.cursor(dictionary=True)
  if "user_type" not in session:
    return redirect("/")
  # doesn't allow access if not logged in as faculty
  if session["user_type"] != "Faculty":
    return redirect("/")

  session['years'] = [2023, 2024]
  session['semesters'] = [1, 2, 3]
  session['student_portal_error'] = ''
  if 'current_year' not in session:
    session['current_year'] = 2023
  if 'current_semester' not in session:
    session['current_semester'] = 3
  session['semester_names'] = ['blank', 'spring', 'summer', 'fall'] # 'blank' becaues there is no 0 semester

  cursor.execute("SELECT * FROM current_sections WHERE professor_uid = %s and semester = %s and year = %s ORDER BY day, timeslot", (session["uid"], session["current_semester"], session["current_year"]))
  prof_classes = cursor.fetchall()
  
  # Allow users to pick the semester they want to see there schedule for
  if request.method == 'POST':
    if 'semester' in request.form:
      session['current_semester'] = int(request.form['semester'])
      session['current_year'] = int(request.form['year'])
      print("")
      return redirect(url_for("Faculty_Portal"))

    # TODO: get all classes from database for that semester/year
    # session['schedule'] = []
    # cursor.execute('SELECT * FROM current_sections JOIN classes ON classes.cid = current_sections.cid JOIN users ON current_sections.professor_uid = users.uid WHERE users.uid = %s AND current_sections.year = %s AND current_sections.semester = %s',
    #                 (session['uid'], str(session['current_year']), str(session['current_semester'])))
    # classes_taking = cursor.fetchall()
    # for i in [1, 2, 3]:
    #   partial = []
    #   for j in ['M', 'T', 'W', 'R', 'F']:
    #     for k in classes_taking:
    #       if int(k['timeslot']) == i and k['day'] == j:
    #         partial.append([k['class_title'], k['section_id']])
    #     else:
    #       partial.append(['free period', 'none'])
    #   session['schedule'].append(partial)
  
  return render_template('Faculty_Portal.html', prof_classes = prof_classes, semesters = ["", "Spring", "Summer", "Fall"])


########################################################################################################################################
  #GET STATS PAGE
    #displays stats for GS to query
########################################################################################################################################
@app.route("/Get_Stats", methods = ["GET", "POST"])
def get_stats():
  # SEMESTER, YEAR, DEGREE
  mydb = mydbfunc()
  cursor = mydb.cursor(dictionary=True)

  if "user_type" not in session:
    return redirect("/")
  elif session["user_type"] not in ["GS", "Admin"]:
    return redirect("/")

  semester = "%"
  year = "%"
  degree = "%"

  cursor.execute("SELECT * FROM applications WHERE semester LIKE %s and year LIKE %s and degree LIKE %s", (semester, year, degree))
  apps = cursor.fetchall()

  valid_years = []
  valid_semesters = ["Spring", "Fall"]
  for app in apps:
    if app["year"] not in valid_years:
      valid_years.append(app["year"])

  total_apps = len(apps)
  total_rejected = 0
  total_accepted = 0

  admittedList = ["acceptdeposit", "student"]

  for app in apps:
    if app["status"] == "denied":
      total_rejected += 1
    elif app["status"] in admittedList:
      total_accepted += 1

  average_GPA_admit = 0
  average_GPA_reject = 0
  GPAs_admit = 0
  GPAs_reject = 0

  for app in apps:
    cursor.execute("SELECT * FROM degrees WHERE uid = %s", (app["uid"],))
    degs = cursor.fetchall()
    for deg in degs:
      if app["status"] == "denied":
        average_GPA_reject += deg["gpa"]
        GPAs_reject += 1
      elif app["status"] in admittedList:
        average_GPA_admit += deg["gpa"]
        GPAs_admit += 1

  if GPAs_admit + GPAs_reject != 0:
    average_GPA_all = (average_GPA_admit + average_GPA_reject)/(GPAs_admit + GPAs_reject)
  else:
    average_GPA_all = 0
  if GPAs_admit != 0:
    average_GPA_admit = average_GPA_admit/GPAs_admit
  if GPAs_reject != 0:
    average_GPA_reject = average_GPA_reject/GPAs_reject

  average_total_accept = 0
  average_verbal_accept = 0
  average_quant_accept = 0
  average_score_accept = 0
  average_TOEFL_accept = 0
  average_total_reject = 0
  average_verbal_reject = 0
  average_quant_reject = 0
  average_score_reject = 0
  average_TOEFL_reject = 0

  total_GRE_accept = 0
  total_toefl_accept = 0
  total_score_accept = 0
  total_GRE_reject = 0
  total_toefl_reject = 0
  total_score_reject = 0

  for app in apps:
    cursor.execute("SELECT * FROM gres WHERE uid = %s", (app["uid"], ))
    gre = cursor.fetchall()
    if len(gre) != 0:
      gre = gre[0]
      if "total" in gre:
        if app["status"] == "denied":
          average_total_reject += gre['total']
          average_quant_reject += gre['quant']
          average_verbal_reject += gre['verbal']
          total_GRE_reject += 1
        elif app["status"] in admittedList:
          average_total_accept += gre['total']
          average_quant_accept += gre['quant']
          average_verbal_accept += gre['verbal']
          total_GRE_accept += 1
      if "toefl" in gre:
        if app["status"] == "denied":
          average_TOEFL_reject += gre["toefl"]
          total_toefl_reject += 1
        elif app["status"] in admittedList:
          average_TOEFL_accept += gre["toefl"]
          total_toefl_accept += 1
      if "score" in gre:
        if app["status"] == "denied":
          average_score_reject += gre["score"]
          total_score_reject += 1
        elif app["status"] in admittedList:
          average_score_accept += gre["score"]
          total_score_accept += 1

  if total_GRE_accept != 0:
    average_total_accept = average_total_accept/total_GRE_accept
    average_verbal_accept = average_verbal_accept/total_GRE_accept
    average_quant_accept = average_quant_accept/total_GRE_accept
  if total_score_accept != 0:
    average_score_accept = average_score_accept/total_score_accept
  if total_toefl_accept != 0:
    average_TOEFL_accept = average_TOEFL_accept/total_toefl_accept
  if total_GRE_reject != 0:
    average_total_reject = average_total_reject/total_GRE_reject
    average_verbal_reject = average_verbal_reject/total_GRE_reject
    average_quant_reject = average_quant_reject/total_GRE_reject
  if total_score_reject != 0:
    average_score_reject = average_score_reject/total_score_reject
  if average_TOEFL_reject != 0:
    average_TOEFL_reject = average_TOEFL_reject/total_toefl_reject

  # total_GRE_accept = 0
  # total_toefl_accept = 0
  # total_score_accept = 0
  # total_GRE_reject = 0
  # total_toefl_reject = 0
  # total_score_reject = 0

  if request.method == "POST":
    print("post!")
    year = request.form["year"]
    sem = request.form["semester"]
    degree = request.form["degree"]
    
    cursor.execute("SELECT * FROM applications WHERE semester LIKE %s and year LIKE %s and degree LIKE %s", (semester, year, degree))
    apps = cursor.fetchall()

    total_apps = len(apps)
    total_rejected = 0
    total_accepted = 0

    admittedList = ["admitted", "admitaid", "acceptdeposit"]

    for app in apps:
      if app["status"] == "denied":
        total_rejected += 1
      elif app["status"] in admittedList:
        total_accepted += 1

    average_GPA_admit = 0
    average_GPA_reject = 0
    GPAs_admit = 0
    GPAs_reject = 0

    for app in apps:
      cursor.execute("SELECT * FROM degrees WHERE uid = %s", (app["uid"],))
      degs = cursor.fetchall()
      for deg in degs:
        if app["status"] == "denied":
          average_GPA_reject += deg["gpa"]
          GPAs_reject += 1
        elif app["status"] in admittedList:
          average_GPA_admit += deg["gpa"]
          GPAs_admit += 1

    if GPAs_admit + GPAs_reject != 0:
      average_GPA_all = (average_GPA_admit + average_GPA_reject)/(GPAs_admit + GPAs_reject)
    else:
      average_GPA_all = 0
    if GPAs_admit != 0:
      average_GPA_admit = average_GPA_admit/GPAs_admit
    if GPAs_reject != 0:
      average_GPA_reject = average_GPA_reject/GPAs_reject

    average_total_accept = 0
    average_verbal_accept = 0
    average_quant_accept = 0
    average_score_accept = 0
    average_TOEFL_accept = 0
    average_total_reject = 0
    average_verbal_reject = 0
    average_quant_reject = 0
    average_score_reject = 0
    average_TOEFL_reject = 0

    total_GRE_accept = 0
    total_toefl_accept = 0
    total_score_accept = 0
    total_GRE_reject = 0
    total_toefl_reject = 0
    total_score_reject = 0

    for app in apps:
      cursor.execute("SELECT * FROM gres WHERE uid = %s", (app["uid"], ))
      gre = cursor.fetchall()
      if len(gre) != 0:
        gre = gre[0]
        if "total" in gre:
          if app["status"] == "denied":
            average_total_reject += gre['total']
            average_quant_reject += gre['quant']
            average_verbal_reject += gre['verbal']
            total_GRE_reject += 1
          elif app["status"] in admittedList:
            average_total_accept += gre['total']
            average_quant_accept += gre['quant']
            average_verbal_accept += gre['verbal']
            total_GRE_accept += 1
        if "toefl" in gre:
          if app["status"] == "denied":
            average_TOEFL_reject += gre["toefl"]
            total_toefl_reject += 1
          elif app["status"] in admittedList:
            average_TOEFL_accept += gre["toefl"]
            total_toefl_accept += 1
        if "score" in gre:
          if app["status"] == "denied":
            average_score_reject += gre["score"]
            total_score_reject += 1
          elif app["status"] in admittedList:
            average_score_accept += gre["score"]
            total_score_accept += 1

    if total_GRE_accept != 0:
      average_total_accept = average_total_accept/total_GRE_accept
      average_verbal_accept = average_verbal_accept/total_GRE_accept
      average_quant_accept = average_quant_accept/total_GRE_accept
    if total_score_accept != 0:
      average_score_accept = average_score_accept/total_score_accept
    if total_toefl_accept != 0:
      average_TOEFL_accept = average_TOEFL_accept/total_toefl_accept
    if total_GRE_reject != 0:
      average_total_reject = average_total_reject/total_GRE_reject
      average_verbal_reject = average_verbal_reject/total_GRE_reject
      average_quant_reject = average_quant_reject/total_GRE_reject
    if total_score_reject != 0:
      average_score_reject = average_score_reject/total_score_reject
    if average_TOEFL_reject != 0:
      average_TOEFL_reject = average_TOEFL_reject/total_toefl_reject

          
    return render_template("stats.html", total_apps = total_apps, total_rejected = total_rejected, total_accepted = total_accepted, average_GPA_admit = average_GPA_admit, average_GPA_all = average_GPA_all, average_GPA_reject = average_GPA_reject, current_year = year, current_sem = sem, current_deg = degree,
      total_GRE_accept = total_GRE_accept, total_toefl_accept = total_toefl_accept, total_score_accept = total_score_accept, total_GRE_reject = total_GRE_reject, total_toefl_reject = total_toefl_reject, total_score_reject = total_score_reject,
      average_total_accept = average_total_accept, average_verbal_accept = average_verbal_accept, average_quant_accept = average_quant_accept, average_score_accept = average_score_accept, valid_semesters = valid_semesters, valid_years = valid_years,
      average_TOEFL_accept = average_TOEFL_accept, average_total_reject = average_total_reject, average_verbal_reject = average_verbal_reject, average_quant_reject = average_quant_reject, average_score_reject = average_score_reject, average_TOEFL_reject = average_TOEFL_reject)
  
        
  return render_template("stats.html", total_apps = total_apps, total_rejected = total_rejected, total_accepted = total_accepted, average_GPA_admit = average_GPA_admit, average_GPA_all = average_GPA_all, average_GPA_reject = average_GPA_reject, current_year = "%", current_sem = "%", current_deg = "%",
    total_GRE_accept = total_GRE_accept, total_toefl_accept = total_toefl_accept, total_score_accept = total_score_accept, total_GRE_reject = total_GRE_reject, total_toefl_reject = total_toefl_reject, total_score_reject = total_score_reject,
    average_total_accept = average_total_accept, average_verbal_accept = average_verbal_accept, average_quant_accept = average_quant_accept, average_score_accept = average_score_accept, valid_semesters = valid_semesters, valid_years = valid_years,
    average_TOEFL_accept = average_TOEFL_accept, average_total_reject = average_total_reject, average_verbal_reject = average_verbal_reject, average_quant_reject = average_quant_reject, average_score_reject = average_score_reject, average_TOEFL_reject = average_TOEFL_reject)
  

########################################################################################################################################
  #REGISTRAR FACULTY PORTAL PAGE (REGS)
    #edit course catalog and sections
########################################################################################################################################
@app.route("/Registrar_Portal", methods = ["GET", "POST"])
def Registrar_Portal():
  if "user_type" not in session:
    return redirect("/")
  elif session["user_type"] != "Registrar":
    return redirect("/")

  return render_template("Registrar_Portal.html")

################################################################
  #CHECKS IF USER HAS PRIVILEGES TO VIEW TRANSCRIPT PAGE
  #TODO: add registrar
################################################################
def transcript_visible(student_ID):
  #ALWAYS: grad sec, sysadmin
  #SOMETIMES: faculty (if advisor of student), student and alumni (if uid matches)
  #NEVER: registrar, applicant  
  mydb = mydbfunc()
  cursor = mydb.cursor(dictionary=True)

  if "user_type" not in session:
    return False
    #FALSE

  if session["user_type"] == "Admin" or session["user_type"] == "GS" or session["user_type"] == "Registrar":
    return True

  if session["user_type"] == "Student":
    print(student_ID)
    print(session["uid"])
    if int(student_ID) != int(session["uid"]):
      print("studentid no match")
      return False
    else:
      return True
  
  if session["user_type"] == "Alumni":
    if int(student_ID) != int(session["uid"]):
      return False
    else:
      return True
  
  if session["user_type"] == "Applicant":
    return False

  if session["user_type"] == "Faculty":

    cursor.execute("SELECT * FROM faculty WHERE uid = %s", (session["uid"],))
    fac_info = cursor.fetchone()
    if fac_info["is_CAC"] == "T":
      return True
    if fac_info["can_advise"] == "T":
      cursor.execute("SELECT * FROM students WHERE advisor_id = %s", (session["uid"],))
      advisees = cursor.fetchall()
      for advisee in advisees:
        print("advisee!")
        print(advisee["uid"])
        print(student_ID)
        if str(student_ID) == str(advisee["uid"]):
          print("advisee found!")
          return True
  
  
  return False
  

########################################################################################################################################
  #TRANSCRIPT PAGE (REGS and ARGS)
    #displays the transcript for a specific student (based on the student_ID which is part of the url)
  #TODO: (for REGS) maybe let GS and Sysadmin (and CAC?) edit grades here?
########################################################################################################################################
@app.route('/Transcript<student_ID>', methods = ['GET', 'POST'])
def Transcript(student_ID):
  mydb = mydbfunc()
  cursor = mydb.cursor(dictionary=True)
  if "user_type" not in session:
    return redirect("/")

  visible = transcript_visible(student_ID)

  if not visible:
    return redirect(url_for("login"))
    
  session['semester_names'] = ['blank', 'spring', 'summer', 'fall'] # 'blank' becaues there is no 0 semester

  cursor.execute('SELECT fname, minit, lname FROM users WHERE users.uid = %s', 
                (student_ID, ))
  session['student_name'] = cursor.fetchone()
  print(session['student_name'])
  
  session['classes_taken'] = []
  cursor.execute('SELECT * FROM student_classes JOIN classes ON classes.cid = student_classes.cid JOIN current_sections ON student_classes.section_id = current_sections.section_id JOIN users ON users.uid = current_sections.professor_uid WHERE student_classes.student_uid = %s',
                (student_ID, ))
  session['classes_taken'] = cursor.fetchall()

  cursor.execute('SELECT grade FROM student_classes JOIN classes ON classes.cid = student_classes.cid JOIN current_sections ON student_classes.section_id = current_sections.section_id JOIN users ON users.uid = current_sections.professor_uid WHERE student_classes.student_uid = %s',
                (student_ID, ))
  grades = cursor.fetchall()
  grades = [list(dct.values())[0] for dct in grades]
  possible_grades = ['IP', 'F', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A']

  # Calculate GPA
  session['GPA'] = (sum(possible_grades.index(i) for i in grades)+5)/(len(grades)+1)

  return render_template('Transcript.html', student_ID = student_ID)


def class_page_visible(class_ID):
  #ALWAYS: grad sec, sysadmin, registrar
  #SOMETIMES: faculty (if they are teaching that class), students & alumni (if they are in that section)
  #NEVER: applicant
  mydb = mydbfunc()
  cursor = mydb.cursor(dictionary=True)

  if "user_type" not in session:
    return False
  
  if session["user_type"] == "GS" or session["user_type"] == "Admin" or session["user_type"] == "Registrar":
    return True
  
  if session["user_type"] == "Applicant":
    return False
  
  if session["user_type"] == "Student" or session["user_type"] == "Alumni":
    cursor.execute("SELECT * FROM student_classes WHERE section_id = %s", (class_ID,))
    students = cursor.fetchall()
    for student in students:
      if str(student["student_uid"]) == str(session["uid"]):
        return True 
    return False
  
  if session["user_type"] == "Faculty":
    cursor.execute("SELECT * FROM current_sections WHERE section_id = %s", (class_ID,))
    professor = cursor.fetchone()
    if str(professor["professor_uid"]) == str(session["uid"]):
      return True
    return False

  return False


########################################################################################################################################
  #CLASS PAGE PAGE (REGS)
    #displays the students and class info for a specific class
    #this is where faculty (and GS and Sysadmin) can change students grades
########################################################################################################################################
@app.route('/Class_Page<class_ID>', methods = ['GET', 'POST'])
def Class_Page(class_ID):
  # class_ID is a section id
  mydb = mydbfunc()
  cursor = mydb.cursor(dictionary=True)
  if "user_type" not in session:
    return redirect("/")
  print("refresh class page")
  visible = class_page_visible(class_ID)
  if not visible:
    return redirect(url_for("login"))
  
  session['different_periods'] = ['3-5:30pm', '4-6:30pm', '6-8:30pm']
  session['different_periods_2'] = ['blank', '3-5:30pm', '4-6:30pm', '6-8:30pm']
  session['semester_names'] = ['blank', 'spring', 'summer', 'fall']
  
  cursor.execute("SELECT * FROM current_sections JOIN classes ON current_sections.cid = classes.cid LEFT JOIN student_classes ON student_classes.section_id = current_sections.section_id LEFT JOIN users ON users.uid = current_sections.professor_uid WHERE current_sections.section_id = %s", (class_ID, ))
  course = cursor.fetchone()
  session['course'] = course
  try:
    cursor.fetchall() # so cursor doesn't have a fit when I try to use it again
  except:
    pass
  # cursor.execute("SELECT * FROM student_classes WHERE section_id = %s", (class_ID,))
  # class1 = cursor.fetchall()
  # print(class1)
  cursor.execute('SELECT * FROM student_classes JOIN users ON users.uid = student_classes.student_uid WHERE student_classes.section_id = (%s)',
                 (class_ID, ))
  students = cursor.fetchall()
  session['students'] = students
  print(students)
  print(session['students'])

  session['possible_grades'] = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'F', 'IP']

  if request.method == 'POST':
    student_uid = list(request.form.keys())[0]
    new_grade = request.form[student_uid]
    if new_grade == 'IP':
      cursor.execute('UPDATE student_classes SET grade = %s WHERE student_uid = %s AND section_id = %s',
                   (new_grade, student_uid, class_ID))
      mydb.commit()
    else:
      cursor.execute('UPDATE student_classes SET grade = %s WHERE student_uid = %s AND section_id = %s',
                   (new_grade, student_uid, class_ID))
      mydb.commit()

    cursor.execute('SELECT * FROM student_classes JOIN users ON users.uid = student_classes.student_uid WHERE student_classes.section_id = %s',
                 (class_ID, ))
    session['students'] = cursor.fetchall()
  
  return render_template('Class_Page.html', class_ID = class_ID)

########################################################################################################################################
  #EDIT PERSONAL INFO
    #allows users to edit their personal info (name, adress)
########################################################################################################################################
@app.route("/Edit_Info", methods = ["GET", "POST"])
def Edit_Info():
  mydb = mydbfunc()
  cursor = mydb.cursor(dictionary=True)
  if "user_type" not in session:
    return redirect("/")
  if session['user_type'] == 'Recommender':
    return redirect("/")

  session['EditInfoError'] = ""

  if request.method == 'POST':
    fname = request.form["fname"]
    minit = request.form["minit"]
    lname = request.form["lname"]
    address = request.form["address"]
    email = request.form["email"]

    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    dbemail = cursor.fetchall()
    dbemail = dbemail[0]

    if len(dbemail) != 0 and dbemail["uid"] != session["uid"]:
      session["EditInfoError"] = "Sorry, that email is already in use"
    else:
      cursor.execute("UPDATE users SET fname = %s, minit = %s, lname = %s, address = %s, email = %s WHERE uid = %s", (fname, minit, lname, address, email, session["uid"]))
      mydb.commit()

      session["first_name"] = fname
      session["middle_initial"] = minit
      session["last_name"] = lname
      session["address"] = address
      session["email"] = email

  return render_template("Edit_Info.html")

########################################################################################################################################
  #CHANGE PASSWORD
    #allows users to edit their personal info (name, adress)
########################################################################################################################################
@app.route("/Change_Password", methods = ["GET", "POST"])
def Change_Pass():
  if "user_type" not in session:
    return redirect("/")
  if session['user_type'] == 'Recommender':
    return redirect("/")
  
  session["passError"] = ""
  session["passSuccess"] = ""
  if request.method == "POST":
    pass1 = request.form["pass1"]
    pass2 = request.form["pass2"]
    mydb = mydbfunc()
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE uid = %s", (session["uid"],))
    realpass = cursor.fetchone()

    if pass1 != pass2:
      session["passError"] = "passwords dont match"
      return render_template("Change_Password.html")
    elif realpass["password"] == pass1:
      session["passError"] = "your new password can not be your old password"
      return render_template("Change_Password.html")
    else:
      cursor.execute("UPDATE users SET password = %s WHERE uid = %s", (pass1, session["uid"]))
      mydb.commit()
      session["passSuccess"] = "Yay! You updated your password"
    
  return render_template("Change_Password.html")


########################################################################################################################################
  #GET GRAD YEAR AND SEM FUNCTION
    # gets grad year and sem as most recent semester a student took classes
########################################################################################################################################
def get_grad_year_sem(uid):
  mydb = mydbfunc()
  cursor = mydb.cursor(dictionary=True)

  cursor.execute("SELECT * FROM student_classes LEFT JOIN current_sections ON student_classes.section_id = current_sections.section_id WHERE student_uid = %s", (uid,))
  classes = cursor.fetchall()

  recent_year = 0
  recent_sem = 0
  for class1 in classes:
    if class1["year"] > recent_year:
      recent_year = class1["year"]
      recent_sem = int(class1["semester"])
    if class1["year"] == recent_year and int(class1["semester"]) > recent_sem:
      recent_sem = int(class1["semester"])

  gradYearSem = [recent_year, recent_sem]
  return gradYearSem


########################################################################################################################################
  #VIEW ADMITTED STUDENTS PAGE
    # allows GS to view all admitted students
########################################################################################################################################
@app.route("/admittedstudents", methods = ["GET", "POST"])
def admittedstudents():
  mydb = mydbfunc()
  cursor = mydb.cursor(dictionary=True)
  if "user_type" not in session:
    return redirect("/")
  if session["user_type"] not in ["GS", "Admin"]:
    return redirect("/")
  
  cursor.execute("SELECT * FROM applications LEFT JOIN users ON applications.uid = users.uid WHERE applications.status = %s or applications.status = %s  or applications.status = %s", ("admitted", "admitaid", "acceptdeposit"))
  applicants = cursor.fetchall()


  valid_years = [2020, 2021, 2022, 2023, 2024]
  valid_sems = ["Spring", "Summer", "Fall"]

  if request.method == "POST":
    if "degree" in request.form:
      lname = "%" + request.form["lname"] + "%"
      id = request.form["uid"] + "%"
      admityear = request.form["year"]
      admitsem = request.form["sem"]
      degree = request.form["degree"]
      aid1 = "admitaid"
      aid2 = "admitted"
      aid3 = "acceptdeposit"
    

      cursor.execute("SELECT * FROM applications LEFT JOIN users ON applications.uid = users.uid WHERE (applications.status = %s or applications.status = %s or applications.status = %s) and users.uid LIKE %s and users.lname LIKE %s and applications.year LIKE %s and applications.semester LIKE %s and applications.degree LIKE %s", (aid1, aid2, aid3, id, lname, admityear, admitsem, degree))
      applicants = cursor.fetchall()
      return render_template("admittedstudents.html", applicants = applicants, current_year = admityear, current_sem = admitsem, current_deg = degree, valid_years = valid_years, valid_sems = valid_sems)


  return render_template("admittedstudents.html", applicants = applicants, current_year = "%", current_sem = "%", current_deg = "%", valid_years = valid_years, valid_sems = valid_sems)

@app.route("/gradcleared", methods = ["GET", "POST"])
def gradclearedstudents():
  mydb = mydbfunc()
  cursor = mydb.cursor(dictionary=True)
  if "user_type" not in session:
    return redirect("/")
  if session["user_type"] not in ["GS", "Admin"]:
    return redirect("/")

  semesters = ["", "Spring", "Summer", "Fall"]

  cursor.execute("SELECT * FROM current_sections")
  classes = cursor.fetchall()

  valid_years = []
  for class1 in classes:
    if class1["year"] not in valid_years:
      valid_years.append(class1["year"])
  
  cursor.execute("SELECT applications.degree, s.*, a.uid AS aduid, grad_requests.* FROM grad_requests LEFT JOIN users AS s ON grad_requests.student_id = s.uid LEFT JOIN users AS a ON grad_requests.advisor_id = a.uid LEFT JOIN applications ON applications.uid = s.uid WHERE grad_requests.approved = 'T'")
  requests = cursor.fetchall()

  for req in requests:
    gradyear = get_grad_year_sem(req["uid"])
    req["semester"] = gradyear[1]
    req["year"] = gradyear[0]

  if request.method == "POST":
    if "year" in request.form:
      lname = "%" + request.form["lname"] + "%"
      id = request.form["uid"] + "%"
      gradyear = request.form["year"]
      gradsem = request.form["sem"]
      degree = request.form["degree"]
      aduid = request.form["aduid"]  + "%"

      cursor.execute("SELECT applications.degree, s.*, a.uid AS aduid, grad_requests.* FROM grad_requests LEFT JOIN users AS s ON grad_requests.student_id = s.uid LEFT JOIN users AS a ON grad_requests.advisor_id = a.uid LEFT JOIN applications ON applications.uid = s.uid HAVING grad_requests.approved = 'T' AND s.uid LIKE %s AND s.lname LIKE %s AND applications.degree LIKE %s AND a.uid LIKE %s", (id, lname, degree, aduid))
      requests = cursor.fetchall()
      
      print(requests)

      for req in requests:
        gradinfo = get_grad_year_sem(req["uid"])
        if gradyear != "%":
          if int(gradinfo[0]) != int(gradyear):
            requests.remove(req)
            print("year dont match")
            pass
        if gradsem != "%":
          if semesters[gradinfo[1]] != gradsem:
            print(gradinfo[1])
            print(gradsem)
            requests.remove(req)
            print("sem dont match")
            pass
        req["year"] = gradinfo[0]
        req["semester"] = gradinfo[1]

      return render_template("gradcleared.html", requests = requests, semesters = semesters, valid_years = valid_years, valid_sems = ["Spring", "Summer", "Fall"], current_year = gradyear, current_sem = gradsem, current_degree = degree)

  
  return render_template("gradcleared.html", requests = requests, semesters = semesters, valid_years = valid_years, valid_sems = ["Spring", "Summer", "Fall"], current_year = "%", current_sem = "%", current_degree = "%")


@app.errorhandler(Exception)
def all_exception_handler(error):
    print(error)
    return render_template("error.html", err_message = error)


#########################################################################################################################################
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
#########################################################################################################################################








################################################  ADMIN HOME ROUTE  ################################################
#This Route contains all the information, basically the admin pass homepage
##############################################################################################################
@app.route('/home')
def home():
    if "user_type" not in session:
      return redirect("/")
    email = session.get('email')
    password = session.get('password')
    user_type = session.get('user_type')
    mydb = mydbfunc()
    cur = mydb.cursor(dictionary = True)

    return render_template("home.html", user_type = user_type)



################################################  COURSE CATALOG DONE ################################################
#Show the entire course catalog (Courses available etc)
##################################################################################################################
@app.route('/coursecatalog')
def coursecatalog():
    mydb = mydbfunc()
    cur = mydb.cursor(dictionary=True)
    if "user_type" not in session:
      return redirect("/")
    # Retrieve all data from the "classes" table
    cur.execute("""
        SELECT *
        FROM classes
        ORDER BY cid;
    """)
    data = cur.fetchall()

    # Retrieve all prerequisites for each class
    for i in range(len(data)):
        # Retrieve the prerequisites for this class
        cur.execute("""
            SELECT c.department, c.class_num
            FROM classes c
            INNER JOIN prerequisites p ON c.cid = p.prereq_cid
            WHERE p.class_cid = %s;
        """, (data[i]['cid'],))
        prerequisites = cur.fetchall()
        # Add the prerequisites to the class's dictionary
        if len(prerequisites) > 0:
            data[i]['prerequisite_1'] = prerequisites[0]['department'] + " " + str(prerequisites[0]['class_num'])
            if len(prerequisites) > 1:
                data[i]['prerequisite_2'] = prerequisites[1]['department'] + " " + str(prerequisites[1]['class_num'])
            else:
                data[i]['prerequisite_2'] = "None"
        else:
            data[i]['prerequisite_1'] = "None"
            data[i]['prerequisite_2'] = "None"

    user_type = session['user_type']
    return render_template("coursecatalog.html", data=data, user_type=user_type, id=session['uid'])



################################################  FULL STUDENT PAGE DONE ################################################
#Show an entire list of all the students, their info, and a link to their directory (Admin View, Grad Secretary View)
#####################################################################################################################
@app.route('/students', methods=['GET'])
def students():
    mydb = mydbfunc()
    cur = mydb.cursor(dictionary=True)
    if "user_type" not in session:
      return redirect("/")
    if session['user_type'] not in ['GS', 'Admin', 'Registrar']:
      return redirect("/")
    

    cur.execute("SELECT students.uid, fname, minit, lname, email FROM students JOIN users ON students.uid = users.uid")
    students = cur.fetchall()

    user_type = session['user_type']
    return render_template("students.html", students=students, user_type=user_type)

################################################  FULL STUDENT PAGE DONE ################################################
#Show an entire list of all the students, their info, and a link to their directory (Admin View, Grad Secretary View)
#####################################################################################################################
@app.route('/viewalltranscripts', methods=['GET'])
def viewalltranscripts():
    mydb = mydbfunc()
    cur = mydb.cursor(dictionary=True)
    if "user_type" not in session:
      return redirect("/")
    if session['user_type'] not in ['GS', 'Admin', 'Registrar']:
      return redirect("/")

    cur.execute("SELECT students.uid, fname, minit, lname, email FROM students JOIN users ON students.uid = users.uid")
    students = cur.fetchall()

    user_type = session['user_type']
    return render_template("all_transcripts.html", students=students, user_type=user_type)


################################################  FACULTY ADVISOR STUDENT PAGE  ################################################
#Show an  list of all the advisors' students, their info, and a link to their directory (Admin View, Grad Secretary View)
################################################################################################################################
@app.route('/facultyviewstudents', methods = ["GET", "POST"])
def facultyviewstudents():
    mydb = mydbfunc()
    cur = mydb.cursor(dictionary=True)
    if "user_type" not in session:
      return redirect("/")
    if session['user_type'] not in ['GS', 'Admin', 'Faculty', 'Registrar']:
      return redirect("/")

    valid_years = [2020, 2021, 2022, 2023, 2024]
    valid_sems = ["Spring", "Summer", "Fall"]

    id = session['uid']
    print(id)
    user_type = session['user_type']
    cur.execute("SELECT * FROM users WHERE uid = (%s)", (id,))
    facultyinfo = cur.fetchone()
    print(facultyinfo)
    if user_type == 'Faculty':
        print("isfaculty")
        # cur.execute("SELECT students.*, users.* FROM students JOIN users ON students.uid = users.uid WHERE students.advisor_id = (%s)", (id,))
        cur.execute("SELECT students.*, users.*, phd_thesis.approved, applications.* FROM students JOIN users ON students.uid = users.uid LEFT JOIN applications ON users.uid = applications.uid LEFT JOIN phd_thesis ON students.uid = phd_thesis.user_id WHERE students.advisor_id = (%s)", (id,))
        studentinfo = cur.fetchall()
        print("fac")
        print(studentinfo)
    else:
        print("isnotfaculty")
        cur.execute("SELECT * FROM students JOIN users on students.uid = users.uid LEFT JOIN applications on users.uid = applications.uid")
        studentinfo = cur.fetchall()

    cur.execute("SELECT * FROM phd_thesis")
    studentthesis = cur.fetchall()

    if request.method == "POST":
      if "sem" in request.form:
        lname = "%" + request.form["lname"] + "%"
        id = request.form["uid"] + "%"
        admityear = request.form["year"]
        admitsem = request.form["sem"]
        degree = request.form["degree"]
        if user_type == 'Faculty':
          print("isfaculty")
          # cur.execute("SELECT students.*, users.* FROM students JOIN users ON students.uid = users.uid WHERE students.advisor_id = (%s)", (id,))
          cur.execute("SELECT students.*, users.*, phd_thesis.approved, applications.* FROM students JOIN users ON students.uid = users.uid LEFT JOIN applications ON users.uid = applications.uid LEFT JOIN phd_thesis ON students.uid = phd_thesis.user_id WHERE students.advisor_id LIKE (%s) and applications.year LIKE %s and applications.semester LIKE %s AND applications.degree LIKE %s AND users.uid LIKE %s AND users.lname LIKE %s", (id,admityear, admitsem, degree, id, lname))
          studentinfo = cur.fetchall()
          print("fac")
          print(studentinfo)
        else:
            print("isnotfaculty")
            cur.execute("SELECT * FROM students JOIN users on students.uid = users.uid LEFT JOIN applications on users.uid = applications.uid WHERE applications.year LIKE %s and applications.semester LIKE %s AND applications.degree LIKE %s AND users.uid LIKE %s AND users.lname LIKE %s", (admityear, admitsem, degree, id, lname))
            studentinfo = cur.fetchall()
            cur.execute("SELECT * FROM students JOIN users on students.uid = users.uid LEFT JOIN applications on users.uid = applications.uid")
            test = cur.fetchall()
            print(test)
            for stuff in test:
              print(stuff["year"])
        
        # print(admityear)
        # print(admitsem)
        # print(degree)
        # print(lname)
        # print(id)
        return render_template("facultystudentview.html", studentinfo=studentinfo, user_type=user_type, studentthesis=studentthesis, facultyinfo=facultyinfo, valid_sems = valid_sems, valid_years = valid_years, current_sem = admitsem, current_year = admityear, current_deg = degree)


    return render_template("facultystudentview.html", studentinfo=studentinfo, user_type=user_type, studentthesis=studentthesis, facultyinfo=facultyinfo, valid_sems = valid_sems, valid_years = valid_years, current_sem = "%", current_year = "%", current_deg = "%")

################################################  STUDENT DIRECTORY  ################################################
#Show all the info of said student
#####################################################################################################################
@app.route('/studentdirectory/<id>', methods=['GET', 'POST'])
def studentdirectory(id):
    mydb = mydbfunc()
    cur = mydb.cursor(dictionary=True)
    if "user_type" not in session:
      return redirect("/")

    if request.method == 'POST':
        # Handle form submission for updating student info
        cur.execute("UPDATE users SET fname=%s, minit=%s, lname=%s, email=%s, address=%s, password=%s WHERE uid=%s", (
            request.form['fname'],
            request.form['minit'],
            request.form['lname'],
            request.form['email'],
            request.form['address'],
            request.form['password'],
            # id
        ))
        mydb.commit()

        flash('Student information updated successfully.')
        return redirect(url_for('studentdirectory', id=id))

    # Fetch student information with user_id=id
    cur.execute("SELECT * FROM students JOIN users ON students.uid = users.uid WHERE students.uid = (%s)", (id,))
    student_info = cur.fetchone()

    if student_info is not None:
        cur.execute("SELECT fname, lname FROM users WHERE uid = (%s)", (student_info['advisor_id'],))
        advisor_info = cur.fetchone()
    else:
        advisor_info = None
    
    cur.execute("SELECT * FROM form1 WHERE user_id = (%s) LIMIT 1", (id,))
    form1_info = cur.fetchone()
    has_requested_grad = False
    print (has_requested_grad)
    print (form1_info)
    if not form1_info:
        # If id not found, return an error message
        has_form1=False
    else:
        has_form1=True
    
    # Check if there is a grad_request for the student
    if has_form1 == True:
       
      cur.execute("SELECT * FROM grad_requests WHERE student_id = (%s)", (id,))
      grad_request_info = cur.fetchone()
      if not grad_request_info:
        has_requested_grad = False
      else:
        has_requested_grad = True
    

    return render_template("studentdirectory.html", 
                            x=student_info, 
                            adname=advisor_info,
                            has_form1 = has_form1,
                            has_requested_grad = has_requested_grad,
                            user_type=session['user_type'])


################################################  FORM 1 PAGE DONE ##############################################################
#This is where form1 is filled in for the student
#############################################################################################################################
@app.route('/form1/<id>', methods = ['GET'])
def form1(id):
    if "user_type" not in session:
      return redirect("/")
    if session['user_type'] != 'Student':
      return redirect('/')
    if int(session['uid']) != int(id):
      return redirect('/')
    user_type = session.get('user_type')
    mydb = mydbfunc()
    cur = mydb.cursor(dictionary = True)
    

    #clear form1 for all its ids
    cur.execute("DELETE FROM form1 WHERE user_id = %s", (id,))
    mydb.commit()

    print("successfully cleared")
    
    cur.execute("SELECT * FROM student_classes WHERE student_uid = (%s) LIMIT 1", (id,))
    transcript = cur.fetchone()

    if not transcript:
        # If id not found, return an error message
        err_message = "No transcript so Form 1 cannot be submitted talk to your advisor to address this issue"
        return render_template("error.html", err_message = err_message)
    print("student has transcript")
    cur.execute("SELECT * FROM students JOIN users ON students.uid = users.uid WHERE students.uid = (%s)", (id,))
    x = cur.fetchone()


    cur.execute("""
        SELECT cid, department, class_num
        FROM classes
        ORDER BY department, class_num ASC;
    """)
    course = cur.fetchall()

    return render_template("form1.html",x = x, course=course, id=id, user_type = user_type)

################################################  FORM 1 SUBMISSION DONE ##############################################################
#This is where form1 is submitted and added to database
###################################################################################################################################
@app.route('/submitForm1/<id>', methods=['GET', 'POST'])
def submit_form1(id):
    if "user_type" not in session:
      return redirect("/")
    if session['user_type'] != 'Student':
      return redirect('/')
    if int(session['uid']) != int(id):
      return redirect('/')
    # Get the user_id value from the form
    mydb = mydbfunc()
    cur = mydb.cursor(buffered=True)
    print("submission in progress")
    # user_id = request.form['user_id']
    print(id)
    courses = [request.form.get('course_{}'.format(i)) for i in range(0, 13) if request.form.get('course_{}'.format(i))]
    if courses:
     cur.executemany("INSERT INTO form1 (user_id, cid) VALUES (%s, %s)", [(id, course) for course in courses])
     print("added:", ", ".join(courses))
    
    mydb.commit()
    print("committed")
  
    #Check Form1 true:
    #1: Check if advisor is assigned to student: if not then delete the form and show error message
    cur.execute("select advisor_id from students where uid = (%s)", (id,))
    advisor = cur.fetchone()
    print(advisor)
    if(advisor == None):
        cur.execute("DELETE FROM form1 WHERE user_id =(%s)", (id,))
        mydb.commit()
        err_message = "No advisor ID found"   
        return render_template("error.html", err_message = err_message) 
    
    #2:check if prereqs were taken, and compare form1 with transcript (courses taken)
    if ((prereqmatch(id) == False) or (comparef1andtranscript(id)==0)):
              print("FAIL")
              cur.execute("DELETE FROM form1 WHERE user_id = %s", (id,))
              mydb.commit()
              err_message = "Your Form1 Does NOT fufil the requirements please try again :)"
              return render_template("error.html", err_message = err_message)
    
    print("submission done")
    return redirect(url_for('All_Student_Portal', id=id))

################################################  FORM 1 VIEW DONE  ##############################################################
# View the form 1 of said student
#############################################################################################################################
@app.route("/viewform1/<id>", methods = ['GET'])
def view_form1(id):
    if "user_type" not in session:
      return redirect("/")
    if session['user_type'] not in ['Admin', 'GS', 'Faculty', 'Registrar']:
      if session['user_type'] == 'Student':
        if int(session['uid']) != int(id):
          return redirect('/')
      else:
        return redirect('/')
    
    mydb = mydbfunc()
    cur = mydb.cursor(dictionary = True)
    cur.execute("select * from users where uid =(%s)", (id,))
    student = cur.fetchone()

    cur.execute("""
                SELECT c.department, c.class_num, c.cid, c.class_title
                FROM form1 f
                INNER JOIN classes c ON f.cid = c.cid
                WHERE f.user_id = %s;
            """, (id,))
    x = cur.fetchall()
    print(x)
    user_type = session['user_type']

    return render_template("viewform1.html", x = x, student=student, id = id, user_type = user_type)


################################################  TRANSCRIPT PAGE DONE  ################################################
#Show the transcript of said student
###################################################################################################################

@app.route('/transcript_ads/<student_ID>', methods=['GET', 'POST'])
def transcript_ads(student_ID):
    mydb = mydbfunc()
    cursor = mydb.cursor(dictionary=True)

    # Doesn't allow access if not logged in
    if 'user_type' not in session:
        return redirect(url_for('/'))
    print(student_ID)
    visible = transcript_visible(student_ID)

    print(visible)
    if not visible:
      return redirect(url_for("login"))

    # TODO: Faculty can only see the grads of their students
    if session['user_type'] == 'faculty':
        cursor.execute('SELECT dept FROM faculty WHERE uid = %s', (session['uid'],))
        faculty_dept = cursor.fetchone()['dept']
        cursor.execute('''SELECT COUNT(*)
                          FROM students
                          JOIN users ON students.uid = users.uid
                          JOIN faculty ON students.advisor_id = faculty.uid
                          WHERE users.uid = %s AND faculty.dept = %s''', (student_ID, faculty_dept))
        if cursor.fetchone()['COUNT(*)'] == 0:
            return redirect(url_for('/'))

    if session['user_type'] == 'student_p' or session['user_type'] == 'student_m':
        if student_ID != session['uid']:
            return redirect(url_for('/'))

    session['semester_names'] = ['blank', 'spring', 'summer', 'fall']  # 'blank' because there is no 0 semester

    cursor.execute('SELECT fname, minit, lname FROM users WHERE users.uid = %s', (student_ID,))
    session['student_name'] = cursor.fetchone()

    session['classes_taken'] = []
    cursor.execute('SELECT * FROM student_classes JOIN classes ON classes.cid = student_classes.cid JOIN current_sections ON student_classes.section_id = current_sections.section_id JOIN users ON users.uid = current_sections.professor_uid WHERE student_classes.student_uid = %s ORDER BY classes.cid',
                (student_ID, ))
    session['classes_taken'] = cursor.fetchall()
    
    gpa=get_gpa(student_ID)
    total_credit_hours = get_total_credit_hours(student_ID)

    print ("Total GPA: ", gpa)
    print("Total Credit Hours: ", total_credit_hours)
    print(student_ID)

    # Render the transcript template with the GPA and total credit hours
    return render_template('transcript_ads.html', gpa=gpa, total_credit_hours=total_credit_hours, student_ID=student_ID)

################################################  PERSONAL INFO DONE   ##############################################################
# View the users personal info such as email, name, etc
###############################################################################################################################
@app.route('/personalinfo/<id>')
def personalinfo(id):
    if "user_type" not in session:
      return redirect("/")
    mydb = mydbfunc()
    cur = mydb.cursor(dictionary = True)
    #first get the student's name from the id 
    cur.execute("SELECT * FROM students JOIN users ON students.uid = users.uid WHERE students.uid = (%s)", (id,))
    x = cur.fetchone()

    return render_template("personalinfo.html", x = x)

################################################  APPLY FOR GRADUATION PENDING ##############################################################
# Student applies for graduation here
######################################################################################################################################
@app.route('/applyforGrad/<id>')
def applyforgrad(id):
    #do the auditing and then change button name to pending graduation approval
    mydb = mydbfunc()
    cur = mydb.cursor(dictionary = True)
    if "user_type" not in session:
      return redirect("/")
    if session['user_type'] != 'Student':
      return redirect("/")
    if int(session['uid']) != int(id):
      return redirect("/")

  #Graduation Checks

  #1: Check if they have advisor
    cur.execute("select advisor_id from students where uid = (%s)", (id,))
    advisor = cur.fetchone()
    advisorID= advisor['advisor_id']
    print("Advisors ID: ",advisorID)
    if(advisor == None):
        cur.execute("DELETE FROM form1 WHERE user_id =(%s)", (id,))
        mydb.commit()
        err_message = "No advisor ID found"
        return render_template("error.html", err_message = err_message)
  
  #2: Get their degree type
    cur.execute("select degree from students where uid = (%s)", (id,))
    degree = cur.fetchone()
    print("Degree: ", degree['degree'])

  #3: Get their total amount of credits
    credit_hours = get_total_credit_hours(id)
    print("Total Credits: ", credit_hours)

  #4: Get their GPA
    gpa = get_gpa(id)
    print("Total GPA: ", gpa  )

  #5: get the amount of B's
    total_b = get_grades_below_b(id)
    print("grades below B: ", total_b )

  #6: check if they have taken their core classes
    taken_core = get_core_courses(id)
    print("Has Taken Core Classes: ", id )

  #7: Get the total amount of cs credits taken
    total_cs_credit_hours = get_total_cs_credit_hours(id)

  #check if they have a grad request already
    cur.execute("select * from grad_requests where student_id = (%s)", (id,))
    has_request = cur.fetchone()
    print("Request Status: ", has_request)

    #2 Masters Degree Requirements to pass audit: 
        #1: at least a total of 30 credits DONE
        #2: GPA > 3.00 DONE
        #3: No more than 2 grades below B DONE
        #4: Core classes: CSCI 6212, CSCI 6221, and CSCI 6461 Done 
        #5: Get all cs courses and check if their total is 30 credits if not DONE
        #6: go through all other non cs courses and select the 2 with highest credit DONE
        # Catch if fails else is good:
    if (degree['degree'] == 'Masters'):
        print("checking for masters")
        if has_request:
             #IF THEY HAVE REQUEST
             print("Request: PRESENT")
             #FAIL
             if((credit_hours<30) or (gpa<=3.00) or (total_b > 2) or (taken_core == False) or (total_cs_credit_hours <30)): 
                print("Master Graduation Aplication FAIL")
                cur.execute("UPDATE grad_requests set approved = (%s) where student_id =(%s)", ("F",id))
                mydb.commit()
                return redirect(url_for('All_Student_Portal', id=id))
             #PASS
             print("Master Graduation Aplication PASS")
             cur.execute("UPDATE grad_requests set approved = (%s) where student_id =(%s)", ("T",id))
             mydb.commit()
             return redirect(url_for('All_Student_Portal', id=id))
        
        #IF THEY DONT HAVE REQUEST
        print("Request: NOT PRESENT")
        #FAIL
        if((credit_hours<30) or (gpa<3.00) or (total_b > 2) or (taken_core == False) or (total_cs_credit_hours <30)): 
                print("Master Graduation Aplication FAIL")
                cur.execute("INSERT INTO grad_requests (student_id, advisor_id, approved) VALUES ((%s), (%s), (%s))", (id, advisorID, "F",))
                mydb.commit()
                return redirect(url_for('All_Student_Portal', id=id))
        #PASS
        print("Master Graduation Aplication PASS")
        cur.execute("INSERT INTO grad_requests (student_id, advisor_id, approved) VALUES (%s, %s, %s)", (id, advisorID, "T"))
        mydb.commit()
        return redirect(url_for('All_Student_Portal', id=id))
    
     #If They are PHD students:    
        #1: at least a total of 36 credits
        #2: at least 30 credits are from CS
        #3: no more than one grade below a b
        #4: gpa >= 3.50
        #5: pass thesis

    if (degree['degree'] == 'PHD'):
      print("checking for PHD")
      cur.execute("select approved from phd_thesis where user_id = (%s)", (id,))
      thesis_info = cur.fetchone()
      if thesis_info is None:
        # If id not found, return an error message
        err_message = "No Thesis Done"
        return render_template("error.html", err_message = err_message)
          
      else:
        is_approved = thesis_info['approved']
        print("Thesis Approval State: ", is_approved)

      if has_request:  
        #IF THEY HAVE REQUEST
        #FAIL
        if((credit_hours<36) or (total_cs_credit_hours <30) or (total_b >1) or (gpa<3.50) or (is_approved == "F")):
            print("PHD Graduation Aplication FAIL")
            cur.execute("UPDATE gradrequests set approved = (%s) where advisee_id =(%s)", ("F",id))
            mydb.commit()
            return redirect(url_for('All_Student_Portal', id=id))
        #PASS
        print("PHD Graduation Aplication PASS")
        cur.execute("UPDATE gradrequests set approved = (%s) where advisee_id =(%s)", ('T',id))
        mydb.commit()
        return redirect(url_for('All_Student_Portal', id=id))
      #IF THEY DONT HAVE REQUEST
      #FAIL
      if((credit_hours<36) or (total_cs_credit_hours <30) or (total_b >1) or (gpa<3.50) or (is_approved == "F")):
              print("PHD Graduation Aplication FAIL")
              cur.execute("INSERT INTO grad_requests (student_id, advisor_id, approved) VALUES ((%s), (%s), (%s))", (id, advisorID, "F",))
              mydb.commit()
              return redirect(url_for('All_Student_Portal', id=id))
      #PASS
      print("PHD Graduation Aplication PASS")
      cur.execute("INSERT INTO grad_requests (student_id, advisor_id, approved) VALUES ((%s), (%s), (%s))", (id, advisorID, "T",))
      mydb.commit()
      return redirect(url_for('All_Student_Portal', id=id))
    
    print("nothing happened")
    return redirect(url_for('All_Student_Portal', id=id))

################################################  GPA FUNCTION  ##############################################################
# Calculate the total gpa of the student
##############################################################################################################################
def get_gpa(student_ID): 
    mydb = mydbfunc()
    cursor = mydb.cursor(dictionary=True)
 # Create a dictionary to map grades to grade points
    grade_points = {'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 'B-': 2.7,
                    'C+': 2.3, 'C': 2.0, 'F': 0.0, 'IP': None}

    # Initialize variables for GPA and total credit hours
    gpa = 0.0
    total_credit_hours = 0

    # Retrieve the student's classes from the database
    cursor.execute('''SELECT *
                    FROM student_classes
                    JOIN current_sections ON student_classes.section_id = current_sections.section_id
                    JOIN classes ON classes.cid = current_sections.cid
                    JOIN users ON users.uid = current_sections.professor_uid
                    WHERE student_classes.student_uid = %s''', (student_ID,))
    classes_taken = cursor.fetchall()

    # Iterate over each class taken
    for class_taken in classes_taken:
        # Check for IP grade and skip this class if found
        if class_taken['grade'] == 'IP':
            continue
        
        # Look up the grade point value for this grade
        grade_point = grade_points[class_taken['grade']]
        
        # Add the grade point value times the credit hours to the total
        gpa += grade_point * class_taken['credit_hours']
        total_credit_hours += class_taken['credit_hours']

    # Calculate the GPA by dividing the total grade points by the total credit hours
    if total_credit_hours == 0:
        gpa = 0.0
    else:
        gpa /= total_credit_hours

    # Round the GPA to two decimal places
    gpa = round(gpa, 2)
    print(gpa)
    return gpa

################################################  TOTAL CREDIT HOURS FUNCTION  ###############################################
# Calculate the total Credit hours
##############################################################################################################################
def get_total_credit_hours(student_ID): 
    mydb = mydbfunc()
    cursor = mydb.cursor(dictionary=True)
    
    total_credit_hours = 0

    # Retrieve the student's classes from the database
    cursor.execute('''SELECT *
                    FROM student_classes
                    JOIN current_sections ON student_classes.section_id = current_sections.section_id
                    JOIN classes ON classes.cid = current_sections.cid
                    JOIN users ON users.uid = current_sections.professor_uid
                    WHERE student_classes.student_uid = %s''', (student_ID,))
    classes_taken = cursor.fetchall()

    # Iterate over each class taken
    for class_taken in classes_taken:
        # Check for IP grade and skip this class if found
        if class_taken['grade'] == 'IP':
            continue
        total_credit_hours += class_taken['credit_hours']
    print (total_credit_hours)
    return total_credit_hours

################################################  TOTAL CS CREDIT HOURS FUNCTION  ##############################################################
# Calculate the total CS Credit hours
################################################################################################################################################
def get_total_cs_credit_hours(student_ID): 
    mydb = mydbfunc()
    cursor = mydb.cursor(dictionary=True)
    
    total_cs_credit_hours = 0

    # Retrieve the student's CS classes from the database
    cursor.execute('''SELECT *
                    FROM student_classes
                    JOIN current_sections ON student_classes.section_id = current_sections.section_id
                    JOIN classes ON classes.cid = current_sections.cid
                    JOIN users ON users.uid = current_sections.professor_uid
                    WHERE student_classes.student_uid = %s
                    AND classes.department = 'CSCI' ''', (student_ID,))
    cs_classes_taken = cursor.fetchall()

    # Retrieve the student's degree from the database
    cursor.execute('''SELECT degree
                    FROM students
                    WHERE uid = %s''', (student_ID,))
    degree = cursor.fetchone()['degree']


    # Iterate over each CS class taken
    for class_taken in cs_classes_taken:
        # Check for IP grade and skip this class if found
        if class_taken['grade'] == 'IP':
            continue
        total_cs_credit_hours += class_taken['credit_hours']


    if degree == 'Masters' and total_cs_credit_hours < 30:
        print("Adding non csci courses to make up to thirty for masters")
        # Retrieve the student's non-CSCI classes sorted by credit hours in descending order
        cursor.execute('''SELECT *
                        FROM student_classes
                        JOIN current_sections ON student_classes.section_id = current_sections.section_id
                        JOIN classes ON classes.cid = current_sections.cid
                        WHERE student_classes.student_uid = %s
                        AND classes.department != 'CSCI'
                        ORDER BY classes.credit_hours DESC''', (student_ID,))
        non_cs_classes_taken = cursor.fetchall()

        # Add the credit hours of the two highest non-CSCI classes to the total_cs_credit_hours
        for class_taken in non_cs_classes_taken[:2]:
            if class_taken['grade'] != 'IP':
                total_cs_credit_hours += class_taken['credit_hours']
    
    return total_cs_credit_hours
################################################  HAS ALL CORE COURSES ##############################################################
# Calculate the total Credit hours
##############################################################################################################################
def get_core_courses(student_ID): 
    mydb = mydbfunc()
    cur = mydb.cursor(dictionary=True)
    
    # Execute the SQL query
    cur.execute("""
        SELECT COUNT(DISTINCT cid) AS num_courses
        FROM student_classes
        WHERE cid IN (1, 2, 3)
        AND student_uid = %s
        GROUP BY student_uid
        HAVING num_courses = 3
    """, (student_ID,))

    # Fetch the results
    results = cur.fetchall()

    if results:
        print("The student has taken all three courses.")
        return True
    else:
        print("The student has not taken all three courses.")
        return False

################################################  NUM OF NON CS COURSES  ##############################################################
# Calculate the total numebr of non computer science courses in transcript
#######################################################################################################################################
def num_of_non_cs(id):
    mydb = mydbfunc()
    cur = mydb.cursor(dictionary = True)
    cur.execute("select dept1, dept2, dept3, dept3, dept4, dept5, dept6, dept7, dept8, dept9, dept10, dept11, dept12 from transcript where user_id = (%s)", (id,))
    x = cur.fetchone()
    num_non_cs = 0
    for i in range(1,12):
        if(x['dept' + str(i)] != 'CSCI'):
            num_non_cs = num_non_cs + 1

    if(num_non_cs > 2):
        return 0
    return 1

################################################ GET GRADES BELOW B  ##############################################################
# Checks how many grades are below b, if two are below b then badbad
################################################################################################################################
def get_grades_below_b(id):
    mydb = mydbfunc()
    cur = mydb.cursor(dictionary = True)
    cur.execute('''SELECT grade
                  FROM student_classes
                  JOIN current_sections ON student_classes.section_id = current_sections.section_id
                  JOIN classes ON classes.cid = current_sections.cid
                  WHERE student_classes.student_uid = %s''', (id,))
    grades = cur.fetchall()
    grades = [list(dct.values())[0] for dct in grades]
    possible_grades = ['IP', 'F', 'C', 'C+', 'B-', 'B', 'B+', 'A-', 'A']
    num_below_b = 0
    for grade in grades:
        if grade == 'IP':
            continue
        if possible_grades.index(grade) < possible_grades.index('B'):
         print(num_below_b)
         num_below_b += 1
         

    if (num_below_b >= 3): 
         print("placed on academic suspension")
         cur.execute("UPDATE students SET suspended = 'T' WHERE uid = (%s)", (id,))
         mydb.commit()
         
    return num_below_b
    

################################################  GRADUATION REQUESTS VIEW  ##############################################################
# View all graduation requests
##########################################################################################################################################
@app.route('/gradrequests', methods = ['GET', 'POST'])
def gradrequests():
    mydb = mydbfunc()
    cur = mydb.cursor(dictionary=True)
    if "user_type" not in session:
      return redirect("/")
    if session["user_type"] not in ["GS", "Admin"]:
      return redirect("/")
    
    cur.execute("SELECT grad_requests.approved, users.uid, grad_requests.advisor_id, CONCAT(users.fname, ' ', users.minit, ' ', users.lname) AS student_name, CONCAT(advisor.fname, ' ', advisor.minit, ' ', advisor.lname) AS advisor_name FROM grad_requests INNER JOIN users ON grad_requests.student_id = users.uid INNER JOIN users AS advisor ON grad_requests.advisor_id = advisor.uid;")
    x = cur.fetchall()
    user_type = session['user_type']
    print(x)

    for y in x:
      gradinfo = get_grad_year_sem(y["uid"])
      y["year"] = gradinfo[0]
      y["semester"] = gradinfo[1]

    cur.execute("SELECT * FROM valid_semesters")
    sems = cur.fetchall()
    valid_years = []
    valid_sems = ["Spring", "Summer", "Fall"]
    semesters = ["", "Spring", "Summer", "Fall"]

    for sem in sems:
      if sem["year"] not in valid_years:
        valid_years.append(sem["year"])

    if request.method == "POST":
      if "year" in request.form:
        lname = "%" + request.form["lname"] + "%"
        id = request.form["uid"] + "%"
        year = request.form["year"]
        sem = request.form["sem"]
        degree = request.form["degree"]
        aduid = request.form["aduid"]  + "%"
        audit = request.form["audit"]
        audit1 = 'T'
        audit2 = 'F'
        if audit == 'T':
          audit2 = 'T'
        if audit == 'F':
          audit1 = 'F'
        print(aduid)
        # cur.execute("SELECT grad_requests.approved, users.uid, grad_requests.advisor_id, CONCAT(users.fname, ' ', users.minit, ' ', users.lname) AS student_name, CONCAT(advisor.fname, ' ', advisor.minit, ' ', advisor.lname) AS advisor_name FROM grad_requests INNER JOIN users ON grad_requests.student_id = users.uid INNER JOIN users AS advisor ON grad_requests.advisor_id = advisor.uid LEFT JOIN applications ON applications.uid = users.uid WHERE users.uid LIKE %s AND users.lname LIKE %s AND applications.degree LIKE %s AND grad_requests.approved = %s", (id, lname, degree, audit))
        cur.execute("SELECT grad_requests.approved, users.uid, grad_requests.advisor_id, CONCAT(users.fname, ' ', users.minit, ' ', users.lname) AS student_name, CONCAT(advisor.fname, ' ', advisor.minit, ' ', advisor.lname) AS advisor_name FROM grad_requests INNER JOIN users ON grad_requests.student_id = users.uid INNER JOIN users AS advisor ON grad_requests.advisor_id = advisor.uid LEFT JOIN applications ON applications.uid = users.uid WHERE users.uid LIKE %s and users.lname LIKE %s AND applications.degree LIKE %s AND (grad_requests.approved = %s or grad_requests.approved = %s) AND advisor.uid LIKE %s", (id, lname, degree, audit1, audit2, aduid))
        x = cur.fetchall()

        print(x)

        for y in x:
          gradinfo = get_grad_year_sem(y["uid"])
          if year != "%":
            if int(gradinfo[0]) != int(year):
              print("year not match")
              x.remove(y)
              pass
          if sem != "%":
            if semesters[gradinfo[1]] != sem:
              print("sem not match")
              x.remove(y)
              pass
          y["year"] = gradinfo[0]
          y["semester"] = gradinfo[1]

        print(x)
        
        return render_template("gradrequests.html", x = x, user_type = user_type, valid_years = valid_years, valid_sems = valid_sems, current_year = year, current_sem = sem, current_degree = degree, current_audit = audit, semesters = semesters)

    return render_template("gradrequests.html", x = x, user_type = user_type, valid_years = valid_years, valid_sems = valid_sems, current_year = "%", current_sem = "%", current_degree = "%", current_audit = "%", semesters = semesters)

################################################  GRADUATION ACTION ##############################################################
# Allow student to graduate manually
#################################################################################################################################
@app.route('/graduate/<id>')
def graduate(id):
    mydb = mydbfunc()
    cur = mydb.cursor(dictionary=True)
    if "user_type" not in session:
      return redirect("/")
    if session['user_type'] != 'GS':
      return redirect('/')
    
    cur.execute("update users set user_type = 'Alumni' where uid = (%s)", (id,))
    mydb.commit()
    cur.execute("delete from grad_requests where student_id = (%s)", (id,))
    mydb.commit()
    cur.execute("delete from students where uid = (%s)", (id,))
    mydb.commit()

    return redirect(url_for('gradrequests'))

################################################  REJECT GRAD #############################################
#This rejects a grad student and removes them from the grad request table
###########################################################################################################
@app.route('/rejectgrad/<id>')
def rejectgrad(id):
    mydb = mydbfunc()
    cur = mydb.cursor(dictionary=True)
    if "user_type" not in session:
      return redirect("/")
    if session['user_type'] != 'GS':
      return redirect('/')
    #update database 
    cur.execute("delete from  grad_requests where student_id = (%s)", (id,))
    mydb.commit()
    cur.execute("delete from form1 where user_id = (%s)", (id,))
    mydb.commit()
    return redirect(url_for('gradrequests'))

################################################  ALUMNI VIEW ##############################################################
# View all alumni
############################################################################################################################
@app.route('/alumni', methods = ['GET', "POST"])
def alumni():
     mydb = mydbfunc()
     cur = mydb.cursor(dictionary = True)
     if "user_type" not in session:
      return redirect("/")
     if session["user_type"] not in ["GS", "Admin"]:
      return redirect('/')

     cur.execute("SELECT * FROM users LEFT JOIN applications ON users.uid = applications.uid WHERE user_type = 'Alumni'")
     x=cur.fetchall()
     
     for y in x:
      print(y)
      yearsem = get_grad_year_sem(y["uid"])
      y["year"] = yearsem[0]
      y["semester"] = yearsem[1]
      print(y)

     print(x)

     cur.execute("SELECT * FROM current_sections")
     apps = cur.fetchall()
     valid_years = []
     valid_semesters = ["Spring", "Summer", "Fall"]
     for app in apps:
      if app["year"] not in valid_years:
        valid_years.append(app["year"])


     user_type = session['user_type']

     if request.method == "POST":
      year = request.form["year"]
      sem = request.form["sem"]
      deg = request.form["degree"]
      lname = request.form["lname"] + "%"
      print(deg)

      cur.execute("SELECT * FROM users LEFT JOIN applications ON users.uid = applications.uid WHERE user_type = 'Alumni' AND lname LIKE %s AND degree LIKE %s", (lname, deg))
      x=cur.fetchall()
      print("HELLO")
      print(x)
     
      for y in x:
        yearsem = get_grad_year_sem(y["uid"])
        y["year"] = yearsem[0]
        y["semester"] = yearsem[1]
        print(yearsem)

      for y in x:
        if year != "%":
          print("year exists")
          if int(y["year"]) != int(year):
            print("year doesn't match")
            print(y["year"])
            print(year)
            x.remove(y)
            pass
        if sem != "%":
          print("sem exists")
          semesters = ["", "Spring", "Summer", "Fall"]
          if str(semesters[int(y["semester"])]) != str(sem):
            print(y["semester"])
            print(sem)
            print("sem doesnt match")
            x.remove(y)
            pass



      valid_years = []
      valid_semesters = ["Spring", "Summer", "Fall"]
      cur.execute("SELECT * FROM current_sections")
      apps = cur.fetchall()
      for app in apps:
        if app["year"] not in valid_years:
          valid_years.append(app["year"])


      user_type = session['user_type']
      return render_template("alumni.html", x = x, user_type = user_type, semesters = ["", "Spring", "Summer", "Fall"], valid_years = valid_years, current_year = year, current_sem = sem, current_deg = deg, semesters2 = ["Spring", "Summer", "Fall"], valid_sems = ["Spring", "Summer", "Fall"])

     return render_template("alumni.html", x = x, user_type = user_type, semesters = ["", "Spring", "Summer", "Fall"], valid_years = valid_years, current_year = "%", current_sem = "%", current_deg = "%", semesters2 = ["Spring", "Summer", "Fall"], valid_sems = ["Spring", "Summer", "Fall"])


################################################  ALUMNI DIRECTORY  ################################################
#Show all the info of said alumni
#####################################################################################################################
@app.route('/alumnidirectory/<id>', methods=['GET'])
def alumnidirectory(id):
    mydb = mydbfunc()
    cur = mydb.cursor(dictionary=True)
    if "user_type" not in session:
      return redirect("/")

    cur.execute("SELECT * FROM users WHERE uid = (%s)", (id,))
    y = cur.fetchone()
    
    return render_template("alumnidirectory.html", x=y)


################################################  PERSONAL ALUMNI INFO  ##############################################################
# View the users personal info of alumni such as email, name, etc
###############################################################################################################################
@app.route('/alumnipersonalinfo/<id>')
def alumnipersonalinfo(id):
    if 'user_type' not in session:
      return redirect('/')
    mydb = mydbfunc()
    cur = mydb.cursor(dictionary = True)
    cur.execute("SELECT * FROM users WHERE uid = (%s)", (id,))
    x = cur.fetchone()

    return render_template("alumnipersonalinfo.html", x = x)

################################################  PERSONAL INFO ALUMNI UPDATE  ##############################################################
# Update the alumni personal info
##############################################################################################################################################
@app.route('/alumnidirectory/<id>/update', methods=['POST'])
def update_alumni(id):
    mydb = mydbfunc()
    cur = mydb.cursor()
    if "user_type" not in session:
      return redirect("/")
    
    # Update the users table
    cur.execute("UPDATE users SET fname=%s, minit=%s, lname=%s, email=%s WHERE uid=%s", (
        request.form['fname'],
        request.form['minit'],
        request.form['lname'],
        request.form['email'],
        id
    ))
    mydb.commit()
    
    cur.execute("SELECT * FROM users WHERE uid=%s", (id,))
    updated_row = cur.fetchone()
   # print("Updated row in users table:", updated_row)

    return redirect(url_for('alumnidirectory', id=id))

################################################  ADVISOR - STUDENT MATCH  ##############################################################
# Display the advisor match ups with their students
#########################################################################################################################################
@app.route('/asmatch', methods=['GET', "POST"])
def asmatch():
    mydb = mydbfunc()
    cur = mydb.cursor(dictionary=True)
    if "user_type" not in session:
      return redirect("/")
    if session["user_type"] not in ["GS", "Admin"]:
      return redirect('/')

    # Modify the SQL query to include a join with the users table to get the advisor's information
    cur.execute("SELECT students.*, s.fname as student_fname, s.minit as student_minit, s.lname as student_lname, a.fname as advisor_fname, a.minit as advisor_minit, a.lname as advisor_lname FROM students LEFT JOIN users AS s ON students.uid = s.uid LEFT JOIN users AS a ON students.advisor_id = a.uid")
    x = cur.fetchall()

    user_type = session['user_type']

    if request.method == "POST":
      if "studentuid" in request.form:
        studentuid = request.form["studentuid"]
        studentlname = request.form["studentlname"]
        aduid = request.form["aduid"]
        adlname = request.form["adlname"]
        if studentuid == "":
          studentuid = "%"
        if studentlname == "":
          studentlname = "%"
        if aduid == "":
          aduid = "%"
        if adlname == "":
          adlname = "%"

        cur.execute("SELECT students.*, s.fname as student_fname, s.minit as student_minit, s.lname as student_lname, a.fname as advisor_fname, a.minit as advisor_minit, a.lname as advisor_lname FROM students LEFT JOIN users AS s ON students.uid = s.uid LEFT JOIN users AS a ON students.advisor_id = a.uid WHERE s.lname LIKE %s AND s.uid LIKE %s AND a.lname LIKE %s AND a.uid LIKE %s", (studentlname, studentuid, adlname, aduid))
        x = cur.fetchall()

        return render_template("asmatch.html", x=x, user_type=user_type)

    return render_template("asmatch.html", x=x, user_type=user_type)


####FIX CHANGE ADVISOR

################################################  CHANGE ADVISOR - STUDENT MATCH  #######################################################
# Change the advisor of a student
#########################################################################################################################################
@app.route('/changeadvisor/<id>', methods = ['GET'])
def changeadvisor(id):
    mydb = mydbfunc()
    cur = mydb.cursor(dictionary = True)
    if "user_type" not in session:
      return redirect("/")
    if session["user_type"] not in ["GS", "Admin"]:
      return redirect('/')
      # Get student info and their advisor's name
    cur.execute("""
                SELECT students.*, users.fname AS advisor_fname, users.minit AS advisor_minit, users.lname AS advisor_lname,
                      suser.fname AS student_fname, suser.minit AS student_minit, suser.lname AS student_lname
                FROM students
                LEFT JOIN users ON students.advisor_id = users.uid
                JOIN users AS suser ON students.uid = suser.uid
                WHERE students.uid = %s
            """, (id,)) 
    studentinfo = cur.fetchone()

    # Fetch all advisors from the users table
    cur.execute("SELECT users.* FROM users INNER JOIN faculty ON users.uid = faculty.uid WHERE users.user_type = 'Faculty' AND faculty.can_advise = 'T';")
    advisors = cur.fetchall()

    return render_template("changeadvisor.html", studentinfo=studentinfo, advisors=advisors, id = id)

################################################ PREREQUISITE CHECK DONE #######################################################
# Check if prerquisites are met
############################################################################################################################
def prereqmatch(id): 
    print("checking prereqs")
    result = 0
     #connect to database
    mydb = mydbfunc()
    cur = mydb.cursor(dictionary = True)
    # Retrieve the classes the student has taken
    # Define the query to retrieve the cids of the classes taken by a specific student
    query = "SELECT cid FROM student_classes WHERE student_uid = %s"

    # Execute the query
    cur.execute(query, (id,))

    # Retrieve the results
    taken_cids = cur.fetchall()
    print("Courses taken by student:")
    for cid in taken_cids:
        print("Taken course: ", cid['cid'])
        query = "SELECT prereq_cid FROM prerequisites WHERE class_cid = %s"
        cur.execute(query, (cid['cid'],))
        prereqs = cur.fetchall()
        print("Prerequisites for course", cid['cid'], ":")
        if not prereqs:
             print("No prerequisites found for course", cid['cid'])
        else:
            for prereq in prereqs:
                prereq_cid = prereq['prereq_cid']
                query = "SELECT * FROM student_classes WHERE student_uid = %s AND cid = %s"
                cur.execute(query, (id, prereq_cid))
                result = cur.fetchone()
                if not result:
                    print("Prerequisite", prereq_cid, "not taken by student", id)
                    print("Prereq Check FAILS")
                    return False
                else:
                    print("Prerequisite", prereq_cid, "taken by student", id)
                    
    print("all prereqs PASS")
    return True

 

################################################ UPDATE ADVISOR #######################################################
# Update the advisor of such student in the database
#########################################################################################################################
@app.route('/update_advisor/<id>', methods=['POST'])
def update_advisor(id):
    if "user_type" not in session:
      return redirect("/")
    if session["user_type"] not in ["GS", "Admin"]:
      return redirect('/')
    
    advisor_id = request.form['newAdvisor']
    mydb = mydbfunc()
    cur = mydb.cursor()
    print("advisor id: ", advisor_id)
    cur.execute('UPDATE students SET advisor_id = %s WHERE uid = %s', (advisor_id, id,))
    mydb.commit()
    print("2")
    #match the statements 
    # Modify the SQL query to include a join with the users table to get the advisor's information
    cur.execute("SELECT students.*, users.fname as advisor_fname, users.minit as advisor_minit, users.lname as advisor_lname FROM students LEFT JOIN users ON students.advisor_id = users.uid")
    x = cur.fetchall()
    print("3")
    user_type = session['user_type']

    return redirect(url_for('asmatch', x=x, user_type = user_type))

################################################  COMPARE 1F AND TRANSCRIPT DONE #############################################
#Function to check Form 1 and Transcript :) 
#########################################################################################################################
def comparef1andtranscript(id):
    print("Comparing form1 and transcript")
    #establish a connection
    mydb = mydbfunc()
    cur = mydb.cursor(dictionary = True)

    # query to check for missing class IDs in student_classes
    missing_form1_cids_query = """
        SELECT DISTINCT f.cid 
        FROM form1 f 
        WHERE f.user_id = %s 
        AND NOT EXISTS (
            SELECT 1 
            FROM student_classes sc 
            WHERE sc.student_uid = f.user_id 
            AND sc.cid = f.cid
        )
    """
    # execute the query with the specific user_id
    cur.execute(missing_form1_cids_query, (id,))
    
    # retrieve the results
    missing_form1_cids = cur.fetchall()
    
    print("Amount of missing id's in form 1: ", len(missing_form1_cids))
        # check for missing class IDs in student_classes
    if len(missing_form1_cids) == 0:
        print("Form1 == Transcript", id)
    else:
        print("Form1 != Transcript", id)
        return False
    return True

#faculty advisors view thesis
################################################  VIEW THESIS #############################################
#This approves the thesis of the phd student! 
##############################################################################################################
@app.route('/viewthesis/<id>')
def viewthesis(id):
    mydb = mydbfunc()
    cur = mydb.cursor(dictionary=True)
    if "user_type" not in session:
      return redirect("/")
    if session['user_type'] not in ['Admin', 'GS', 'Faculty']:
      return redirect('/')
    cur.execute("SELECT * FROM phd_thesis WHERE user_id = (%s)", (id,))
    x = cur.fetchone()
    cur.execute("SELECT * FROM users WHERE uid = (%s)", (id,))
    studentinfo = cur.fetchone()
    return render_template('thesis.html', x = x, id = id, studentinfo = studentinfo)

#faculty advisors can approve thesis
################################################  APPROVE THESIS #############################################
#This approves the thesis
#############################################################################################################
@app.route('/approvethesis/<id>')
def approvehere(id):
    mydb = mydbfunc()
    cur = mydb.cursor(dictionary=True)
    if "user_type" not in session:
      return redirect("/")
    if session['user_type'] != 'Faculty':
      return redirect('/')
    
    cur.execute("UPDATE phd_thesis SET approved = 'T' WHERE user_id = (%s)", (id,))
    mydb.commit()

    return redirect(url_for('viewthesis', id = id))
    

################################################  STUDENT ACCESS THESIS #############################################
#Students can view and change thesis
#############################################################################################################
@app.route('/studentaccessthesis/<id>', methods = ['GET','POST'])
def studentaccessthesis(id):
    mydb = mydbfunc()
    cur = mydb.cursor(dictionary=True)
    if "user_type" not in session:
      return redirect("/")
    if session['user_type'] != 'Student':
      return redirect('/')
    if int(session['uid']) != int(id):
      return redirect('/')
    cur.execute("SELECT * FROM phd_thesis WHERE user_id = (%s)", (id,))
    x = cur.fetchone()

    if request.method == 'POST':
      newthesis = request.form['thesis']
      if x:
          # Update existing thesis
          cur.execute("UPDATE phd_thesis SET thesis = (%s), approved = (%s) WHERE user_id = (%s)", (newthesis, 'F', id,))
      else:
          # Insert new thesis
          cur.execute("INSERT INTO phd_thesis (user_id, thesis, approved) VALUES (%s, %s, %s)", (id, newthesis, 'F',))
      mydb.commit()
      print("PHD succesfully submitted")
      return redirect(url_for('All_Student_Portal'))

    return render_template('studentthesis.html', x = x)

########################################################################################################################################
  #ACCOUNT CREATION PAGE (ALL)
    #creates an account
  #TODO: this one is bad, maybe use APPS 
    #--> should you even be able to create an account that is not an applicant? Should sysadmin add other accounts?
########################################################################################################################################
@app.route('/Account_Creation', methods = ['GET', 'POST'])
def Account_Creation():
  if "user_type" not in session:
    return redirect("/")
  # cursor = mydb.cursor(dictionary=True)

  # session['error_account_creation'] = ''
  # if request.method == 'POST':
  #   if 'first_name' in request.form and 'middle_initial' in request.form and 'last_name' in request.form and 'address' in request.form and 'birthday' in request.form and 'password' in request.form and 'uid' in request.form and 'user_type' in request.form:
  #     first_name = request.form['first_name']
  #     middle_initial = request.form['middle_initial']
  #     last_name = request.form['last_name']
  #     address = request.form['address']
  #     password = request.form['password']
  #     uid = request.form['uid']
  #     user_type = request.form['user_type']
  #     # email = request.form["email"]

  #     val = (fname,
  #            minit,
  #            lname,
  #            address,
  #            birthday,
  #            uid,
  #            password,
  #            user_type)
  #     cursor.execute('INSERT INTO users (first_name, middle_initial, last_name, address, birthday, uid, password_hash, user_type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', val)
  #     mydb.commit()
  #     #cursor.close()

  #     return redirect('/')
  #   else:
  #     session['error_account_creation'] = 'Please fill fields before clicking submit'

  return render_template('Account_Creation.html')



########################################################################################################################################
  #APPS SYSADMIN PORTAL PAGE (ALL)
  #TODO We want this review process to be automated, wherein the faculty reviewer can enter their scores into a review form.
########################################################################################################################################


#Combine Admin portals - create users, edit personal (not ssn, or uid), delete users, #review and decide, see apps (all fac)
@app.route('/', methods=['GET', 'POST'])
def login():
  mydb = mydbfunc()
  cur = mydb.cursor(dictionary=True)
  session.clear()
  # Login and create session variables
  if request.method == 'POST':
    email = request.form["email"]
    password = request.form.get("password")
    cur.execute("SELECT * FROM users")
    users = cur.fetchall()

    for user in users:
      if user['email'] == email and user['password'] == password:
        session['email'] = email
        session['type'] = user['user_type']
        session['user_type'] = user['user_type']

        cur.execute("SELECT * FROM users WHERE email = (%s)", (session['email'],))
        data = cur.fetchone()
        session['uid'] = data['uid']
        session['first_name'] = data['fname']
        session['middle_initial'] = data['minit']
        session['last_name'] = data['lname']
        session['address'] = data['address']
        
        return redirect('/Portal')
      
    #if you are a recommender
    email = request.form["email"]
    cur.execute("SELECT email FROM recs")
    recs = cur.fetchall()
    for rec in recs:
      if rec['email'] == email:
        session['email'] = email
        session['type'] = 'Recommender'
        session['user_type'] = 'Recommender'
        return redirect('/writeletter')

    return redirect('/')
  return render_template('login.html')

#Create account 
@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
  mydb = mydbfunc()
  cur = mydb.cursor(dictionary=True)
    
  user_types = ['Admin', 'GS', 'Faculty', 'Applicant', 'Student', 'Alumni', 'Registrar']
  #enter into database
  if request.method == 'POST':
    email = request.form['email']
    passw = request.form['password']
    fname = request.form['firstname']
    minit = request.form.get('minit')
    lname = request.form['lastname']
    address = request.form['address']
    ssn = request.form['ssn']
    is_type = request.form.get('user_type') 

    if not is_type:
      is_type = 'Applicant'
    #dup protection
    cur.execute("SELECT email FROM users")
    es = cur.fetchall()
    for em in es:
      if em['email'] == email:
        return render_template('create_account.html', error='Email in use', user_types = ['Admin', 'GS', 'Faculty', 'Applicant', 'Student', 'Alumni', 'Registrar'])
    cur.execute("SELECT ssn FROM users")
    ss = cur.fetchall()
    for sn in ss:
      if sn['ssn'] == ssn:
        return render_template('create_account.html', error='SSN in use', user_types = ['Admin', 'GS', 'Faculty', 'Applicant', 'Student', 'Alumni', 'Registrar'])
    cur.execute("INSERT INTO users (fname, minit, lname, email, password, address, ssn, user_type) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (fname, minit, lname, email, passw, address, ssn, is_type,))
    mydb.commit()

    cur.execute("SELECT uid FROM users WHERE ssn = (%s)", (ssn,))
    uid = cur.fetchone()['uid']

    #student creation
    if is_type == 'Student':
      advisor = request.form.get('ad_id')
      masters = request.form.get('masters')
      phd = request.form.get('phd')

      cur.execute("SELECT uid FROM faculty WHERE can_advise = (%s)", ('T',))
      advises = cur.fetchall()
      if advisor:
        advisor = int(advisor)
      x = 'no'
      for ads in advises:
        if ads['uid'] == advisor:
          x = 'yes'
      if x == 'no':
        return render_template('create_account.html', error='invalid advisor ID', user_types = ['Admin', 'GS', 'Faculty', 'Applicant', 'Student', 'Alumni', 'Registrar'])


      if masters:
        cur.execute("INSERT INTO students (uid, degree, advisor_id) VALUES (%s,%s,%s)", (uid, 'Masters', advisor))  
      elif phd:
        cur.execute("INSERT INTO students (uid, degree, advisor_id) VALUES (%s,%s,%s)", (uid, 'PhD', advisor))  
      else:
        cur.execute("INSERT INTO students (uid, degree, advisor_id) VALUES (%s,%s,%s)", (uid, 'Masters', advises[0]['uid']))  
      mydb.commit()
    #faculty creation
    elif is_type == 'Faculty':
      dept = request.form.get('dept')
      is_cac = request.form.get('cac')
      can_teach = request.form.get('teach')
      can_advise = request.form.get('advise')
      can_review = request.form.get('review')
      if not is_cac:
        is_cac = 'F'
      if not can_teach:
        can_teach = 'F'
      if not can_advise:
        can_advise = 'F'
      if not can_review:
        can_review = 'F'
      cur.execute("INSERT INTO faculty VALUES (%s,%s,%s,%s,%s,%s)", (uid, dept, is_cac, can_teach, can_advise, can_review))  
      mydb.commit()

    return redirect('/Portal')
  
  return render_template('create_account.html', user_types=user_types)


################################################ VIEW ALL APPLICATIONS #############################################
#Students can view and change thesis
####################################################################################################################
@app.route('/viewallapps', methods=['GET', 'POST'])
def viewallapps():
    if "user_type" not in session:
      return redirect('/')
    if session['type'] not in ['Admin', 'GS', 'Faculty']:
      return redirect('/')
    mydb = mydbfunc()
    cur = mydb.cursor(dictionary=True)
    id = session['uid']
    print(id)
    cur.execute("SELECT * FROM users WHERE uid = (%s)", (id,))
    facultyinfo = cur.fetchone()
    cur.execute("SELECT * FROM users LEFT JOIN applications ON users.uid = applications.uid WHERE user_type = (%s)", ('Applicant',))
    users = cur.fetchall()
    cur.execute("SELECT * FROM users INNER JOIN applications ON users.uid=applications.uid INNER JOIN reviews ON applications.uid=reviews.uid WHERE applications.status = (%s) AND reviews.reviewer_id IS NOT NULL HAVING COUNT(reviews.reviewer_id) > 0", ('complete',))
    decides = cur.fetchall()
    cur.execute("SELECT * FROM users INNER JOIN applications ON users.uid = applications.uid WHERE applications.status = (%s)", ('acceptdeposit',))
    admit = cur.fetchall()

    valid_years = [2020, 2021, 2022, 2023, 2024]
    valid_sems = ["Spring", "Summer", "Fall"]

    if request.method == "POST":
      if "uid" in request.form:
        lname = "%" + request.form["lname"] + "%"
        id = request.form["uid"] + "%"
        degree = request.form["degree"]
        year = request.form["year"]
        sem = request.form["sem"]
        print(lname)
        print(id)

        cur.execute("SELECT * FROM users WHERE uid = (%s)", (session["uid"], ))
        facultyinfo = cur.fetchone()
        cur.execute("SELECT * FROM users LEFT JOIN applications ON users.uid = applications.uid WHERE user_type = (%s) and users.lname LIKE %s and users.uid LIKE %s and degree LIKE %s and year LIKE %s and semester LIKE %s", ('Applicant', lname, id, degree, year, sem))
        users = cur.fetchall()
        print(users)
        cur.execute("SELECT * FROM users INNER JOIN applications ON users.uid=applications.uid INNER JOIN reviews ON applications.uid=reviews.uid WHERE applications.status = (%s) AND users.lname LIKE %s AND users.uid LIKE %s AND reviews.reviewer_id IS NOT NULL HAVING COUNT(reviews.reviewer_id) > 0", ('complete', lname, id))
        decides = cur.fetchall()
        print(decides)
        cur.execute("SELECT * FROM users INNER JOIN applications ON users.uid = applications.uid WHERE applications.status = (%s) AND users.lname LIKE %s AND users.uid LIKE %s", ('acceptdeposit', lname, id))
        admit = cur.fetchall()
        print(admit)
        return render_template("view_all_apps.html", users=users, facultyinfo=facultyinfo, decides=decides, admit=admit, valid_years = valid_years, valid_sems = valid_sems, current_year = year, current_sem = sem, current_degree = degree)

    return render_template("view_all_apps.html", users=users, facultyinfo=facultyinfo, decides=decides, admit=admit, valid_years = valid_years, valid_sems = valid_sems, current_year = "%", current_sem = "%", current_degree = "%")

################IM SORRY BEN IM EDITING YOUR CODE ILY##########
# All I am doing is making different directories so that I can make the portal better I SORRY
################IM SORRY BEN IM EDITING YOUR CODE ILY##########

@app.route('/viewdecideapps', methods=['GET', 'POST'])
def viewdecideapps():
    if "user_type" not in session:
      return redirect('/')
    if session['type'] not in ['Admin', 'GS', 'Faculty']:
      return redirect('/')
    mydb = mydbfunc()
    cur = mydb.cursor(dictionary=True)
    id = session['uid']
    print(id)
    cur.execute("SELECT * FROM users WHERE uid = (%s)", (id,))
    facultyinfo = cur.fetchone()
    cur.execute("SELECT * FROM users WHERE user_type = (%s)", ('Applicant',))
    users = cur.fetchall()
    cur.execute("SELECT * FROM users INNER JOIN applications ON users.uid=applications.uid INNER JOIN reviews ON applications.uid=reviews.uid WHERE applications.status = (%s) AND reviews.reviewer_id IS NOT NULL GROUP BY users.uid", ('complete',))
    decides = cur.fetchall()
    cur.execute("SELECT * FROM users INNER JOIN applications ON users.uid = applications.uid WHERE applications.status = (%s)", ('acceptdeposit',))
    admit = cur.fetchall()
    print(decides)

    if request.method == "POST":
      if "uid" in request.form:
        lname = "%" + request.form["lname"] + "%"
        id = request.form["uid"] + "%"
        print(lname)
        print(id)

        cur.execute("SELECT * FROM users WHERE uid = (%s)", (session["uid"], ))
        facultyinfo = cur.fetchone()
        cur.execute("SELECT * FROM users WHERE user_type = (%s) and lname LIKE %s and uid LIKE %s", ('Applicant', lname, id))
        users = cur.fetchall()
        print(users)
        cur.execute("SELECT * FROM users INNER JOIN applications ON users.uid=applications.uid INNER JOIN reviews ON applications.uid=reviews.uid WHERE applications.status = (%s) AND users.lname LIKE %s AND users.uid LIKE %s AND reviews.reviewer_id IS NOT NULL GROUP BY users.uid", ('complete', lname, id))
        decides = cur.fetchall()
        print(decides)
        cur.execute("SELECT * FROM users INNER JOIN applications ON users.uid = applications.uid WHERE applications.status = (%s) AND users.lname LIKE %s AND users.uid LIKE %s", ('acceptdeposit', lname, id))
        admit = cur.fetchall()
        print(admit)
        return render_template("view_decide_apps.html", users=users, facultyinfo=facultyinfo, decides=decides, admit=admit)

    return render_template("view_decide_apps.html", users=users, facultyinfo=facultyinfo, decides=decides, admit=admit)

################IM SORRY BEN IM EDITING YOUR CODE ILY##########
# All I am doing is making different directories so that I can make the portal better I SORRY
################IM SORRY BEN IM EDITING YOUR CODE ILY##########

################IM SORRY BEN IM EDITING YOUR CODE ILY##########
# All I am doing is making different directories so that I can make the portal better I SORRY
################IM SORRY BEN IM EDITING YOUR CODE ILY##########

@app.route('/admitstudents', methods=['GET', 'POST'])
def admitstudents():
    if "user_type" not in session:
      return redirect('/')
    if session['type'] not in ['Admin', 'GS']:
      return redirect('/')
    
    mydb = mydbfunc()
    cur = mydb.cursor(dictionary=True)
    id = session['uid']
    print(id)
    cur.execute("SELECT * FROM users WHERE uid = (%s)", (id,))
    facultyinfo = cur.fetchone()
    cur.execute("SELECT * FROM users WHERE user_type = (%s)", ('Applicant',))
    users = cur.fetchall()
    cur.execute("SELECT * FROM users INNER JOIN applications ON users.uid=applications.uid INNER JOIN reviews ON applications.uid=reviews.uid WHERE applications.status = (%s) AND reviews.reviewer_id IS NOT NULL GROUP BY users.uid", ('complete',))
    decides = cur.fetchall()
    cur.execute("SELECT * FROM users INNER JOIN applications ON users.uid = applications.uid WHERE applications.status = (%s)", ('acceptdeposit',))
    admit = cur.fetchall()
    # print(admit)
    if request.method == "POST":
      if "uid" in request.form:
        lname = "%" + request.form["lname"] + "%"
        id = request.form["uid"] + "%"
        print(lname)
        print(id)

        cur.execute("SELECT * FROM users WHERE uid = (%s)", (session["uid"], ))
        facultyinfo = cur.fetchone()
        cur.execute("SELECT * FROM users WHERE user_type = (%s) and lname LIKE %s and uid LIKE %s", ('Applicant', lname, id))
        users = cur.fetchall()
        print(users)
        cur.execute("SELECT * FROM users INNER JOIN applications ON users.uid=applications.uid INNER JOIN reviews ON applications.uid=reviews.uid WHERE applications.status = (%s) AND users.lname LIKE %s AND users.uid LIKE %s AND reviews.reviewer_id IS NOT NULL GROUP BY users.uid", ('complete', lname, id))
        decides = cur.fetchall()
        print(decides)
        cur.execute("SELECT * FROM users INNER JOIN applications ON users.uid = applications.uid WHERE applications.status = (%s) AND users.lname LIKE %s AND users.uid LIKE %s", ('acceptdeposit', lname, id))
        admit = cur.fetchall()
        print(admit)
        return render_template("admitstudents.html", users=users, facultyinfo=facultyinfo, decides=decides, admit=admit)
    return render_template("admitstudents.html", users=users, facultyinfo=facultyinfo, decides=decides, admit=admit)

################IM SORRY BEN IM EDITING YOUR CODE ILY##########
# All I am doing is making different directories so that I can make the portal better I SORRY
################IM SORRY BEN IM EDITING YOUR CODE ILY##########

################################################ VIEW ALL APPLICATIONS #############################################
#Students can view and change thesis
####################################################################################################################
@app.route('/viewallreviews', methods=['GET', 'POST'])
def viewallreviews():
    if "user_type" not in session:
      return redirect('/')
    if session['type'] not in ['Admin', 'GS', 'Faculty']:
      return redirect('/')
    mydb = mydbfunc()
    cur = mydb.cursor(dictionary=True)
    id = session['uid']
    print(id)
    cur.execute("SELECT * FROM users WHERE user_type = (%s)", ('Applicant',))
    users = cur.fetchall()
    cur.execute("SELECT is_CAC, can_teach, can_advise, can_review FROM faculty WHERE uid = (%s)", (session['uid'],))
    fac = cur.fetchone()
    #for CAC and Reviewer
    cur.execute("SELECT * FROM users INNER JOIN applications ON users.uid=applications.uid INNER JOIN reviews ON applications.uid=reviews.uid WHERE applications.status = (%s) AND reviews.reviewer_id IS NOT NULL GROUP BY users.uid", ('complete',))
    decides = cur.fetchall()
    cur.execute("SELECT COALESCE (users.uid, reviews.uid) AS uid, users.fname, users.minit, users.lname, users.email, users.password, users.address, users.ssn, users.user_type, applications.status, applications.transcript, applications.degree, applications.semester, applications.year, applications.experience, applications.aoi, applications.received, reviews.rating, reviews.deficiency, reviews.reason, reviews.advisor_id, reviews.comments, reviews.reviewer_id FROM users INNER JOIN applications ON users.uid = applications.uid LEFT JOIN reviews ON users.uid = reviews.uid WHERE applications.status = 'complete' AND users.uid NOT IN (SELECT uid FROM reviews WHERE reviewer_id = %s) GROUP BY users.uid HAVING COUNT(reviews.reviewer_id) < 3 AND (reviews.reviewer_id IS NULL OR reviews.reviewer_id != %s)", (session['uid'], session['uid']))
    reviews = cur.fetchall()
    if request.method == "POST":
      if "uid" in request.form:
        lname = "%" + request.form["lname"] + "%"
        id = request.form["uid"] + "%"

        cur.execute("SELECT * FROM users WHERE uid = (%s)", (session["uid"], ))
        facultyinfo = cur.fetchone()
        cur.execute("SELECT * FROM users WHERE user_type = (%s) and lname LIKE %s and uid LIKE %s", ('Applicant', lname, id))
        users = cur.fetchall()

        cur.execute("SELECT is_CAC, can_teach, can_advise, can_review FROM faculty WHERE uid = (%s)", (session['uid'],))
        fac = cur.fetchone()
        #for CAC and Reviewer
        cur.execute("SELECT * FROM users INNER JOIN applications ON users.uid=applications.uid INNER JOIN reviews ON applications.uid=reviews.uid WHERE applications.status = (%s) AND reviews.reviewer_id IS NOT NULL GROUP BY users.uid", ('complete',))
        decides = cur.fetchall()
        cur.execute("SELECT COALESCE (users.uid, reviews.uid) AS uid, users.fname, users.minit, users.lname, users.email, users.password, users.address, users.ssn, users.user_type, applications.status, applications.transcript, applications.degree, applications.semester, applications.year, applications.experience, applications.aoi, applications.received, reviews.rating, reviews.deficiency, reviews.reason, reviews.advisor_id, reviews.comments, reviews.reviewer_id FROM users INNER JOIN applications ON users.uid = applications.uid LEFT JOIN reviews ON users.uid = reviews.uid WHERE applications.status = 'complete' AND users.uid NOT IN (SELECT uid FROM reviews WHERE reviewer_id = %s) AND users.lname LIKE %s AND users.uid LIKE %s GROUP BY users.uid HAVING COUNT(reviews.reviewer_id) < 3 AND (reviews.reviewer_id IS NULL OR reviews.reviewer_id != %s)", (session['uid'], lname, id, session['uid']))
        reviews = cur.fetchall()

        return render_template("view_all_review_apps.html", users=users, reviews=reviews, fac=fac, decides=decides)

    return render_template("view_all_review_apps.html", users=users, reviews=reviews, fac=fac, decides=decides)



@app.route('/homeapps', methods=['GET', 'POST'])
def homeapps():
  mydb = mydbfunc()
  cur = mydb.cursor(dictionary=True)
  if "user_type" not in session:
    return redirect('/')
  #Specific homepage for user type
  if session['type'] not in ['Admin', 'Applicant', 'GS', 'Faculty']:
    return redirect('/')

  #if applicant, gather if it has a past application
  if session['type'] == 'Applicant':
    cur.execute("SELECT * FROM applications WHERE uid = (%s)", (session['uid'],))
    app = cur.fetchone()
    cur.execute("SELECT * FROM recs WHERE uid = (%s)", (session['uid'],))
    sent = cur.fetchall()

    return render_template("homeapps.html", app=app, sent=sent)
  
  #if admin
  if session['type'] == 'Admin':
    cur.execute("SELECT * FROM users WHERE user_type = (%s)", ('Applicant',))
    users = cur.fetchall()
    cur.execute("SELECT * FROM users INNER JOIN applications ON users.uid=applications.uid INNER JOIN reviews ON applications.uid=reviews.uid WHERE applications.status = (%s) AND reviews.reviewer_id IS NOT NULL GROUP BY users.uid", ('complete',))
    decides = cur.fetchall()
    cur.execute("SELECT COALESCE (users.uid, reviews.uid) AS uid, users.fname, users.minit, users.lname, users.email, users.password, users.address, users.ssn, users.user_type, applications.status, applications.transcript, applications.degree, applications.semester, applications.year, applications.experience, applications.aoi, applications.received, reviews.rating, reviews.deficiency, reviews.reason, reviews.advisor_id, reviews.comments, reviews.reviewer_id FROM users INNER JOIN applications ON users.uid = applications.uid LEFT JOIN reviews ON users.uid = reviews.uid WHERE applications.status = 'complete' AND users.uid NOT IN (SELECT uid FROM reviews WHERE reviewer_id = %s) GROUP BY users.uid HAVING COUNT(reviews.reviewer_id) < 3 AND (reviews.reviewer_id IS NULL OR reviews.reviewer_id != %s)", (session['uid'], session['uid'])) 
    reviews = cur.fetchall()
    cur.execute("SELECT * FROM users INNER JOIN applications ON users.uid = applications.uid WHERE applications.status = (%s)", ('acceptdeposit',))
    admit = cur.fetchall()
    return render_template("homeapps.html", users=users, decides=decides, reviews=reviews, admit=admit)
  
  #if GS
  if session['type'] == "GS":
    cur.execute("SELECT * FROM users WHERE user_type = (%s)", ('Applicant',))
    users = cur.fetchall()
    cur.execute("SELECT * FROM users INNER JOIN applications ON users.uid=applications.uid INNER JOIN reviews ON applications.uid=reviews.uid WHERE applications.status = (%s) AND reviews.reviewer_id IS NOT NULL GROUP BY users.uid", ('complete',))
    decides = cur.fetchall()
    cur.execute("SELECT * FROM users INNER JOIN applications ON users.uid = applications.uid WHERE applications.status = (%s)", ('acceptdeposit',))
    admit = cur.fetchall()
    print(admit)
    return render_template("homeapps.html", users=users, decides=decides, admit=admit)
  
  #if Faculty
  if session['type'] == "Faculty":
    cur.execute("SELECT * FROM users WHERE user_type = (%s)", ('Applicant',))
    users = cur.fetchall()
    cur.execute("SELECT is_CAC, can_teach, can_advise, can_review FROM faculty WHERE uid = (%s)", (session['uid'],))
    fac = cur.fetchone()
    #for CAC and Reviewer
    cur.execute("SELECT * FROM users INNER JOIN applications ON users.uid=applications.uid INNER JOIN reviews ON applications.uid=reviews.uid WHERE applications.status = (%s) AND reviews.reviewer_id IS NOT NULL GROUP BY users.uid", ('complete',))
    decides = cur.fetchall()
    cur.execute("SELECT COALESCE (users.uid, reviews.uid) AS uid, users.fname, users.minit, users.lname, users.email, users.password, users.address, users.ssn, users.user_type, applications.status, applications.transcript, applications.degree, applications.semester, applications.year, applications.experience, applications.aoi, applications.received, reviews.rating, reviews.deficiency, reviews.reason, reviews.advisor_id, reviews.comments, reviews.reviewer_id FROM users INNER JOIN applications ON users.uid = applications.uid LEFT JOIN reviews ON users.uid = reviews.uid WHERE applications.status = 'complete' AND users.uid NOT IN (SELECT uid FROM reviews WHERE reviewer_id = %s) GROUP BY users.uid HAVING COUNT(reviews.reviewer_id) < 3 AND (reviews.reviewer_id IS NULL OR reviews.reviewer_id != %s)", (session['uid'], session['uid']))
    reviews = cur.fetchall()
    print(reviews)
    return render_template("homeapps.html", users=users, reviews=reviews, fac=fac, decides=decides)

  return redirect('/')

@app.route('/remove_user/<id>', methods=['GET', 'POST'])
def remove_user(id):
  mydb = mydbfunc()
  cur = mydb.cursor(dictionary=True)
  if "user_type" not in session:
    return redirect('/')
  if session['type'] != 'Admin':
    return redirect('/')

  cur.execute("UPDATE students SET advisor_id = %s WHERE advisor_id = %s", (session["uid"],id))
  cur.execute("UPDATE current_sections SET professor_uid = %s WHERE professor_uid = %s", (session["uid"], id))
  cur.execute("UPDATE grad_requests SET advisor_id = %s WHERE advisor_id = %s", (session["uid"], id))
  cur.execute("UPDATE reviews SET advisor_id = %s WHERE advisor_id = %s", (session["uid"], id))
  cur.execute("DELETE FROM advisor_hold_classes WHERE student_uid = %s", (id,))
  cur.execute("DELETE FROM applications WHERE uid = (%s)", (id,))
  cur.execute("DELETE FROM degrees WHERE uid = (%s)", (id,))
  cur.execute("DELETE FROM gres WHERE uid = (%s)", (id,))
  cur.execute("DELETE FROM recs WHERE uid = (%s)", (id,))
  cur.execute("DELETE FROM reviews WHERE uid = (%s)", (id,))
  cur.execute("DELETE FROM student_classes WHERE student_uid = (%s)", (id,))
  cur.execute("DELETE FROM form1 WHERE user_id = (%s)", (id,))
  cur.execute("DELETE FROM grad_requests WHERE student_id = (%s)", (id,))
  cur.execute("DELETE FROM phd_thesis WHERE user_id = (%s)", (id,))
  cur.execute("DELETE FROM faculty WHERE uid = (%s)", (id,))
  cur.execute("DELETE FROM students WHERE uid = (%s)", (id,))
  cur.execute("DELETE FROM users WHERE uid = (%s)", (id,))
  mydb.commit()
  return redirect('/all_users')

@app.route('/all_users', methods = ["GET", "POST"])
def all_users():
  if "user_type" not in session:
    return redirect("/")
  if session['type'] != 'Admin':
    return redirect('/')

  mydb = mydbfunc()
  cur = mydb.cursor(dictionary=True)

  valid_types = ["Applicant", "Faculty", "Admin", "Student", "Registrar", "GS", "Alumni"]


  cur.execute("SELECT * FROM users")
  users = cur.fetchall()

  if request.method == "POST":
    if "type" in request.form:
      uid = request.form["uid"] + "%"
      lname = "%" + request.form["lname"] + "%"
      type1 = "%" + request.form["type"] + "%"

      cur.execute("SELECT * FROM users WHERE uid LIKE %s AND lname LIKE %s AND user_type LIKE %s", (uid, lname, type1))
      users = cur.fetchall()
      return render_template("all_users.html", users = users, valid_types = valid_types, current_type = type1)

  return render_template("all_users.html", users = users, valid_types = valid_types, current_type = "%")


@app.route('/user_page/<id>', methods=['GET', 'POST'])
def user_page(id):
  mydb = mydbfunc()
  cur = mydb.cursor(dictionary=True)

  if "user_type" not in session:
    return redirect("/")
  if session['type'] != 'Admin':
    return redirect('/')
  
  user_types = ['Admin', 'GS', 'Faculty', 'Applicant', 'Student', 'Alumni', 'Registrar']
  cur.execute("SELECT * FROM users WHERE uid = (%s)", (id,))
  cur_user = cur.fetchone()

  if request.method == 'POST':
    email = request.form.get('email')
    passw = request.form.get('password')
    fname = request.form.get('firstname')
    minit = request.form.get('minit')
    lname = request.form.get('lastname')
    address = request.form.get('address')
    #ssn = request.form.get('ssn')
    #is_type = request.form.get('user_type') 
    mydb = mydbfunc()
    cur = mydb.cursor(dictionary=True)
    if email != '':
      #check if email exists
      cur.execute('SELECT email FROM users') 
      emails = cur.fetchall()
      for em in emails:
        if em['email'] == email:
          error = 'Email already in use'
          user_types = ['Admin', 'GS', 'Faculty', 'Applicant', 'Student', 'Alumni', 'Registrar']
          cur.execute("SELECT * FROM users WHERE uid = (%s)", (id,))
          cur_user = cur.fetchone()

          return render_template("user_page.html", user_types=user_types, cur_user=cur_user, id=id, error=error)
        

      cur.execute("UPDATE users SET email = (%s) WHERE uid = (%s)", (email, id,))
      mydb.commit()
    elif passw != '':
      cur.execute("UPDATE users SET password = (%s) WHERE uid = (%s)", (passw, id,))
      mydb.commit()
    elif fname != '':
      cur.execute("UPDATE users SET fname = (%s) WHERE uid = (%s)", (fname, id,))
      mydb.commit()
    elif minit != '':
      cur.execute("UPDATE users SET minit = (%s) WHERE uid = (%s)", (minit, id,))
      mydb.commit()
    elif lname != '':
      cur.execute("UPDATE users SET lname = (%s) WHERE uid = (%s)", (lname, id,))
      mydb.commit()
    elif address != '':
      cur.execute("UPDATE users SET address = (%s) WHERE uid = (%s)", (address, id,))
      mydb.commit()
    '''
    elif ssn != '':
      #check if ssn exists
      cur.execute('SELECT ssn FROM users') 
      ssns = cur.fetchall()
      for s in emails:
        if s['ssn'] == ssns:
          error = 'ssn already in use'
          return redirect(url_for('user_page'), error=error)
      cur.execute("UPDATE users SET ssn = (%s) WHERE uid = (%s)", (ssn, id,))
      mydb.commit()
    elif is_type != '':
      cur.execute("SELECT user_type FROM users WHERE uid = (%s)", (id,))
      former = cur.fetchone()['user_type']
      cur.execute("UPDATE users SET user_type = (%s) WHERE uid = (%s)", (is_type, id,))
      #if faculty 
      if is_type == 'Faculty':
        dept = request.form.get('dept')
        is_cac = request.form.get('cac')
        can_teach = request.form.get('teach')
        can_advise = request.form.get('advise')
        can_review = request.form.get('review')
        if former != 'Faculty':
          cur.execute("INSERT INTO faculty uid = (%s)", (id,))
        if dept != '':
          cur.execute("UPDATE faculty SET dept = (%s) WHERE uid = (%s)", (dept, id))
        if is_cac != '':
          cur.execute("UPDATE faculty SET is_CAC = (%s) WHERE uid = (%s)", (is_cac, id))
        if can_teach != '':
          cur.execute("UPDATE faculty SET can_teach = (%s) WHERE uid = (%s)", (can_teach, id))
        if can_advise != '':
          cur.execute("UPDATE faculty SET can_advise= (%s) WHERE uid = (%s)", (can_advise, id))
        if can_review != '':
          cur.execute("UPDATE faculty SET can_review = (%s) WHERE uid = (%s)", (can_review, id))
        
    
      #if student
      elif is_type == 'Student':
        advisor = request.form.get('ad_id')
        masters = request.form.get('masters')
        phd = request.form.get('phd')
        suspended = request.form.get('suspended')
        if former != 'Student':
          cur.execute("INSERT INTO students uid = (%s)", (id,))
        if advisor != '':
          cur.execute("UPDATE students SET advisor_id = (%s) WHERE uid = (%s)", (advisor, id))
        if masters != '':
          cur.execute("UPDATE students SET degree = (%s) WHERE uid = (%s)", (masters, id))
        if phd != '':
          cur.execute("UPDATE students SET degree = (%s) WHERE uid = (%s)", (phd, id))
        if suspended != '':
          cur.execute("UPDATE students SET suspended = (%s) WHERE uid = (%s)", (suspended, id))
        '''
      
    mydb.commit()
    return redirect('/all_users')

  return render_template("user_page.html", user_types=user_types, cur_user=cur_user, id=id)

@app.route('/view_apps/<id>', methods=['GET', 'POST'])
def view_apps(id):
  mydb = mydbfunc()
  cur = mydb.cursor(dictionary=True)
  if "user_type" not in session:
    return redirect('/')
  if session['type'] not in ['Admin', 'GS', 'Faculty']:
    return redirect('/')

  cur.execute("SELECT * FROM applications WHERE uid = (%s)", (id,))
  app = cur.fetchone()
  if not app:
    print("not app")
    return redirect('/Portal')
  cur.execute("SELECT * FROM recs WHERE uid = (%s)", (id,))
  rec = cur.fetchall()
  cur.execute("SELECT * FROM degrees WHERE uid = (%s)", (id,))
  deg = cur.fetchall()
  cur.execute("SELECT * FROM users WHERE uid = (%s)", (id,))
  user = cur.fetchone()
  cur.execute("SELECT * FROM gres WHERE uid = (%s)", (id,))
  gre = cur.fetchone()

  if request.method == 'POST':
    trans = request.form.get('trans')
    if trans:
      cur.execute("UPDATE applications SET transcript = (%s) WHERE uid= (%s)", (trans, id,))
      cur.execute("UPDATE applications SET status = (%s) WHERE uid = (%s)", ('complete', id,))
    mydb.commit()
    return redirect('/Portal')
  
  return render_template("view_apps.html", deg=deg, gre=gre, rec=rec, app=app, user=user)

#application
@app.route('/application', methods=['GET', 'POST'])
def application():
  mydb = mydbfunc()
  cur = mydb.cursor(dictionary=True)
  if "user_type" not in session:
    return redirect('/')
  if session['type'] not in ['Admin', 'Applicant', 'GS', 'Faculty']:
    return redirect('/')
  
  if request.method == 'POST':
    if session['type'] == 'Faculty' or session['type'] == 'GS' or session['type'] == 'Admin':
      cur.execute("SELECT * FROM faculty WHERE uid = (%s)", (session['uid'],))
      fac = cur.fetchone()

      if session['type'] == 'Admin':
        reviewuid = request.form.get('reviewappadmin')
        decideuid = request.form.get('decideappadmin')
  
        if reviewuid:
          cur.execute("SELECT * FROM users WHERE uid = (%s)", (reviewuid,))
          user = cur.fetchone()
          cur.execute("SELECT * FROM applications WHERE uid = (%s)", (reviewuid,))
          app = cur.fetchone()
          cur.execute("SELECT * FROM degrees WHERE uid = (%s)", (reviewuid,))
          degs = cur.fetchall()
          cur.execute("SELECT * FROM gres WHERE uid = (%s)", (reviewuid,))
          gre = cur.fetchone()
          cur.execute("SELECT * FROM recs WHERE uid = (%s)", (reviewuid,))
          recs = cur.fetchall()

          return render_template('application.html', app=app, form='review', user=user, degs=degs, recs=recs, gre=gre)
        elif decideuid:
          cur.execute("SELECT * FROM reviews WHERE uid = (%s)", (decideuid,))
          reviews = cur.fetchall()
          cur.execute("SELECT * FROM applications WHERE uid = (%s)", (decideuid,))
          app = cur.fetchone()
          cur.execute("SELECT * FROM users WHERE uid = (%s)", (decideuid,))
          user = cur.fetchone()
          cur.execute("SELECT * FROM recs WHERE uid = (%s)", (decideuid,))
          recs = cur.fetchall()
          cur.execute("SELECT rating FROM reviews WHERE uid = (%s)", (decideuid,))
          avgs = cur.fetchall()
          review_avg = 0
          for a in avgs:
            review_avg += int(a['rating'])
          review_avg = review_avg/len(avgs)

          return render_template("decide_cac.html", reviews=reviews, app=app, user=user, review_avg=review_avg, recs=recs)

      reviewuid = request.form.get('reviewapp')
      decideuid = request.form.get('decideapp')
      if fac:
        if reviewuid:
          if fac['can_review'] == 'T' or fac['is_CAC'] == 'T':
            #Review for CAC and Reviewer
            cur.execute("SELECT * FROM users WHERE uid = (%s)", (reviewuid,))
            user = cur.fetchone()
            cur.execute("SELECT * FROM applications WHERE uid = (%s)", (reviewuid,))
            app = cur.fetchone()
            cur.execute("SELECT * FROM degrees WHERE uid = (%s)", (reviewuid,))
            degs = cur.fetchall()
            cur.execute("SELECT * FROM gres WHERE uid = (%s)", (reviewuid,))
            gre = cur.fetchone()
            cur.execute("SELECT * FROM recs WHERE uid = (%s)", (reviewuid,))
            recs = cur.fetchall()

            return render_template('application.html', app=app, form='review', user=user, degs=degs, recs=recs, gre=gre)

        #GS and CAC decision form
        if decideuid:
          if fac['is_CAC'] == 'T' and decideuid:
            cur.execute("SELECT * FROM reviews WHERE uid = (%s)", (decideuid,))
            reviews = cur.fetchall()
            cur.execute("SELECT * FROM applications WHERE uid = (%s)", (decideuid,))
            app = cur.fetchone()
            cur.execute("SELECT * FROM users WHERE uid = (%s)", (decideuid,))
            user = cur.fetchone()
            cur.execute("SELECT * FROM recs WHERE uid = (%s)", (decideuid,))
            recs = cur.fetchall()
            cur.execute("SELECT rating FROM reviews WHERE uid = (%s)", (decideuid,))
            avgs = cur.fetchall()
            review_avg = 0
            for a in avgs:
              review_avg += int(a['rating'])
            review_avg = review_avg/len(avgs)

            return render_template("decide_cac.html", reviews=reviews, app=app, user=user, review_avg=review_avg, recs=recs)
      
      elif session['type'] == 'GS':
          decideuid = request.form.get('decideapp')
          cur.execute("SELECT * FROM reviews WHERE uid = (%s)", (decideuid,))
          reviews = cur.fetchall()
          cur.execute("SELECT * FROM applications WHERE uid = (%s)", (decideuid,))
          app = cur.fetchone()
          cur.execute("SELECT * FROM users WHERE uid = (%s)", (decideuid,))
          user = cur.fetchone()
          cur.execute("SELECT * FROM recs WHERE uid = (%s)", (decideuid,))
          recs = cur.fetchall()
          cur.execute("SELECT rating FROM reviews WHERE uid = (%s)", (decideuid,))
          avgs = cur.fetchall()
          review_avg = 0
          for a in avgs:
            review_avg += int(a['rating'])
          review_avg = review_avg/len(avgs)

          return render_template("decide_cac.html", reviews=reviews, app=app, user=user, review_avg=review_avg, recs=recs)
         

    #Applicant
    if session['type'] == 'Applicant':
      create = request.form.get('createapp') 
      view = request.form.get('viewapp') 
      send = request.form.get('sendrec')
      trans = request.form.get('sendt')
      accept = request.form.get('accept')
      reject = request.form.get('reject')

      #create application
      if create:
        cur.execute("SELECT * FROM users WHERE uid = (%s)", (session['uid'],))
        data = cur.fetchone()
        return render_template('application.html', form=create, data=data, year=datetime.now().year)

      #accept admission
      elif accept:
        cur.execute("SELECT status FROM applications WHERE uid = (%s)", (session['uid'],))
        aid = cur.fetchone()
        return render_template('application.html', aid=aid, form=accept)

      #reject admission
      elif reject:
        cur.execute("DELETE FROM applications WHERE uid = (%s)", (session['uid'],))
        cur.execute("DELETE FROM degrees WHERE uid = (%s)", (session['uid'],))
        cur.execute("DELETE FROM gres WHERE uid = (%s)", (session['uid'],))
        cur.execute("DELETE FROM recs WHERE uid = (%s)", (session['uid'],))
        cur.execute("DELETE FROM reviews WHERE uid = (%s)", (session['uid'],))
        cur.execute("DELETE FROM users WHERE uid = (%s)", (session['uid'],))
        mydb.commit()
        return redirect('/logout')
      
      #view application
      elif view:
        cur.execute("SELECT * FROM applications WHERE uid = (%s)", (session['uid'],))
        app = cur.fetchone()
        cur.execute("SELECT * FROM degrees WHERE uid = (%s)", (session['uid'],))
        degrees = cur.fetchall()
        cur.execute("SELECT * FROM gres WHERE uid = (%s)", (session['uid'],))
        gre = cur.fetchone()
        cur.execute("SELECT writer, message FROM recs WHERE uid = (%s)", (session['uid'],))
        recs = cur.fetchall()

        return render_template('application.html', form=view, app=app, degrees=degrees, gre=gre, recs=recs)
      
      #Sent email
      elif send:
        cur.execute("SELECT writer, email FROM recs WHERE email = (%s)", (send,))
        rec = cur.fetchone()
        return render_template('application.html', form='rec', rec=rec)
      
      elif trans:
        return redirect('/transcriptapps')

  return render_template('application.html')

@app.route('/accept_app/<id>', methods=['GET', 'POST'])
def accept_app(id):
  mydb = mydbfunc()
  cur = mydb.cursor(dictionary=True)
  if "user_type" not in session:
    return redirect('/')
  if session['type'] not in ['Admin', 'GS', 'Applicant']:
    return redirect('/')
  if session['type'] == 'Applicant':
    if int(session['uid'] != int(id)):
      return redirect('/')

  if request.method == 'POST':
    accept = request.form.get('accept') #admitted
    accept_aid = request.form.get('accept_aid') #admitaid
    if (accept or accept_aid) and session['type'] == 'Applicant':
      cur.execute("UPDATE applications SET status = 'acceptdeposit' WHERE uid = (%s)", (session['uid'],))
      mydb.commit()
      return redirect('/')
    
  if request.method == 'GET':
    if session['type'] == 'GS' or session['type'] == 'Admin':
      cur.execute("UPDATE users SET user_type = 'Student' WHERE uid = (%s)", (id,))
      cur.execute("UPDATE applications SET status = 'Student' WHERE uid = (%s)", (id,))
      cur.execute("SELECT degree FROM applications WHERE uid = (%s)", (id,))
      deg = cur.fetchone()['degree']
      cur.execute("SELECT advisor_id FROM reviews WHERE uid = (%s)", (id,))
      advisor_id = cur.fetchall()
      advisor_id = advisor_id[0]['advisor_id']
      if deg == 'MS':
        deg = 'Masters'
      if deg == 'PhD':
        deg = 'PHD'
      cur.execute("INSERT INTO students VALUES (%s, %s, %s, %s)", (id, deg, advisor_id, 'F'))
      mydb.commit()
    mydb.commit()
    return redirect('/Portal')
  
  return redirect('/Portal')


@app.route('/review_application', methods=['POST'])
def review_application():
  mydb = mydbfunc()
  cur = mydb.cursor(dictionary=True)
  if "user_type" not in session:
    return redirect('/')
  if session['type'] not in ['Admin','Faculty']:
    return redirect('/')
  if session['type'] == 'Faculty':
    cur.execute("SELECT is_CAC, can_review FROM faculty WHERE uid = (%s)", (session['uid'],))
    d=cur.fetchone()
    iscac = d['is_CAC']
    canrev = d['can_review']
    if iscac == 'F' and canrev == 'F':
      return redirect('/')

  uid = request.form.get("user_id")
  rating = request.form.get("review_rating")
  deficiency = request.form.get("review_deficiency")
  reason = request.form.get("review_reason")
  advisor_id = request.form.get("review_advisor")
  comments = request.form.get("review_comments")
    
  #Check valid advisor
  cur.execute("SELECT users.uid, email FROM users JOIN faculty ON users.uid = faculty.uid WHERE faculty.can_advise = (%s)", ('T',))
  fac = cur.fetchall()
  for f in fac:
    if f['email'] == advisor_id:
      advisor_id = f['uid']
  if type(advisor_id) != int:
    return render_template("application.html", error='incorrect advisor email')
  
  #Update recs table
  cur.execute("SELECT * FROM recs WHERE uid = (%s)", (uid,))
  user = cur.fetchall()
  for us in user:
    ratingw = request.form.get("rat" + str(us['writer']))
    generic = request.form.get("gen" + str(us['writer']))
    credible = request.form.get("cred" + str(us['writer']))
    cur.execute("UPDATE recs SET rating = %s, generic = %s, credible = %s WHERE uid = (%s) AND email = (%s)", (ratingw, generic, credible, us['uid'], us['email']))
    mydb.commit() 
  mydb.commit()   

  #Create Review
  cur.execute("INSERT INTO reviews (uid, rating, deficiency, reason, advisor_id, comments, reviewer_id) VALUES ((%s),(%s),(%s),(%s),(%s),(%s),(%s))", (uid, rating, deficiency, reason, advisor_id, comments, session['uid']))

  mydb.commit()

  return redirect('/Portal')

@app.route('/decide_application', methods=['POST'])
def decide_final():
  mydb = mydbfunc()
  cur = mydb.cursor(dictionary=True)
  if "user_type" not in session:
    return redirect('/')
  if session['type'] not in ['Admin', 'GS', 'Faculty']:
    return redirect('/')
  if session['type'] == 'Faculty':
    cur.execute("SELECT is_CAC FROM faculty WHERE uid = (%s)", (session['uid'],))
    iscac = cur.fetchone()['is_CAC']
    if iscac == 'F':
      return redirect('/')
  
  status = request.form.get("decide_final")
  appid = request.form.get("user_id")
  cur.execute("UPDATE applications SET status = (%s) WHERE uid = (%s)", (status, appid))
  mydb.commit()
  cur.execute("UPDATE applications SET received = (%s) WHERE uid = (%s)", (status, datetime.now().strftime('%Y-%m-%d')))
  mydb.commit()

  return redirect("/Portal")


@app.route('/thankyou', methods=['GET', 'POST'])
def thankyou():
  mydb = mydbfunc()
  cur = mydb.cursor(dictionary=True)
  if "user_type" not in session:
    return redirect('/')
  if session['type'] != 'Applicant':
    return redirect('/')
  if request.method == 'POST':
    #gre 
    gre = None
    total = request.form.get('total')
    score = request.form.get('score')
    toefl = request.form.get('toefl')
    if total: 
      verbal = int(request.form['verbal'])
      quant = int(request.form['quant'])
      total = int(request.form['total'])
      year = int(request.form['yearexam'])
      cur.execute("SELECT * FROM gres WHERE uid = (%s)", (session['uid'],))
      gre = cur.fetchone()
      if gre:
        cur.execute("UPDATE gres SET total = %s, verbal =%s, quant = %s, year = %s WHERE uid = (%s)", (total, verbal, quant, year, session['uid']))
        mydb.commit()
      else:
        cur.execute("INSERT INTO gres (uid, total, verbal, quant, year) VALUES (%s,%s,%s,%s,%s)", (session['uid'], total, verbal, quant, year))
        mydb.commit()
    if score:
      score = int(request.form['score'])
      subject = request.form['subject']
      cur.execute("SELECT * FROM gres WHERE uid = (%s)", (session['uid'],))
      gre = cur.fetchone()
      if gre:
        cur.execute("UPDATE gres SET score=(%s), subject=(%s) WHERE uid = (%s)", (score, subject, session['uid'])) 
        mydb.commit()
      else:
        cur.execute("INSERT INTO gres (uid, score, subject) VALUES (%s,%s,%s)", (session['uid'], score, subject,))
        mydb.commit()
    if toefl: 
      toefl = int(request.form['toefl'])
      date = int(request.form['dateexam'])
      cur.execute("SELECT * FROM gres WHERE uid = (%s)", (session['uid'],))
      gre = cur.fetchone()
      if gre:
        cur.execute("UPDATE gres SET toefl=(%s), date=(%s) WHERE uid = (%s)", (toefl, date, session['uid'])) 
        mydb.commit()
      else:
        cur.execute("INSERT INTO gres (uid, toefl, date) VALUES (%s,%s,%s)", (session['uid'], score, date,))
        mydb.commit()

    #past degrees
    d_type = request.form.get('ms')
    if d_type:
      gpa = float(request.form['gpa'])
      major = request.form['major']
      college = request.form['university']
      year = int(request.form['pdyear'])
      cur.execute("INSERT INTO degrees (uid, type, gpa, major, college, year) VALUES (%s,%s,%s,%s,%s,%s)", (session['uid'], d_type, gpa, major, college, year))
      mydb.commit()
    d_type = request.form['bsba']
    gpa = float(request.form['gpa2'])
    major = request.form['major2']
    college = request.form['university2']
    year = int(request.form['pdyear2'])
    cur.execute("INSERT INTO degrees (uid, type, gpa, major, college, year) VALUES (%s,%s,%s,%s,%s,%s)", (session['uid'], d_type, gpa, major, college, year))
    mydb.commit()

    #letters
    writer = request.form['writer']
    email = request.form['email']
    title = request.form['title']
    affiliation = request.form['affiliation']
    cur.execute("INSERT INTO recs (uid, writer, email, title, affiliation) VALUES (%s,%s,%s,%s,%s)", (session['uid'], writer, email, title, affiliation))
    mydb.commit()

    writer2 = request.form.get('writer2')
    email2 = request.form.get('email2')
    title2 = request.form.get('title2')
    affiliation2 = request.form.get('affiliation2')

    if writer2:
      cur.execute("INSERT INTO recs (uid, writer, email, title, affiliation) VALUES (%s,%s,%s,%s,%s)", (session['uid'], writer2, email2, title2, affiliation2))
      mydb.commit()

    writer3 = request.form.get('writer3')
    email3 = request.form.get('email3')
    title3 = request.form.get('title3')
    affiliation3 = request.form.get('affiliation3')

    if writer3:
      cur.execute("INSERT INTO recs (uid, writer, email, title, affiliation) VALUES (%s,%s,%s,%s,%s)", (session['uid'], writer3, email3, title3, affiliation3))
      mydb.commit()

    #app
    status = 'incomplete'
    transcript = 'F'
    degree = request.form.get('degree')
    semester = request.form.get('semester')
    year = int(request.form.get('year'))
    experience = request.form['exp']
    aoi = request.form['aoi']
    cur.execute("INSERT INTO applications (uid, status, transcript, degree, semester, year, experience, aoi, received) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", (session['uid'], status, transcript, degree, semester, year, experience, aoi, datetime.now().strftime('%Y-%m-%d')))
    mydb.commit()
    return render_template('thankyou.html')
  
  return redirect('/')

@app.route('/transcriptapps', methods=['GET', 'POST'])
def transcriptapps():
  mydb = mydbfunc()
  cur = mydb.cursor(dictionary=True)
  if "user_type" not in session:
    return redirect('/')
  if session['type'] != 'Applicant':
    return redirect('/')
  if request.method == 'POST':
    mail = request.form.get('mail')
    online = request.form.get('online')
    if mail:
      cur.execute("UPDATE applications SET transcript = (%s) WHERE uid = (%s)", ('M', session['uid']))
      mydb.commit()
      return redirect('/Portal')
    if online:
      cur.execute("UPDATE applications SET transcript = (%s) WHERE uid = (%s)", ('M', session['uid']))
      mydb.commit()
      return redirect('/Portal')
  return render_template('transcriptapps.html')

#Recommender write to applicant
@app.route('/letterwriter', methods=['GET', 'POST'])
def letterwriter():
  mydb = mydbfunc()
  cur = mydb.cursor(dictionary=True)
  if "user_type" not in session:
    return redirect('/')
  if session['type'] != 'Applicant':
    return redirect('/')

  if request.method == 'POST':
    send = 'sent'

    email = request.form.get("lettermail")
    message = request.form.get("lettermessage")
    cur.execute("UPDATE recs SET sent = %s WHERE uid = %s AND email = %s", (message, session["uid"], email))
    mydb.commit() 
    return render_template('application.html', form=send, msg=message, email=email)


  return redirect('/homeapps')

#Write to recommender
@app.route('/writeletter', methods=['GET', 'POST'])
def writeletter():
  mydb = mydbfunc()
  cur = mydb.cursor(dictionary=True)
  if "user_type" not in session:
    return redirect('/')
  if session['type'] != 'Recommender':
    return redirect('/')
  
  if request.method == 'POST':
    #add into database
    cur.execute("SELECT * FROM recs WHERE email = (%s)", (session['email'],))
    user = cur.fetchall()
    for us in user:
      if not us['message']:
        message = request.form.get(str(us['uid']))
        cur.execute("UPDATE recs SET message = (%s) WHERE uid = (%s) AND email = (%s)", (message, us['uid'], session['email']))
        mydb.commit() 
    mydb.commit()     
    cur.execute("SELECT users.fname, users.minit, users.lname, recs.message, recs.sent, users.uid FROM users LEFT JOIN recs ON users.uid = recs.uid WHERE recs.email = (%s)", (session['email'],))
    data = cur.fetchall()
    return render_template('writeletter.html', data=data)
  
  cur.execute("SELECT users.fname, users.minit, users.lname, recs.message, recs.sent, users.uid FROM users LEFT JOIN recs ON users.uid = recs.uid WHERE recs.email = (%s)", (session['email'],))
  data = cur.fetchall()

  return render_template('writeletter.html', data=data)
  
@app.route('/edit_apps/<id>', methods=['GET', 'POST'])
def edit_apps(id):
  mydb = mydbfunc()
  cur = mydb.cursor(dictionary=True)
  if "user_type" not in session:
    return redirect('/')
  if session['type'] not in ['Admin', 'GS']:
    return redirect('/')
  
  if request.method == 'POST':
    deg1 = request.form.get('deg1')
    gpa1 = request.form.get('gpa1')
    major1 = request.form.get('major1')
    uni1 = request.form.get('uni1')
    year1 = request.form.get('year1')
    deg2 = request.form.get('deg2')
    gpa2 = request.form.get('gpa2')
    major2 = request.form.get('major2')
    uni2 = request.form.get('uni2')
    year2 = request.form.get('year2')
    total = request.form.get('total')
    quant = request.form.get('quant')
    verbal = request.form.get('verbal')
    yearexam = request.form.get('yearg')
    score = request.form.get('score')
    subject = request.form.get('subject')
    toefl = request.form.get('toefl')
    dateexam = request.form.get('yeart')

    cur.execute("SELECT * FROM degrees WHERE uid = (%s)", (id,))
    numdegs = cur.fetchall()

    cur.execute("UPDATE degrees SET type = (%s) WHERE uid = (%s) AND type = (%s)", (deg1, id, deg1))
    mydb.commit()
    cur.execute("UPDATE degrees SET gpa = (%s) WHERE uid = (%s) AND type = (%s)", (gpa1, id, deg1))
    mydb.commit()
    cur.execute("UPDATE degrees SET major = (%s) WHERE uid = (%s) AND type = (%s)", (major1, id, deg1))
    mydb.commit()
    cur.execute("UPDATE degrees SET college = (%s) WHERE uid= (%s) AND type = (%s)", (uni1, id, deg1))
    mydb.commit()
    cur.execute("UPDATE degrees SET year = (%s) WHERE uid = (%s) AND type = (%s)", (year1, id, deg1))
    mydb.commit()
    if len(numdegs) == 2:
      cur.execute("UPDATE degrees SET type = (%s) WHERE uid = (%s) AND type = (%s)", (deg2, id, deg2))
      mydb.commit()
      cur.execute("UPDATE degrees SET gpa = (%s) WHERE uid = (%s) AND type = (%s)", (gpa2, id, deg2))
      mydb.commit()
      cur.execute("UPDATE degrees SET major = (%s) WHERE uid = (%s) AND type = (%s)", (major2, id, deg2))
      mydb.commit()
      cur.execute("UPDATE degrees SET college = (%s) WHERE uid= (%s) AND type = (%s)", (uni2, id, deg2))
      mydb.commit()
      cur.execute("UPDATE degrees SET year = (%s) WHERE uid = (%s) AND type = (%s)", (year2, id, deg2))
      mydb.commit()

    if total:
      cur.execute("UPDATE gres SET total = (%s) WHERE uid = (%s)", (total, id,))
      mydb.commit()
      cur.execute("UPDATE gres SET quant = (%s) WHERE uid = (%s)", (quant, id,))
      mydb.commit()
      cur.execute("UPDATE gres SET verbal = (%s) WHERE uid = (%s)", (verbal, id,))
      mydb.commit()
      cur.execute("UPDATE gres SET year = (%s) WHERE uid = (%s)", (yearexam, id,))
      mydb.commit()
    if score:
      cur.execute("UPDATE gres SET score = (%s) WHERE uid = (%s)", (score, id,))
      mydb.commit()
      cur.execute("UPDATE gres SET subject = (%s) WHERE uid = (%s)", (subject, id,))
      mydb.commit()
    if toefl:
      cur.execute("UPDATE gres SET toefl = (%s) WHERE uid = (%s)", (toefl, id,))
      mydb.commit()
      cur.execute("UPDATE gres SET date = (%s) WHERE uid = (%s)", (dateexam, id,))
      mydb.commit()

    return redirect('/Portal')
  
  return redirect('/Portal')

app.run(host='0.0.0.0', port=3306)