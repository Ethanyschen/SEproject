#!/usr/bin/env python3
# coding=utf-8
# -*- coding: UTF-8 -*-
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import MySQLdb

app = FastAPI()

@app.get('/', response_class=HTMLResponse)
def index():
    form = """
    <html>
    <head>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
            text-align: center;
        }

        form {
            margin: 20px auto;
            width: 300px;
            padding: 20px;
            background-color: #fff;
            border-radius: 8px;
        }

        input[type="text"], input[type="submit"] {
            width: 100%;
            padding: 10px;
            margin: 5px 0;
            border-radius: 4px;
            border: 1px solid #ddd;
        }

        input[type="submit"] {
            background-color: #5cb85c;
            color: white;
            border: none;
            cursor: pointer;
        }

        input[type="submit"]:hover {
            background-color: #4cae4c;
        }

        table {
            margin: 20px auto;
            border-collapse: collapse;
            width: 80%;
        }

        th, td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }

        th {
            background-color: #4CAF50;
            color: white;
        }

        tr:hover {background-color: #f5f5f5;}
    </style>
    </head>
    <body>
    <form method="post" action="/selected" >
        <h3>查詢已選課列表</h3>
        <input type="text" name="my_head" placeholder="輸入學號">
        <input type="submit" value="查詢">
    </form>

    <form method="post" action="/select" >
        <h3>查詢可選課列表</h3>
        <input type="text" name="my_head" placeholder="輸入學號">
        <input type="submit" value="查詢">
    </form>

    <form method="post" action="/course_detail" >
        <h3>查詢課程詳細內容</h3>
        <input type="text" name="section_id" placeholder="輸入課程代碼">
        <input type="submit" value="查詢">
    </form>
    
    <form method="post" action="/course_statistics_UI" >
        <h3>課程資料統計</h3>
        <input type="submit" value="查詢">
    </form>
    
    </body>
    </html>
    """
    return form

@app.post('/selected', response_class=HTMLResponse)
def action(my_head: str = Form(default='')):
    # 建立資料庫連線
    conn = MySQLdb.connect(host="127.0.0.1",
                           user="hj",
                           passwd="test1234",
                           db="coursesystem")

    check = 1

    query = "select Student_id from student"
    cursor = conn.cursor()
    cursor.execute(query)

    rec = cursor.fetchall()
    for record in rec:
        id = record[0]
        if id == my_head:
            check = 0

    # 欲查詢的 query 指令
    query = "SELECT * FROM section where Section_id in(select Section_id from selectdetail where Student_id = '{}');".format(my_head)

    # 執行查詢
    cursor.execute(query)

    results = """
    <html>
    <head>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
            text-align: center;
        }

        form {
            margin: 20px auto;
            width: 300px;
            padding: 20px;
            background-color: #fff;
            border-radius: 8px;
        }

        input[type="text"], input[type="submit"] {
            width: 100%;
            padding: 10px;
            margin: 5px 0;
            border-radius: 4px;
            border: 1px solid #ddd;
        }

        input[type="submit"] {
            background-color: #5cb85c;
            color: white;
            border: none;
            cursor: pointer;
        }

        input[type="submit"]:hover {
            background-color: #4cae4c;
        }

        table {
            margin: 20px auto;
            border-collapse: collapse;
            width: 80%;
        }

        th, td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }

        th {
            background-color: #4CAF50;
            color: white;
        }

        tr:hover {background-color: #f5f5f5;}
    </style>
    </head>
    <body>
    <p><a href="/">Back to Query Interface</a></p>
    <div>
    """
    if check == 0:
        records = cursor.fetchall()
        # 計算已選總學分
        update = "update student set Total_credits = (select sum(credits) from course where Course_id in (select Course_id from section where Section_id in (select Section_id from selectdetail where Student_id = '{}')))where Student_id = '{}';".format(my_head, my_head)
        cursor.execute(update)
        conn.commit()

        results += "<table><tr><th>Column 1</th><th>Column 2</th><th>Column 3</th><th>Column 4</th><th>Column 5</th><th>Column 6</th><th>Column 7</th><th>Column 8</th></tr>"
        for result in records:
            results += "<tr>"
            for col in result:
                results += "<td>{}</td>".format(col)
            results += "</tr>"
        results += "</table>"

        results += """
        <form method="post" action="/quit" >
            <input type="text" name="secid" placeholder="輸入課程代碼">
            <input type="hidden" name="stuid" value="{}">
            <input type="submit" value="退選">
        </form>
        """.format(my_head)
    else:
        results += "<p>不存在此學號</p>"

    results += """
    </div>
    </body>
    </html>
    """
    return results
