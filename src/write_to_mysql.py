'''
This class will open the files and write to the mysql database.
Before running this, you will need to run this in mysql: 
    create database NLP_Reviews;
    create user 'defaultuser'@'localhost' identified by '';
    grant all privileges on *.* to 'defaultuser'@'localhost'
    create table if not exists CdnTireReviews (
    reviewKey int not null auto_increment primary key,
    productCode varchar(30) not null,
    productName varchar(200),
    description varchar(1000),
    avgRating float,
    numReviews int,
    department varchar(50),
    category varchar(50),
    subCategory varchar(100),
    price float,
    stars float,
    reviewDate date not null,
    reviewTitle varchar(255),
    reviewText varchar(2000)    
    );
'''
from __future__ import division
import MySQLdb
import sys
from os import listdir
from os.path import isfile, join

class DatabaseProperties():
    def __init__(self):
        # Should have this initialized
        self.hostname = "localhost"
        self.user = "defaultuser"
        self.password = ""
        self.dbName = "NLP_Reviews"
        
        self.tableName = "CdnTireReviews"
        
        self.dbToVarMap = {'Product Code': 'productCode',
                           'Product Name':'productName',
                           'Description':'description',
                           'Avg Rating':'avgRating',
                           'Num Reviews':'numReviews',
                           'Department':'department',
                           'Category':'category',
                           'Subcategory':'subCategory',
                           'Price':'price',
                           'Stars':'stars',
                           'Date':'reviewDate',
                           'Title':'reviewTitle',
                           'Text':'reviewText',
                           }
        self.dbErrorList = ["avgRatingERROR", "numERROR", 'revTextERROR', "titlListERROR", "titleERROR", "dateListERROR", "starsListERROR", "codeERROR", "nameERROR", "descriptionERROR", "priceERROR", 'depERROR','catERROR','subCatERROR']
        
        self.numList = ['avgRating', 'numReviews', 'price', 'stars']

class DatabaseActions():
    # base class for add, update, and remove
    def __init__(self, dbProperties):
        self.dbProperties = dbProperties
        self.mysqlconnect()
    
    def mysqlconnect(self):
        try:
            self.conn = MySQLdb.connect(self.dbProperties.hostname, 
                                   self.dbProperties.user, 
                                   str(self.dbProperties.password),
                                   self.dbProperties.dbName)
            self.cursor = self.conn.cursor()
        except MySQLdb.Error, e:
            print e.args
            print 'Error: %d %s' %(e.args[0], e.args[1])
            sys.exit(1)
    
    def insert(self, sql):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except MySQLdb.Error, e:
            print e.args
            print 'Error: %d %s' %(e.args[0], e.args[1])
            
    def processErrors(self, elem):
        if elem in self.dbProperties.dbErrorList:
            return None
        else:
            return elem
    
    def __del__(self):
        # Close cursor
        self.cursor.close()
        self.conn.close()
        print 'DB connection closed!'
    
class CdnTireActions(DatabaseActions):
    def generate_insert(self, filename):
        with open(filename, 'r') as f:
            content = f.readlines()
            if len(content) % 13 != 0:
                print "Invalid file!, not 13 lines"
                # Write file name to a list
                with open('ErrorFiles.txt', 'w+') as ff:
                    ff.write(filename + '\n')
            else:
                itr = len(content)/13
                print "Number of reviews to iterate through: ", itr
                for i in range(int(itr)):
                    insertsql = "insert into " + self.dbProperties.tableName + " (%s) values (%s)" 
                    cols = ""
                    vals = ""
                    for line in content[i*13+0:i*13+13]:
                        elem = line.split(":", 1)
                        val = self.processErrors(elem[1].strip())
                        if val is not None:
                            col = self.dbProperties.dbToVarMap[elem[0]]
                            cols += col + ","
                            if col in self.dbProperties.numList:
                                vals += val + ","
                            else:
                                vals += "'" + val.replace("'","''") + "',"
                    cols = cols[:-1]
                    vals = vals[:-1]
                    insertsql = insertsql %(cols, vals)
                    print insertsql
                    # Now, insert sql into db.
                    #self.insert(insertsql)
                    print "Insert completed"
    def insert_all(self, directory):
        # given a directory, iterate through all files.
        onlyfiles = [ f for f in listdir(directory) if isfile(join(directory,f)) ]
        for f in onlyfiles:
            self.generate_insert(join(directory,f))
        print "Inserted " + str(len(onlyfiles)) + " into the database."

# Execute this now.
CdnTireActions(DatabaseProperties()).insert_all("/home/ivan/temp")
        
        
        
    