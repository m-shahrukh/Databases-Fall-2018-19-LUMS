from flask import Flask, render_template, json, request
from flaskext.mysql import MySQL
#import mysql.connector


############# Helper functions

def delete_query(conn,cursor, table_name, col_name, ID):
    query= "DELETE FROM {t} WHERE {c}={i}".format(t=table_name, c=col_name, i=ID)
    cursor.execute(query)
    conn.commit()

def make_list(known_values, problematic_values):
    #known values is already a tuple. problematic values is a list.
    list_of_tuples=[]
    while None in problematic_values or "" in problematic_values:
      if None in problematic_values:
        problematic_values.remove(None)
      if "" in problematic_values:
        problematic_values.remove("")

    for x in problematic_values:
        list_of_tuples.append(known_values+(x,))

    return list_of_tuples


def insert_query(conn, cursor, data, columns, table_name):
    str_data="("
    for x in data:
        if type(x) is str:
            str_data+= "'%s'" % x +","
            continue
        str_data+= str(x)+","
    str_data=str_data[0:len(str_data)-1]+")"   
    query= "INSERT INTO {} {}".format(table_name, columns) +" "+"VALUES {}".format(str_data)
            
    cursor.execute(query)
    conn.commit()


def GetMaxID(conn, cursor, table_name, col_name): #get max ID of Acceptor/Donor, Flag=1= Donor, 2= Donor 3= Acceptor, 4= Blood Drive, 5= Sample, 6= Issue, 7= Pending Req 
# Take table_name, id_col name and just %s it fam no need of flag
# needs connection and cursor object to MySQL as well. Returns 0 if null
    
      query= ("SELECT IF (not exists(select {0} from {1} where {0}=1), 1,0)".format(col_name,table_name))
      cursor.execute(query)
      conn.commit()
      result= cursor.fetchone()[0]
      bank_id=0
      if result==1:
        bank_id=1
      else:
        query2= ("SELECT MAX({}) from {}".format(col_name,table_name))
        cursor.execute(query2)
        conn.commit()
        bank_id= (cursor.fetchone()[0])

        bank_id+=1

      return bank_id

    
def get_ID(conn,cursor,table_name,col_name, condition_col, condition):
        query= ("SELECT IF ( exists(select {0} from {1} where {2}={3}),1,0)".format(col_name,table_name,condition_col,condition))
        cursor.execute(query)
        conn.commit()
        result= cursor.fetchone()
        print (result)
        if result[0]==1:
            query= ("select {0} from {1} where {2}={3}".format(col_name,table_name,condition_col,condition))
            cursor.execute(query)
            conn.commit()
            result1=cursor.fetchall()

            result=[]
            for i in result1:
                result.append(i[0])
            return tuple(result)


        else:
            return ()


############################################ starting flask app and connecting to MySQL
app = Flask(__name__)
mysql = MySQL()
_name=None
_email=None
_password=None
data=None
 
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'abcdef12345'
app.config['MYSQL_DATABASE_DB'] = 'bbms_panga'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


######################### view functions 
@app.route ("/SampleReq/<option>", methods=['GET','POST'])
def SampleReq(option):
  if option=="Sample":
       return render_template('IssueSample.html', who='Sample', redirect="/InsertBlood/Sample")
  elif option=="Request":
    return render_template('IssueSample.html', who='Request', redirect="/InsertBlood/Request")
   