@app.post('/select', response_class=HTMLResponse)
def action(my_head: str = Form(default='')):
    conn = MySQLdb.connect(host="127.0.0.1",
                           user="hj",
                           passwd="test1234",
                           db="coursesystem")

    check = 1
    update = "update section set Cur_studentnum = (select count(Student_id) from selectdetail where selectdetail.Section_id = section.Section_id) order by Section_id;"
    cursor = conn.cursor()
    cursor.execute(update)
    conn.commit()

    query = "select Student_id from student"
    cursor.execute(query)
    rec = cursor.fetchall()
    for record in rec:
        id = record[0]
        if id == my_head:
            check = 0

    query = "select section.Section_id ,section.Section_name ,instructor.Department_name ,section.Year ,section.Semester ,course.Type ,section.Max_quota ,section.Cur_studentnum ,time.Day from section inner join instructor on section.Instructor_id = instructor.Instructor_id inner join time on section.Section_id = time.Section_id inner join course on section.Course_id = course.Course_id;"
    cursor.execute(query)

    results = """
    <html>
    <head>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
            text-align: center;
        }

        form {
            margin: 20px auto;
            width: 300px;
            padding: 20px;
            background-color: #fff;
            border-radius: 8px;
        }

        input[type="text"], input[type="submit"] {
            width: 100%;
            padding: 10px;
            margin: 5px 0;
            border-radius: 4px;
            border: 1px solid #ddd;
        }

        input[type="submit"] {
            background-color: #5cb85c;
            color: white;
            border: none;
            cursor: pointer;
        }

        input[type="submit"]:hover {
            background-color: #4cae4c;
        }

        table {
            margin: 20px auto;
            border-collapse: collapse;
            width: 80%;
        }

        th, td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }

        th {
            background-color: #4CAF50;
            color: white;
        }

        tr:hover {background-color: #f5f5f5;}
    </style>
    </head>
    <body>
    <p><a href="/">Back to Query Interface</a></p>
    <div>
    """
    if check == 0:
        records = cursor.fetchall()
        results += "<table><tr><th>Section ID</th><th>Section Name</th><th>Department</th><th>Year</th><th>Semester</th><th>Type</th><th>Max Quota</th><th>Current Students</th><th>Day</th></tr>"
        for result in records:
            results += "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(*result)
        results += "</table>"

        results += """
        <form method="post" action="/add" >
            <input type="text" name="secid" placeholder="輸入課程代碼">
            <input type="hidden" name="stuid" value="{}">
            <input type="submit" value="加選">
        </form>
        """.format(my_head)
    else:
        results += "<p>不存在此學號</p>"

    results += """
    </div>
    </body>
    </html>
    """
    return results

