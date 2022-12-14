import mysql.connector
import json
mydb=mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456789",
    database="WEBSITE"
)
print("成功連接到資料庫")


# 初始化伺服器
from flask import *
app=Flask(
    __name__,
    static_folder="public",
    static_url_path="/"
)
app.secret_key="secretKey"

# 處理路由
@app.route("/")
def index():
    return render_template("index.html")

# 進入會員頁
@app.route("/member")
def member():
    if "nickname" in session:
        nickname=session["nickname"]
        if nickname!="":
            nickname=nickname+"，"
        return render_template("/member.html",nic=nickname)
    else:
        return redirect("/")

# 回應前端對於留言的資料請求,從資料庫取得資料後先轉成json格式，方便前端處理
@app.route("/resultContentRequest")
def resultContentRequest():
    mycursor=mydb.cursor()
    sql="SELECT NAME , content FROM MEMBER INNER JOIN MESSAGE ON MEMBER.ID=MESSAGE.MEMBER_ID order by time DESC"
    mycursor.execute(sql)
    allContent=mycursor.fetchall()
    jsonStr=json.dumps(allContent)
    jsonStr=str(jsonStr)
    return jsonStr

# /error?msg=錯誤訊息
@app.route("/error")
def error():
    message=request.args.get("msg","發生錯誤，請聯繫克服")
    return render_template("error.html",msa=message)

# 進入註冊頁面
@app.route("/register")
def register():
    return render_template("register.html")

# 註冊帳號 - 與資料庫互動
@app.route("/signup",methods=["POST"])
def signup():
    nickname=request.form["nickname"]
    email=request.form["email"]
    password=request.form["password"]
    mycursor=mydb.cursor()
    sql="SELECT * FROM MEMBER WHERE EMAIL = %s"
    mycursor.execute(sql,email)



    nicknameResult=mycursor.fetchall()
    if(len(nicknameResult) != 0):
        return redirect("/error?msg=信箱已經被註冊")
    mycursor=mydb.cursor()
    sql="INSERT INTO MEMBER(NAME,EMAIL,PASSWORD) VALUES (%s,%s,%s)"
    val = (nickname,email,password)
    mycursor.execute(sql,val)
    mydb.commit()
    return redirect("/")


# 登入 - 確認帳號密碼
@app.route("/signin",methods=["POST"])
def signin():
    passwordIndex=3
    email=request.form["email"]
    password=request.form["password"]
    mycursor=mydb.cursor()
    sql="SELECT * FROM MEMBER WHERE EMAIL = %s"
    mycursor.execute(sql,email)
    clientGet=mycursor.fetchall()
    print(clientGet)
    if(len(clientGet)==0):
        return redirect("/error?msg=帳號或密碼輸入錯誤")
    if(len(clientGet) != 0):
        if(clientGet[0][passwordIndex]!=password):
            return redirect("/error?msg=帳號或密碼輸入錯誤2")
    session["nickname"]=clientGet[0][1]
    session["id"]=clientGet[0][0]
    return redirect("/member")


# 登出 - 清除session資料
@app.route("/signout")
def signout():
    del session["nickname"]
    return redirect("/")


# 留言 - 透過此路遊將網頁上輸入的資訊傳入資料庫
@app.route("/leaveMessage")
def leaveMessage():
    member_id=session["id"]
    content=request.args.get("content","")
    mycursor=mydb.cursor()
    sql="INSERT INTO message(MEMBER_ID,CONTENT) VALUES (%s,%s)"
    val = (member_id,content)
    mycursor.execute(sql,val)
    mydb.commit()
    return redirect("/member")

app.run(port=3000)