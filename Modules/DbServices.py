# All of the database (Sqlite3) functionality:
# - PROJECTS
# - SESSIONS
# - OTHER

# Python sqlite3
# https://docs.python.org/3/library/sqlite3.html
# SQLITE3 Datatypes: TEXT (str), REAL (float), INTEGER (int), BLOB (bytes)

import sqlite3
import datetime
import random

from os import path,makedirs,remove

class DbServices():
    def __init__(self):
        # Relative paths are relative to project base folder (TimeMarker.py). 
        # Db dirs are created automatically if not existing
        self.projectHeadsPathRelative = "./ProjectHeads"
        self.projectsDbPath = "./ProjectHeads/TimeMarkerProjects.db"
        self.projectsTable = "ProjectHeads"
        self.sessionsPathRelative = "./Projects"
        self.sessionsTable = "sessions"
        
    # PROJECTS

    def getProjects(self):
        # Name | database path
        print("Get Projects")
        self.assurePath(self.projectHeadsPathRelative)
        self.assureProjectHeadDb()
        projects = self.getAllProjectHeads()
        projects = reversed(projects)
        return projects

    def assurePath(self, dbPath):
        print(f"- assurePath: {dbPath}")
        try:
            # exists_ok=True --> succeeds even if directory exists (won't raise FileExistsError)
            makedirs(dbPath, exist_ok=True)
        except OSError as error:
            print("--> OSError: " + str(error))

    def assureProjectHeadDb(self):
        print("- assureProjectHeadDb")
        conn = None
        try:
            #  connect() --> If that database does not exist, then it’ll be created. 
            conn = sqlite3.connect(self.projectsDbPath)
            cursor = conn.execute(f'''CREATE TABLE IF NOT EXISTS {self.projectsTable}( 
            ID TEXT,
            NAME TEXT,
            SESSIONSDBPATH TEXT,
            DATE TEXT,
            DESCRIPTION TEXT,
            HOURSTOTAL REAL);''')
            cursor.close()
            print("-> Project Head DB created / exists")
        except sqlite3.Error as error:
            print('--> SQLITE3 Error: ', error)
        finally:
            if conn:
                conn.close()
                print(f'--> SQLite Connection closed ({self.projectsDbPath})')

    def getAllProjectHeads(self):
        print("- getAllProjectHeads")
        result = []
        conn = None
        try:
            conn = sqlite3.connect(self.projectsDbPath)
            cursor = conn.cursor()

            # queryProjectNames = f"SELECT NAME from {self.projectsTable} "
            query = f"SELECT * FROM {self.projectsTable};"
            cursor = conn.execute(query)
            # Fetch and output result
            # ID, NAME, SESSIONSDBPATH, DATE, DESCRIPTION, HOURSTOTAL
            result = cursor.fetchall()
            print(f"-> Fetched {len(result)} Project Heads")
            cursor.close()
        except sqlite3.Error as error:
            print("--> SQLITE3 error: " + str(error))
        finally:
            if (conn):
                conn.close()
                print(f'--> SQLite Connection closed ({self.projectsDbPath})')

        return result

    def getProjectWithId(self,id):
        print("getProjectWithId: " + id)
        conn = None
        project = []
        try:
            conn = sqlite3.connect(self.projectsDbPath)
            query = f"SELECT * FROM {self.projectsTable} WHERE ID = (?)"
            cursor = conn.execute(query, (str(id),))
            project = cursor.fetchone()
            cursor.close()
        except sqlite3.Error as error:
            print("--> SQLITE3 error: " + str(error))
        finally:
            if(conn):
                conn.close()
                print(f"--> SQLITE3 connection closed ({self.projectsDbPath})")
        return project
   
    def createNewProjectDbFiles(self, name, description):
        print("createNewProjectDbFiles")
        # Make new entry to project collections
        (id,dbPath) = self.insertProjectHeadToDb(name,description)
        # Create DB for the project sessions
        sessionsMsg = " - sessions table failed to be created"
        if len(dbPath) > 0:
            self.createSessionTable(dbPath)
            sessionsMsg = " - sessions table created"
        print("-> New Project inserted to head " + sessionsMsg)
        # Return project id
        return id

    def insertProjectHeadToDb(self, name, description):
        print("insertProjectHeadToDb: " + name)
        # Project pointer
        
        dbPath = ""
        date = str(datetime.datetime.now()).split(".")[0]
        idStr = ""
        hourstotal = 0.0
        conn = None
        # Assure path to sessions DBs
        self.assurePath(self.sessionsPathRelative)
        try:
            dbPath = self.sessionsPathRelative + "/" + str(name +"_"+ date) + ".db"
            dbPath = dbPath.replace(" ","_").replace("-","_").replace("ä","a").replace("ö","o").replace(":","_")
            idStr = self.randomString("p-")
            print(f"-> Created an project id ({idStr}) and a custom path for new session db: {dbPath}")
            conn = sqlite3.connect(self.projectsDbPath)

            # ID, NAME, SESSIONSDBPATH, DATE, DESCRIPTION
            query = f'''INSERT INTO {self.projectsTable} VALUES (?,?,?,?,?,?)'''
            print("-> query: " +query)
            conn.execute(query,(idStr,name,dbPath,date,description,hourstotal))
            conn.commit()
            print("-> Project Head inserted to DB")
            # cursor.close()

        except sqlite3.Error as error:
            print("--> SQLITE3 error: " + str(error))
            dbPath = ""
        finally:
            if(conn):
                conn.close()
                print(f'--> SQLite Connection closed ({self.projectsDbPath})')

        return (idStr,dbPath)

    def updateProjectRow(self, projectId, columnName, newValue):
        print(f"updateProjectRow. \n -> Row id: {projectId}, columnName: {columnName}, newValue: {newValue}")
        conn = None
        params = ({ "id":projectId, "val":newValue})
        try:
            conn = sqlite3.connect(self.projectsDbPath)
            cur = conn.cursor()
            query = f"UPDATE {self.projectsTable} SET {columnName} = :val WHERE ID = :id"
            cur.execute(query,params)
            conn.commit()
            cur.close()
            print("-> Project Head DB Update committed")
        except sqlite3.Error as error:
            print("--> SQLITE3 error: " + str(error))
        finally:
            if(conn):
                conn.close()
                print(f"--> SQLITE3 connection closed ({self.sessionsTable})")

    def removeRowFromProjectsDb(self, id):
        print("removeRowFromProjectsDb")
        conn = None
        try:
            conn = sqlite3.connect(self.projectsDbPath)
            cursor = conn.cursor()
            query = f"DELETE FROM {self.projectsTable} WHERE ID = (?)"
            params = (id,)
            cursor.execute(query,params)
            conn.commit()
            cursor.close()
            print("-> Project removed from DB")
        except sqlite3.Error as error:
            print("--> SQLITE3 error: " + str(error))
        finally:
            if (conn):
                conn.close()
                print("--> SQLITE3 connection closed")

    # SESSIONS

    def createSessionTable(self,dbPath):
        print("createSessionTable-> " + dbPath)
        if not dbPath:
            print("--> ERROR. No DB path given to create session table into")
            return 
        conn = None
        try:
            #  connect() --> If that database does not exist, then it’ll be created. 
            conn = sqlite3.connect(dbPath)   
            # Create a {tablename} relation 
            # Datatypes example
            # TEXT (str), REAL (float), INTEGER (int), BLOB (bytes)
            # ID, DATESTART, DATEEND, HOURS, DESCRIPTION
            conn.execute(f'''CREATE TABLE IF NOT EXISTS {self.sessionsTable}( 
            ID TEXT,
            DATESTART TEXT,
            DATEEND TEXT,
            HOURS REAL,
            DESCRIPTION TEXT);''') 
            print("-> Session table created")
        except sqlite3.Error as error:
            print('Error occurred - ', error)
        finally:
            if conn:
                conn.close()
                print('--> SQLite Connection closed')

    def getSessionRows(self, dbPath):
        print("getSessionRows - path: " + dbPath)
        conn = None
        result = []
        try:
            conn = sqlite3.connect(dbPath)
            # ID, DATESTART, DATEEND, HOURS, DESCRIPTION
            query = f"SELECT * FROM {self.sessionsTable};"
            cursor = conn.execute(query)
            result = cursor.fetchall()
            print("-> Rows:")
            for row in cursor: 
                print("  - " + str(row[0])+" "+str(row[1])+" "+str(row[2])+" "+str(row[3])+" "+str(row[4]))
            cursor.close()
        except sqlite3.Error as error:
            print("--> SQLITE3 error: " + str(error))
        finally:
            if(conn):
                conn.close()
                print(f"--> SQLITE3 connection closed ({dbPath})")
        return result

    def getAllColumnValuesFromSessions(self, dbPath, columnName):
        print("getAllColumnValuesFromSessions: " + columnName)
        conn = None
        result = []
        try:
            conn = sqlite3.connect(dbPath)
            cursor = conn.cursor()
            # would return a list of one-element tuples (value,)
            query = f"SELECT {columnName} FROM {self.sessionsTable}"
            # make array of the first element of each tuple
            result = [value[0] for value in cursor.execute(query)]
        except sqlite3.Error as error:
            print("--> SQLITE3 ERROR: " + str(error))
        finally:
            if (conn):
                conn.close()
                print("--> SQLITE3 connection closed")
        return result

    def createEmptySessionToDb(self, dbPath):
        print("createEmptySessionToDb - path: " + dbPath)

        tablename = self.sessionsTable
        if not dbPath:
            print("--> ERROR. no dbPath given")
            return 
        try:
            conn = sqlite3.connect(dbPath)
            
            # ID, DATESTART, DATEEND, HOURS, DESCRIPTION
            id = self.randomString("s-")
            conn.execute(f'''INSERT INTO {tablename} VALUES(?,?,?,?,?)''', (id, "", "", 0.0, "-"))
            conn.commit()
            print("-> Empty Session inserted to DB")

        except sqlite3.Error as error:
            print('Error occurred - ', error)
        finally:
            if conn:
                conn.close()
                print('--> SQLite Connection closed')

    def updateSessionColumn(self, dbPath, sessionId, columnName, newValue):
        print(f"updateSessionColumn. \n -> Row id: {sessionId}, columnName: {columnName}, newValue: {newValue}")
        conn = None
        params = ({ "id":sessionId, "val":newValue})
        try:
            conn = sqlite3.connect(dbPath)
            cur = conn.cursor()
            query = f"UPDATE {self.sessionsTable} SET {columnName} = :val WHERE ID = :id"
            cur.execute(query,params)
            conn.commit()
            cur.close()
            print(f"Session DB Update ({columnName}) committed")
        except sqlite3.Error as error:
            print("--> SQLITE3 error: " + str(error))
        finally:
            if(conn):
                conn.close()
                print(f"--> SQLITE3 connection closed ({self.sessionsTable})")

    def removeSessionRow(self,dbPath,sessionId):
        print("removeSessionRow, path:" + str(dbPath) +" id: " + str(sessionId))
        conn = None
        try:
            conn = sqlite3.connect(dbPath)
            cursor = conn.cursor()
            query = f"DELETE FROM {self.sessionsTable} WHERE ID = (?)"
            params = (sessionId,)
            
            cursor.execute(query,params)
            cursor.close()
            conn.commit()
            print("--> Session row removed")

        except sqlite3.Error as error:
            print("--> SQLITE3 error: " + str(error))
        finally:
            if (conn):
                conn.close()
                print(f"--> SQLITE3 connection closed ({dbPath})")
        return
        
    def deleteSessionDb(self, dbPath):
        print("deleteSessionDb")
        if not (path.isfile(dbPath)):
            return False
        try:
            remove(dbPath)
        except OSError as error:
            print("--> OSError: " + str(error))
            return False
        print("--> Session Database removed")
        return True
    
    # OTHER

    def randomString(self, prefix="p-", randomizedLetters=16, smallerChunkLength=4):
        # random string for project id and session id
        # prefix "p-" | "s-" --> for project | session id
        # return example: p-1LsF-3AyS-y9lh-wGEq
        newStr = prefix
        letters = "1234567890QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm"
        for i in range(0,randomizedLetters):
            if (i % smallerChunkLength == 0 and i != 0):
                newStr += "-"
            newStr += str(letters[ random.randint(0, len(letters)-1 ) ])

        return newStr
            