# 退選條件檢查
@app.post('/quit', response_class=HTMLResponse)
def action(secid: str = Form(default=''), stuid: str = Form(default='')):
    conn = MySQLdb.connect(host="127.0.0.1",
                           user="hj",
                           passwd="test1234",
                           db="coursesystem")

    # select Type from course where Course_id = (select Course_id from section where Section_id = "1261")
    query = "select Credits , Type from course where Course_id = (select Course_id from section where Section_id = '{}')".format(
        secid)
    cursor = conn.cursor()
    cursor.execute(query)
    output = cursor.fetchall()

    for outcome in output:
        credits = int(outcome[0])
        type = outcome[1]

    query = "select Total_credits from student where Student_id = '{}'".format(stuid)
    cursor.execute(query)
    total = cursor.fetchall()
    for totalcre in total:
        totalcredit = int(totalcre[0])

    results = """
    <p><a href="/">Back to Query Interface</a></p>
    """

    if type == "Elective" and (totalcredit - credits) >= 9:
        delete = "delete from selectdetail where Student_id = '{}' and Section_id = '{}'".format(stuid, secid)
        cursor.execute(delete)
        conn.commit()
        update = "update student set Total_credits = (select sum(credits) from course where Course_id in (select Course_id from section where Section_id in (select Section_id from selectdetail where Student_id = '{}')))where Student_id = '{}';".format(
            stuid, stuid)
        cursor.execute(update)
        conn.commit()
        results += "{}".format("quit succesfully")
    else:
        if type == "Required":
            results += "無法退選必修課"
        elif (totalcredit - credits) <= 9:
            results += "無法退選，退選後學分小於9學分"

    return results


@app.post('/add', response_class=HTMLResponse)
def action(secid: str = Form(default=''), stuid: str = Form(default='')):
    conn = MySQLdb.connect(host="127.0.0.1",
                           user="hj",
                           passwd="test1234",
                           db="coursesystem")

    check = 0
    typecheck = 0

    query = "select Course_id from section where Section_id = '{}';".format(secid)
    cursor = conn.cursor()
    cursor.execute(query)

    rec = cursor.fetchall()
    for record in rec:
        selectcourseid = record[0]

    query = "select Cur_studentnum from section where Section_id = '{}';".format(secid)
    cursor.execute(query)

    rec = cursor.fetchall()
    for record in rec:
        curstudentnum = int(record[0])

    query = "select Max_quota from section where Section_id = '{}';".format(secid)
    cursor.execute(query)

    rec = cursor.fetchall()
    for record in rec:
        maxquota = int(record[0])

    query = "select Total_credits from student where Student_id = '{}';".format(stuid)
    cursor.execute(query)

    rec = cursor.fetchall()
    for record in rec:
        totalcredits = int(record[0])

    query = "select Credits from course where Course_id = (select Course_id from section where Section_id = '{}');".format(
        secid)
    cursor.execute(query)

    rec = cursor.fetchall()
    for record in rec:
        credits = int(record[0])

    query = "select Time_type from time where Section_id = '{}';".format(secid)
    cursor.execute(query)

    rec = cursor.fetchall()
    for record in rec:
        selecttype = int(record[0])

    query = "select Course_id from section where Section_id in (select Section_id from selectdetail where Student_id = '{}');".format(stuid)
    cursor.execute(query)

    rec = cursor.fetchall()
    for record in rec:
        courseid = record[0]
        if courseid == selectcourseid:
            check = 1

    query = "select Time_type from time where Section_id in (select Section_id from selectdetail where Student_id = '{}');".format(stuid)
    cursor.execute(query)

    rec = cursor.fetchall()
    for record in rec:
        type = record[0]
        if selecttype == type:
            typecheck = 1

    # 加選條件檢查
    # select Time_type from time where Section_id = "1260";
    results = """
    <p><a href="/">Back to Query Interface</a></p>
    """
    if curstudentnum < maxquota and (totalcredits + credits) <= 30:
        if check == 0 and typecheck == 0:
            add = "insert into selectdetail(Student_id ,Section_id) value ('{}' ,'{}');".format(stuid, secid)
            cursor.execute(add)
            conn.commit()
            update = "update student set Total_credits = (select sum(credits) from course where Course_id in (select Course_id from section where Section_id in (select Section_id from selectdetail where Student_id = '{}')))where Student_id = '{}';".format(
                stuid, stuid)
            cursor.execute(update)
            conn.commit()
            results += "add succesfully"
        else:
            if curstudentnum >= maxquota:
                results += "人數已滿"
            elif check == 1:
                results += "已有同名課程"
            elif (totalcredits + credits) >= 30:
                results += "學分超過30"
            elif typecheck == 1:
                results += "該時段有衝堂"
    else:
        if curstudentnum >= maxquota:
            results += "人數已滿"
        elif check == 1:
            results += "已有同名課程"
        elif (totalcredits + credits) >= 30:
            results += "學分超過30"
        elif typecheck == 1:
            results += "該時段有衝堂"

    return results