#############################################################################################
@app.route("/InsertBlood/<option>", methods=['POST'])
def InsertBlood(option):
    date=request.form['Date']
    ID=None
    conn= mysql.connect()
    cursor= conn.cursor()

    ID1=None
    if option=="Sample":
        ID= request.form['donorID']
        #ID1= GetMaxID(conn,cursor,table_name, col_name)
        table_name="blood_sample"
        col_name="sample_id"
        columns1="(sample_id,date_of_sample)"
        ID1=GetMaxID(conn,cursor,table_name,col_name)

        data1=(ID1,date)
        columns="(sample_id, donor_id)"
        data=(ID1, ID)
        insert_query(conn,cursor,data,columns, table_name)
        insert_query(conn,cursor,data1,columns1, "sample_dates")

        query= R"SELECT blood_donor.donor_id, blood_acceptor.acceptor_id, pending_requests.Request_ID, pending_requests.DateOfRequest, blood_acceptor.blood_type from blood_donor inner join blood_acceptor inner join pending_requests on blood_donor.blood_type=blood_acceptor.blood_type and blood_acceptor.acceptor_id= pending_requests.acceptor_id"
        cursor.execute(query)
        conn.commit()
        result= cursor.fetchall()
        req_id=None
        acceptor_id=None
        # date=""
        #print(ID)
       # print(type(ID))
        if result[0][0]==None or result[0][0]=="":

         for x in result:
            #print(type(x[0]))
            if int(ID)==(x[0]):
                print(x[0])
                req_id=x[2]
                acceptor_id=x[1]
         #       date=x[3]
                break
         print(acceptor_id)
         ID2= GetMaxID(conn,cursor,"Blood_issued", "issue_id")
         insert_query(conn,cursor, (ID2, ID , acceptor_id), "(issue_id,donor_id,acceptor_id)", "Blood_issued")
         insert_query(conn,cursor, (ID2,date), "(issue_id, dateofissue)", "issued_dates")
         delete_query(conn,cursor, "blood_sample", "sample_id", ID1)
         delete_query(conn,cursor, "pending_requests", "request_id", req_id)


    elif option=="Request":
        ID=request.form['AcceptorID']
        table_name="Pending_requests"
        col_name="request_id"
        # columns1=("sample_id","date_of_sample")
        ID1=GetMaxID(conn,cursor,table_name,col_name)

        #data1=(ID1,date)
        columns="(request_id, acceptor_id, dateofrequest)"
        data=(ID1, ID, date)
        # request table is ready to be inserted.
        query="SELECT blood_type FROM blood_acceptor where acceptor_id={}".format(ID)
        cursor.execute(query)
        conn.commit()
        blood_group=cursor.fetchone()[0]
        query=R"SELECT IF ( EXISTS (SELECT blood_donor.donor_id from blood_donor INNER JOIN blood_sample ON blood_donor.donor_id=blood_sample.donor_id where"+ " blood_type= '{}'),1,0)".format(blood_group)
        cursor.execute(query)
        conn.commit()
        check=cursor.fetchone()[0]
        if check==0:
            insert_query(conn,cursor,data,columns, table_name)
            return "<h1> Request Added </h1"
        else:
            query=R"SELECT blood_donor.donor_id from blood_donor INNER JOIN blood_sample ON blood_donor.donor_id=blood_sample.donor_id where"+ " blood_type= '{}'".format(blood_group)
            print(query)
            cursor.execute(query)
            conn.commit()
            donor_id=cursor.fetchone()[0]
            ID1=GetMaxID(conn,cursor,"Blood_issued","issue_id")
            query= "SELECT sample_id from blood_sample where donor_id={}".format(donor_id)
            cursor.execute(query)
            conn.commit()
            sample_id=cursor.fetchone()[0]
            columns="(issue_id,donor_id,acceptor_id)"
            data=(ID1, donor_id, ID)
            insert_query(conn,cursor,data,columns, "Blood_issued")
            insert_query(conn,cursor,(ID1,date), "(issue_id, dateofissue)", "issued_dates")
            delete_query(conn,cursor, "blood_sample", "sample_id", sample_id)
            #delete_query(conn,cursor,table_name,"request_id", )

            return "<h1> Request fulfilled. Blood Issued. Issue ID: {} </h1>".format(ID1)

   
    return render_template('return.html', myvar='insert', ID=ID1)


#######################################################################################################
@app.route("/Querie")
def Querie():
    return render_template('Queries.html')

