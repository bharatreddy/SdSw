import MySQLdb as mdb
import sys
import numpy




fileSapsModel = '/home/bharat/ESAPS/files/saps-pred-data-new.txt'


# the file contains, UT, Lats, Mlts, Prob of occ. and Season/Dst type(inp)
# About 10,000 records....

utSaps = []
latSaps = []
mltSaps = []
mlonSaps = []
probSaps = []
inpSaps = []

# open the file...loop through them and read data into arrays

fInds = open(fileSapsModel, 'r')

count = 0
for line in fInds:
    line = line.strip()
    columns = line.split()
   
    utSaps.append( float( columns[0] ) )
    latSaps.append( float( columns[1] ) )
    mltSaps.append( float( columns[2] ) )
    mlonSaps.append( float( columns[3] ) )
    probSaps.append( float( columns[4] ) )
    inpSaps.append( columns[5] )





con = None

try:

    con = mdb.connect('localhost', 'root', 
        'bharat', 'SAPS');

    with con:
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS \
            SAPSprobmodel( UTtime INT, Lat FLOAT, Mlt FLOAT, Mlon FLOAT, Probability FLOAT, inptype VARCHAR(10) )")
        
        for s1, s2, s3, s3_2, s4, s5 in zip(utSaps, latSaps, mltSaps, mlonSaps, probSaps, inpSaps) :
#            print "INSERT INTO SAPSprobmodel(UTtime, Lat, Mlt, Probability, inptype)\
#                VALUES("+str(s1)+", "+str(s2)+", "+str(s3)+", "+str(s4)+", '"+s5+"')"
            
            popTabStr = "INSERT INTO SAPSprobmodel(UTtime, Lat, Mlt, Mlon, Probability, inptype) \
                VALUES("+str(s1)+", "+str(s2)+", "+str(s3)+", "+str(s3_2)+", "+str(s4)+", '"+s5+"')"

            cur.execute(popTabStr)
        
except mdb.Error, e:

    print "Error %d: %s" % (e.args[0],e.args[1])
    sys.exit(1)

finally:    
    
    if con:    
        con.close()    