@app.post('/course_detail', response_class=HTMLResponse)
def course_detail(section_id: str = Form(default='')):
    conn = MySQLdb.connect(host="127.0.0.1",
                           user="hj",
                           passwd="test1234",
                           db="coursesystem")

    query = """
        SELECT section.Section_id, section.Section_name, instructor.Instructor_name, instructor.Department_name, section.Year,
               section.Semester, course.Type, course.Credits, time.Day, section.Cur_studentnum, section.Max_quota
        FROM section
        INNER JOIN instructor ON section.Instructor_id = instructor.Instructor_id
        INNER JOIN time ON section.Section_id = time.Section_id
        INNER JOIN course ON section.Course_id = course.Course_id
        WHERE section.Section_id = '{}';
    """.format(section_id)

    cursor = conn.cursor()
    cursor.execute(query)
    results = """
    <html>
    <head>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
            text-align: center;
        }

        form {
            margin: 20px auto;
            width: 300px;
            padding: 20px;
            background-color: #fff;
            border-radius: 8px;
        }

        input[type="text"], input[type="submit"] {
            width: 100%;
            padding: 10px;
            margin: 5px 0;
            border-radius: 4px;
            border: 1px solid #ddd;
        }

        input[type="submit"] {
            background-color: #5cb85c;
            color: white;
            border: none;
            cursor: pointer;
        }

        input[type="submit"]:hover {
            background-color: #4cae4c;
        }

        table {
            margin: 20px auto;
            border-collapse: collapse;
            width: 80%;
        }

        th, td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }

        th {
            background-color: #4CAF50;
            color: white;
        }

        tr:hover {background-color: #f5f5f5;}
    </style>
    </head>
    <body>
    <p><a href="/">Back to Query Interface</a></p>
    <div>
    """

    record = cursor.fetchall()
    if record:
        results += "<h2>課程詳細內容：</h2>"
        results += "<table><tr><th>Section ID</th><th>Section Name</th><th>Instructor</th><th>Department</th><th>Year</th><th>Semester</th><th>Type</th><th>Day</th><th>Credits</th><th>Current Students</th><th>Max Quota</th></tr>"
        for result in record:
            results += "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(*result)
        results += "</table>"
    else:
        results += "<p>找不到該課程的詳細內容。</p>"

    results += """
    </div>
    </body>
    </html>
    """
    return results


@app.post('/course_statistics_UI', response_class=HTMLResponse)
def course_statistics_UI():
    form = """
    <html>
    <head>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
            text-align: center;
        }

        form {
            margin: 20px auto;
            width: 300px;
            padding: 20px;
            background-color: #fff;
            border-radius: 8px;
        }

        input[type="text"], input[type="submit"] {
            width: 100%;
            padding: 10px;
            margin: 5px 0;
            border-radius: 4px;
            border: 1px solid #ddd;
        }

        input[type="submit"] {
            background-color: #5cb85c;
            color: white;
            border: none;
            cursor: pointer;
        }

        input[type="submit"]:hover {
            background-color: #4cae4c;
        }

        table {
            margin: 20px auto;
            border-collapse: collapse;
            width: 80%;
        }

        th, td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }

        th {
            background-color: #4CAF50;
            color: white;
        }

        tr:hover {background-color: #f5f5f5;}
    </style>
    </head>
    <body>
    
    <form method="post" action="/course_statistics" >
        <h3>已滿額課程</h3>
        <input type="submit" value="查詢">
    </form>

    <form method="post" action="/popular_courses" >
        <h3>課程受歡迎程度排名</h3>
        <input type="submit" value="查詢">
    </form>

    </body>
    </html>
    """
    return form