######################################################################################
@app.route("/InsertDrive", methods=['POST'])      #Insert a Blood Drive
def InsertDrive():
    bank_id, location= request.form['bankID'], request.form['Location']
    start_date= request.form['SD']
    end_date= request.form['ED']
    conn= mysql.connect()
    cursor=conn.cursor()
    drive_id= GetMaxID(conn, cursor, "blood_drive", "drive_id")
    data= (drive_id,bank_id,location, start_date, end_date)
    columns= "(drive_id, bank_id, location, starting_date, ending_date)"
    insert_query(conn,cursor,data,columns,"blood_drive")

    return render_template('return.html', myvar= 'insert', ID=drive_id)

######################################################################################################################### Insert a Drive Donor
@app.route("/Insert_Drive_Donor", methods=['POST'])
def Insert_Drive_Donor():
    drive_id, fname, gender, dob, BT= request.form['ID'], request.form['Fname'], request.form['gender'], request.form['dob'], request.form['BT']
    donation_date=request.form['DD']
    conn=mysql.connect()
    cursor=conn.cursor()
    donor_id= GetMaxID(conn,cursor,"blood_drive_donor","drive_donor_id")
    data= (donor_id,drive_id,fname,gender,dob,BT,donation_date)
    columns= "(drive_donor_id, drive_id, full_name, gender, dateofbirth, blood_type,donation_date)"
    insert_query(conn,cursor,data,columns, "blood_drive_donor")

    return render_template('return.html', myvar='insert', ID=donor_id)




######################################################################################################################### Insert an Acceptor
@app.route("/UpdatePerson", methods=['POST'])
def UpdatePerson():
    return "<h1> IN PROGRESS</h1>"


############################################################################################################################### Insert a Donor
@app.route("/InsertPerson/<option>", methods=['POST'])
def InsertPerson(option):
    table_name1,table_name2,table_name3,table_name4,table_name5,table_name6= (None,)*6
    col_name=None

    print(option)
    columns_1, columns_2, columns_3, columns_4, columns_5= (None,)*5
    if option.find("Acceptor")>=0:
        table_name1,table_name2,table_name3,table_name4,table_name5= "blood_acceptor", "acceptor_email", "acceptor_address","acceptor_contact", "acceptor_bank"
        table_name6="acceptor_diseases"
        columns_1="(acceptor_id, full_name, gender, weight, blood_type, dateofbirth)"
        columns_2="(acceptor_id, email)"
        columns_3="(acceptor_id,address)"
        columns_4="(acceptor_id,contact)"
        columns_5="(acceptor_id,bank_id)"
        col_name='acceptor_id'
        columns_6="(acceptor_id,disease_id)"

    else:
        
        table_name1,table_name2,table_name3,table_name4,table_name5= "blood_donor", "donor_email", "donor_address","donor_contact", "donor_bank"
        table_name6="donor_diseases"
        columns_1="(donor_id, full_name, gender, weight, blood_type, dateofbirth)"
        columns_2="(donor_id, email)"
        columns_3="(donor_id,address)"
        columns_4="(donor_id,contact)"
        columns_5="(donor_id,bank_id)"
        col_name='donor_id'
        columns_6="(donor_id,disease_id)"


       
    banks, full_name, gender, blood_type, weight, dob= request.form['banks'], request.form['inputfullname'], request.form['Gender'], request.form['BT'], request.form['WT'], request.form['DOB']
    email1, email2, addr1, addr2, contact1, contact2= request.form['E1'], request.form['E2'], request.form['A1'], request.form['A2'], request.form['C1'], request.form['C2']
    conn = mysql.connect()
    cursor=conn.cursor()
    Id=GetMaxID(conn, cursor, table_name1, col_name)

    data=(Id, full_name, gender, weight, blood_type, dob)
    data_email= make_list((Id,), [email1,email2])
    data_addr= make_list((Id,), [addr1,addr2])
    data_contact= make_list((Id,), [contact1,contact2])
    banks= banks.split()
    banks= [int(x) for x in banks]
    data_bank= make_list((Id,), banks)
    if option.find('Update')>=0:
        Id= request.form['pk']
        #update_query(conn,cursor,data,columns_1,table_name1)




    insert_query(conn,cursor,data,columns_1,table_name1)


    d1= request.form.getlist('disease')
    d1= [int(x[1]) for x in d1]
    data_disease= make_list((Id,), d1)

    if len(data_disease)==0:
           insert_query(conn,cursor,(Id,0),columns_6,table_name6)

    else:
          for x in data_disease:
            insert_query(conn, cursor, x, columns_6, table_name6)

    for x in data_addr:
        insert_query(conn, cursor,x, columns_3,table_name3)

    for x in data_contact:
        insert_query(conn,cursor,x, columns_4, table_name4)


    for x in data_email:
        insert_query(conn,cursor,x,columns_2,table_name2)

    for x in data_bank:
        insert_query(conn, cursor,x, columns_5, table_name5)

    return render_template('return.html', myvar= 'insert', ID=Id)
    # get the input. we need to put in big ass SQL queries to insert in each of the normalized tables. 
