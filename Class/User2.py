from .Database import Database
class User(Database):
    def __init__(self):
        super().__init__()

    def login(self,idnum:str, pw:str):
        sql="select * from tbl_user where IdNumber=%s and Password=%s"
        cursor=self.conn.cursor(dictionary=True)
        cursor.execute(sql,(idnum,pw))
        res=cursor.fetchone()
        cursor.close()
        if res:
            return{
                "success":True,
                "IdNumber": res ['IdNumber'],
                "Role": res['Role']
            }
        else:
            return{
                "success":False,
                "Message": "Invalid IdNumber or Password"
            }

    def add(self, idnum:str, ln:str, fn:str, mn:str, bdate:str, address:str, contact:str):
        try:
            sql="insert into info(IdNumber, LastName, FirstName, MiddleName, BirthDate, Address, ContactNo) values(%s, %s, %s, %s, %s,%s, %s)"
            cursor=self.conn.cursor()
            cursor.execute(sql,(idnum,ln,fn,mn,bdate,address,contact))
            self.conn.commit()
            cursor.close()
            return{
                "success": True,
                "message": "Record Added"
            }
        except Exception as e:
            return {
                "success": False,
                "message":str(e)
            }
            
    def displayall(self):
        sql="select *from info order by LastName, FirstName"
        cursor=self.conn.cursor(dictionary=True)
        cursor.execute(sql)
        res=cursor.fetchall()
        cursor.close()
        return res