@app.post('/course_statistics', response_class=HTMLResponse)
def course_statistics():
    conn = MySQLdb.connect(host="127.0.0.1",
                           user="hj",
                           passwd="test1234",
                           db="coursesystem")

    query = """
         SELECT section.Section_id, section.Section_name, instructor.Instructor_name, instructor.Department_name, section.Year,
                section.Semester, course.Type, course.Credits, time.Day, section.Cur_studentnum, section.Max_quota
         FROM section
         INNER JOIN instructor ON section.Instructor_id = instructor.Instructor_id
         INNER JOIN time ON section.Section_id = time.Section_id
         INNER JOIN course ON section.Course_id = course.Course_id
         WHERE section.Cur_studentnum = section.Max_quota;
     """

    cursor = conn.cursor()
    cursor.execute(query)
    records = cursor.fetchall()

    results = """
     <html>
     <head>
         <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
            text-align: center;
        }

        form {
            margin: 20px auto;
            width: 300px;
            padding: 20px;
            background-color: #fff;
            border-radius: 8px;
        }

        input[type="text"], input[type="submit"] {
            width: 100%;
            padding: 10px;
            margin: 5px 0;
            border-radius: 4px;
            border: 1px solid #ddd;
        }

        input[type="submit"] {
            background-color: #5cb85c;
            color: white;
            border: none;
            cursor: pointer;
        }

        input[type="submit"]:hover {
            background-color: #4cae4c;
        }

        table {
            margin: 20px auto;
            border-collapse: collapse;
            width: 80%;
        }

        th, td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }

        th {
            background-color: #4CAF50;
            color: white;
        }

        tr:hover {background-color: #f5f5f5;}
     </style>
     </head>
     <body>
     <p><a href="/">Back to Query Interface</a></p>
     <div>
     """

    if records:
        results += "<h2>報名已滿的課程：</h2>"
        results += "<table><tr><th>Section ID</th><th>Section Name</th><th>Instructor</th><th>Department</th><th>Year</th><th>Semester</th><th>Type</th><th>Day</th><th>Credits</th><th>Current Students</th><th>Max Quota</th></tr>"
        for record in records:
            results += "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                *record)
        results += "</table>"
    else:
        results += "<p>沒有報名已滿的課程。</p>"

    results += """
     </div>
     </body>
     </html>
     """
    return results

@app.post('/popular_courses', response_class=HTMLResponse)
def popular_courses():
    conn = MySQLdb.connect(host="127.0.0.1",
                           user="hj",
                           passwd="test1234",
                           db="coursesystem")

    # 新的 SQL 查詢
    query = """
        SELECT section.Section_id, section.Section_name, instructor.Instructor_name, section.Cur_studentnum
        FROM section
        INNER JOIN instructor ON section.Instructor_id = instructor.Instructor_id
        ORDER BY section.Cur_studentnum DESC;
    """

    cursor = conn.cursor()
    cursor.execute(query)
    records = cursor.fetchall()

    # 組裝 HTML 響應
    results = """
    <html>
    <head>
<style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
            text-align: center;
        }

        form {
            margin: 20px auto;
            width: 300px;
            padding: 20px;
            background-color: #fff;
            border-radius: 8px;
        }

        input[type="text"], input[type="submit"] {
            width: 100%;
            padding: 10px;
            margin: 5px 0;
            border-radius: 4px;
            border: 1px solid #ddd;
        }

        input[type="submit"] {
            background-color: #5cb85c;
            color: white;
            border: none;
            cursor: pointer;
        }

        input[type="submit"]:hover {
            background-color: #4cae4c;
        }

        table {
            margin: 20px auto;
            border-collapse: collapse;
            width: 80%;
        }

        th, td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }

        th {
            background-color: #4CAF50;
            color: white;
        }

        tr:hover {background-color: #f5f5f5;}
     </style>
    </head>
    <body>
    <p><a href="/">Back to Query Interface</a></p>
    <div>
    <h2>受歡迎的課程排名：</h2>
    <table>
    <tr>
        <th>Section ID</th>
        <th>Section Name</th>
        <th>Instructor</th>
        <th>Current Students</th>
    </tr>
    """
    for record in records:
        results += "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(*record)
    results += "</table></div></body></html>"

    return results