########################################################################################################### Insert a bank
@app.route("/InsertBank", methods=['POST'])
def InsertBank():
    
    bank_addr= request.form['inputbankaddress']
    bank_city= request.form['inputCity']
    # query= ("SELECT IF (not exists(select {0} from {1} where {0}=1), 1,0)".format('bank_id','blood_bank'))
    conn = mysql.connect()

    cursor= conn.cursor()
    # cursor.execute(query)
    # conn.commit()
    # result= cursor.fetchone()[0]
    bank_id=GetMaxID(conn,cursor,'blood_bank', 'bank_id')
    # return "<h1> %s </h1>" % result
    
    query= ("INSERT INTO blood_bank (bank_id, address, city, `A+`, `A-`, `B+`, `B-`, `AB+`, `AB-`, `O+`, `O-`)"
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
    
    cursor.execute(query, (bank_id,bank_addr,bank_city,0,0,0,0,0,0,0,0))
    conn.commit()

    return render_template('return.html', myvar='insert', ID=bank_id)



################################################################################################ Delete   
@app.route("/deletegeneral/<option>", methods=['POST'])
def deletegeneral(option):
    ID= request.form['ID']
    conn=mysql.connect()
    cursor=conn.cursor()
    col_name= option[ option.find('_')+1: ]+"_id"
    donor_id=get_ID(conn,cursor,"donor_bank","donor_id",col_name, ID)
    #print (donor_id)
    acceptor_id=get_ID(conn,cursor,"acceptor_bank","acceptor_id",col_name, ID)
    delete_query(conn,cursor,option,col_name, ID)

    if donor_id!=():
        #return "HALO"
      for x in donor_id:
       check= get_ID(conn,cursor,"donor_bank","bank_id","donor_id",x)
       if check==():
        delete_query(conn,cursor,"blood_donor", "donor_id", x)

    if acceptor_id!=():
        #return "HALO"
      for x in acceptor_id:
       check= get_ID(conn,cursor,"acceptor_bank","bank_id","acceptor_id",x)
       if check==():
         delete_query(conn,cursor,"blood_acceptor", "acceptor_id", x)
    
    return render_template('return.html', myvar='delete', ID=ID)



@app.route("/Delete")
def delete():
    return render_template('insert.html', flag='delete', redirect= '/Menu/Delete')

@app.route("/Search")
def Search():

    return "<h1> IN PROGRESS</h1>"



@app.route("/Update")
def Update():
    return render_template('insert.html', flag= 'Update', redirect='/Menu/Update')

@app.route("/")
def appp():
    
    return render_template('index.html')

@app.route('/Insert')
def Insert():
    return render_template('insert.html', flag='Insert', redirect='/Menu/Insert')

@app.route("/main")
def m1():
    return appp()

@app.route("/show")
def show():
    return data



@app.route("/Q4inter")
def Q4inter():
    return render_template('query4.html')

@app.route("/Q4",methods=['POST'])
def Q4():
    gender= request.form["Gender"]
    blood_type= request.form["BT"]
    conn=mysql.connect()
    cursor= conn.cursor()
    cursor.callproc('Query4', ('%s'%gender, '%s'%blood_type))
    result=cursor.fetchall()
    final=[]
    #print(result)
    if result==() or result=="":
        final.append( "The Query returned an Empty Table")
    else:
        for x in result:
            final.append(x[0])
    return render_template('return.html', myvar='Query 4', list=final)


@app.route("/Q5inter")
def Q5inter():
    return render_template('query5.html')

@app.route("/Q5", methods=['POST'])
def Q5():
    bank_id= request.form["bankid"]
    conn=mysql.connect()
    cursor= conn.cursor()
    cursor.callproc('Query5A', (bank_id,))
    result_min= cursor.fetchone()
    final_min=[result_min[1], result_min[0]]

    cursor.callproc('Query5B', (bank_id,))
    result_max= cursor.fetchone()
    final_max=[result_max[1], result_max[0]]
    
    return render_template('return.html', myvar="Query 5", list=[final_min,final_max])

@app.route("/Q6")
def Q6():
    conn=mysql.connect()
    cursor= conn.cursor()
    cursor.callproc('Query6')
    result= cursor.fetchall()
    if result==() or result=="" :
        result=[["The Query returned an empty table"]]
    return render_template('return.html', myvar='Query 6', list= result, len= len(result[0]))


@app.route("/Q7")
def Q7():
    conn=mysql.connect()
    cursor= conn.cursor()
    cursor.callproc('Query7')
    result= cursor.fetchall()
    if result==() or result=="" :
        result=[["The Query returned an empty table"]]
    return render_template('return.html', myvar='Query 7', list= result, len= len(result[0]))


@app.route("/Q8")
def Q8():
    conn=mysql.connect()
    cursor= conn.cursor()
    cursor.callproc('Query8')
    result= cursor.fetchone()
    final=[result[1],result[0]]
    return render_template('return.html', myvar= 'Query 8', list= final)
@app.route("/Q9")
def Q9():
    conn= mysql.connect()
    cursor=conn.cursor()
    cursor.callproc('Query9')
    result= cursor.fetchall()
    final=[]
    #print(result)
    if result==() or result=="":
        final.append( "The Query returned an Empty Table")
    else:
        for x in result:
            final.append(x[0])
    #print(final)
    return render_template('return.html', myvar="Query 9", list=final)
    
@app.route("/Q10")
def Q10():
    conn= mysql.connect()
    cursor=conn.cursor()
    cursor.callproc('Query10')
    result= cursor.fetchone()
    final=[]
    #print(result)
    if result[0]==None or result[0]=="":
        final.append( "The Query returned an Empty Table")
    else:
        final=list(result)
    #print(final)
    return render_template('return.html', myvar="Query 10", list=final)





######################################################

@app.route("/Q2inter")
def Q2inter():
    return render_template('query2.html')

@app.route("/Q2", methods=['POST'])
def Q2():
    starting_date= request.form['startingdate']
    ending_date=request.form['endingdate']
    conn= mysql.connect()
    cursor=conn.cursor()
    cursor.callproc('Query2', ('%s'%starting_date,'%s' % ending_date))
    result= cursor.fetchall()
    print(result)
    final_col1="times donated"
    final_col2="Donor ID"
    final_col3="Full Name"

    if result==() or result=="" :
        result=[["The Query returned an empty table"]]
    return render_template('return.html',myvar='Query 2', list=result, len=len(result[0]))

########################################################################3
@app.route("/Q3inter")
def Q3inter():
    return render_template("query3.html")

@app.route("/Q3", methods=['POST'])
def Q3():
    starting_date= request.form['startingdate']
    ending_date=request.form['endingdate']
    conn= mysql.connect()
    cursor=conn.cursor()
    cursor.callproc('Query3', ('%s'%starting_date,'%s' % ending_date))
    result= cursor.fetchall()
    final=[]
    #print(result)
    if result[0][0]==None or result[0][0]=="":
        final.append( "The Query returned an Empty Table")
    else:
        for x in result:
            final.append(x[0])
    #print(final)
    return render_template('return.html', myvar="Query 3", list=final)



####################################
#Query 1

@app.route("/Q1inter")
def Q1inter():
    return render_template("Q1.html")


@app.route("/Q1",methods=['POST'])
def Q1():
    disease_id= request.form['D_ID']
    conn= mysql.connect()
    cursor= conn.cursor()
    cursor.callproc('Query1',(disease_id,))
    result= cursor.fetchone()[0]
    return render_template('return.html', myvar= "Query 1", list=result)

#######################################
@app.route('/Menu/<option>', methods=['POST'])
def Menu(option):
 resp=(request.form["options"])

 if option=="Insert":
  if resp=="Blood Bank":
    return render_template('create_bank.html')

  elif resp=="Blood Donor":
    return render_template('create_donor.html', who='Donor', redirect="/InsertPerson/Donor")

  elif resp=="Blood Acceptor":
    return render_template('create_donor.html', who='Acceptor',redirect="/InsertPerson/Acceptor" )

  elif resp=="Blood Drive":
    return render_template('blood_drive.html')

  elif resp=="Blood Drive Donor":
    return render_template('blood_drive_donor.html')

##########################################################
 elif option=="Delete":
    if resp=="Blood Bank":
      return render_template('UDS.html', flag='delete', redirect='/deletegeneral/blood_bank')

    elif resp=="Blood Donor":
      return render_template('UDS.html',  flag='delete', redirect='/deletegeneral/blood_donor')

    elif resp=="Blood Acceptor":
      return render_template('UDS.html',  flag='delete', redirect='/deletegeneral/blood_acceptor' )

    elif resp=="Blood Drive":
      return render_template('UDS.html', flag='delete', redirect='/deletegeneral/blood_drive')

    elif resp=="Blood Drive Donor":
      return render_template('UDS.html', flag='delete', redirect='/deletegeneral/blood_drive_donor')

##########################################################33
 elif option=="Update":
  if resp=="Blood Bank":
    return render_template('update_driveorbank.html',  flag='blood bank', redirect="/InsertBank/DonorUpdate")

  elif resp=="Blood Donor":
    return render_template('update_person.html', who='Donor', redirect="/InsertPerson/DonorUpdate")

  elif resp=="Blood Acceptor":
    return render_template('update_person.html', who='Acceptor',redirect="/InsertPerson/AcceptorUpdate" )

  elif resp=="Blood Drive":
    return render_template('Update_driveorbank.html', flag='blood drive', redirect="/InsertDrive/DonorUpdate")

  elif resp=="Blood Drive Donor":
    return render_template('Update_driveorbank', flag='blood drive donor', redirect="/Insert_Drive_Donor/DonorUpdate")
 #####################################################################
 elif option=="Search":
  if resp=="Blood Bank":
    return render_template('create_bank.html')
  elif resp=="Blood Donor":
    return render_template('create_donor.html', who='Donor', redirect="/InsertPerson/Donor")

  elif resp=="Blood Acceptor":
    return render_template('create_donor.html', who='Acceptor',redirect="/InsertPerson/Acceptor" )

  elif resp=="Blood Drive":
    return render_template('blood_drive.html')

  elif resp=="Blood Drive Donor":
    return render_template('blood_drive_donor.html')


if __name__ == "__main__":
    #main()
    app.run(debug=True)