# 首頁和學生功能
@app.get('/', response_class=HTMLResponse)
def index():
    form = """
    <form method="post" action="/selected" >
        輸入學號查詢已選課列表：<input name="my_head">
        <input type="submit" value="查詢">
    </form>
    """
    form += """
    <form method="post" action="/select" >
        輸入學號查詢可選課列表：<input name="my_head">
        <input type="submit" value="查詢">
    </form>
    """ 
    form += """
    <form method="post" action="/course_detail" >
        輸入課程代碼查詢課程詳細內容：<input name="section_id">
        <input type="submit" value="查詢">
    </form>
    """     
    return form


# 管理者用的課程管理介面
@app.get('/admin', response_class=HTMLResponse)
def admin_interface():
    form = """
    <h2>Admin Course Management Interface</h2>
    <form method="post" action="/admin/add_course">
        Add Course:<br>
        Course Name: <input type="text" name="course_name"><br>
        Credits: <input type="number" name="credits"><br>
        Type (Elective/Required): <input type="text" name="course_type"><br>
        <input type="submit" value="Add Course">
    </form>
    """
    form += """
    <form method="post" action="/admin/remove_course">
        Remove Course:<br>
        Course ID: <input type="text" name="course_id"><br>
        <input type="submit" value="Remove Course">
    </form>
    """
    return form

# 管理者新增課程功能
@app.post('/admin/add_course', response_class=HTMLResponse)
def add_course(course_name: str = Form(...), credits: int = Form(...), course_type: str = Form(...)):
    conn = MySQLdb.connect(host="127.0.0.1", user="hj", passwd="test1234", db="coursesystem")
    cursor = conn.cursor()

    query = "INSERT INTO course (Course_name, Credits, Type) VALUES ('{}', {}, '{}');".format(course_name, credits, course_type)
    cursor.execute(query)
    conn.commit()

    return "Course added successfully!"

# 管理者移除課程功能
@app.post('/admin/remove_course', response_class=HTMLResponse)
def remove_course(course_id: str = Form(...)):
    conn = MySQLdb.connect(host="127.0.0.1", user="hj", passwd="test1234", db="coursesystem")
    cursor = conn.cursor()

    query = "DELETE FROM course WHERE Course_id = '{}';".format(course_id)
    cursor.execute(query)
    conn.commit()

    return "Course removed successfully!"

# 其他管理者動作的路由和函數
@app.post('/admin/update_course', response_class=HTMLResponse)
def update_course(course_id: str = Form(...), new_course_name: str = Form(...), new_credits: int = Form(...), new_course_type: str = Form(...)):
    conn = MySQLdb.connect(host="127.0.0.1", user="hj", passwd="test1234", db="coursesystem")
    cursor = conn.cursor()

    query = "UPDATE course SET Course_name = '{}', Credits = {}, Type = '{}' WHERE Course_id = '{}';".format(new_course_name, new_credits, new_course_type, course_id)
    cursor.execute(query)
    conn.commit()

    return "Course updated successfully!"