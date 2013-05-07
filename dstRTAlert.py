import urllib
from HTMLParser import HTMLParser
import string
import datetime
import os
import time
import ftplib
import sys
import numpy
from matplotlib.dates import MonthLocator, WeekdayLocator, DateFormatter
import matplotlib as mp
from calendar import monthrange
import matplotlib.pyplot as plt
import urllib2

# Some part of this code (reading Dst values of Kyoto website) is taken from Jeff's code...

class MyHTMLParser(HTMLParser):
    active=False
    table=None
    def handle_comment(self,data):
        if data.strip()==' ^^^^^ E yyyymm_part2.html ^^^^^ '.strip():
          self.active=True
        else:
          if self.active==True:
            pass
          self.active=False
    def handle_data(self, data):
        if self.active:
          self.table=data






def DstRTRd( last_email_time = datetime.datetime.today(), nemails = 0, old_storm_score = 0. ) :       


    import urllib
    from HTMLParser import HTMLParser
    import string
    import datetime
    import os
    import time
    import ftplib
    import sys
    import numpy
    from matplotlib.dates import MonthLocator, WeekdayLocator, DateFormatter
    import matplotlib as mp
    from calendar import monthrange
    import matplotlib.pyplot as plt
    import urllib2

# check if their website is working
    check_url_dstkyoto_exist = 'no'
    
    try:
       urllib2.urlopen("http://wdc.kugi.kyoto-u.ac.jp/dst_realtime/presentmonth/index.html")
       check_url_dstkyoto_exist = 'yes'
    except urllib2.HTTPError, e:
       print e.code
       check_url_dstkyoto_exist = 'no'
    except urllib2.URLError, e:
       print e.args
       check_url_dstkyoto_exist = 'no'            
        
        
    if (check_url_dstkyoto_exist == 'yes' ) :    
            # This part is taken from Jeff's Code..
            opener = urllib.FancyURLopener({})
            f = opener.open("http://wdc.kugi.kyoto-u.ac.jp/dst_realtime/presentmonth/index.html")
            text=f.read()
            
            #This array is for converting Dst back into float
            #We want floats because python NaNs are floats
            dst_val = []
            
            #We need the date/time array at the same time too..
            date_dst_arr = []
            
            # The first date value is the first hour of first day as we know..this is to get the current date
            Today = datetime.datetime.utcnow()#datetime.datetime.today()
            
            # Dst indices are plotted every hour...so our time delta is 1 hour
            dst_time_del = datetime.timedelta(hours = 1)
            
            parser = MyHTMLParser()
            parser.feed(text)
            lines=parser.table.split("\n")
            
		
            for line in lines[7:]:
		
                columns = line.split()
                
                if len( columns ) > 0. :
                    date_dst_arr.append( datetime.datetime( Today.year, Today.month, int(columns[0]), 1 ) )
                    
                    
                    for cols in range( len( columns[1:] ) ) :
                        
                        # we have a new issue some times for really hight Dst 
                        # Kyoto puts things as -96-114-132 i.e., without any spaces
                        # in such cases the whole thing get read as a single value (-96-114-132) instead of -96, -114, -132
                        # getting treated as different values
                        # this part is to take care of that...actually just remove those values as of now....
                        try:
				inNumberFloatTest = float(columns[cols + 1])
			except:
				continue
				
                        
                        #print len(columns[cols + 1])#len( columns )
                        
                        
                        # I have to do this because of the messed up way Kyoto puts up the latest dst value..
                        # mixed with 9999 (fillers) like if latest dst is 1 then Kyoto puts it as 199999.....
                        if len( columns[ cols + 1 ] ) < 5 :
                            dst_val.append( float( columns[ cols + 1 ] ) )
                        elif ( len( columns[ cols + 1 ] ) > 5 and columns[ cols + 1 ][0:3] != '999' ) :
                            mixed_messed_dst = ''
                            for jj in range(5) :
                                if columns[ cols + 1 ][jj] != '9' :
                                    mixed_messed_dst = mixed_messed_dst + columns[ cols + 1 ][jj]
                            
                            if mixed_messed_dst != '-' :
                                dst_val.append( float( mixed_messed_dst ) )
                            else :
                                dst_val.append( float( 'nan' ) )
                        else :
                            dst_val.append( float( 'nan' ) )
                            
                        
                        if cols > 0 :
                            date_dst_arr.append ( date_dst_arr[-1] + dst_time_del )
                        
                    	
            
            date_dst_arr = numpy.array( date_dst_arr )
            dst_val = numpy.array( dst_val )
            
            dst_val = dst_val[ numpy.where( numpy.isfinite( dst_val ) ) ]
            date_dst_arr = date_dst_arr[ numpy.where( numpy.isfinite( dst_val ) ) ]
            
            dst_val_30nT_arr = dst_val[ numpy.where( ( dst_val <= -30. ) & ( dst_val > -50. ) ) ]
            date_dst_30nT_arr = date_dst_arr[ numpy.where( ( dst_val <= -30. ) & ( dst_val > -50. ) ) ]
            
            dst_val_50nT_arr = dst_val[ numpy.where( dst_val < -50. ) ]
            date_dst_50nT_arr = date_dst_arr[ numpy.where( dst_val < -50. ) ]


            # Now this is the json writing part....
            # the logic and reason for doing this stuff is explained in AceDstAlert.py
            # please look into it.....it is basically the same and I'm pretty sure both these files will
            # be grouped together.

            # to do this we need an hour array
            dstHourDictArr = []
            
            # get only the dates for the latest day 
            nowDayDateVal = []
            nowDayDstVal = []

            for dd1,dsdd1 in zip(date_dst_arr,dst_val) :

                if ( (dd1.month == date_dst_arr[ -1 ].month) & (dd1.day == date_dst_arr[ -1 ].day) & (dd1.year == date_dst_arr[ -1 ].year) ) :
                    nowDayDateVal.append( dd1 )
                    nowDayDstVal.append(dsdd1)

            nowDayDateVal = numpy.array( nowDayDateVal )
            nowDayDstVal = numpy.array( nowDayDstVal )

            for dtd2 in nowDayDateVal :
                dstHourDictArr.append(dtd2.hour) 
            

            dstHourDictArr = numpy.array(dstHourDictArr)
            dstHourDictArrUniq = numpy.unique(dstHourDictArr)     


            dstDictHourArr = []
            dateDstDictArr = []
            stormScoreDstDictArr = []

            for mhhd in dstHourDictArrUniq :
                dstThishour = nowDayDstVal[ numpy.where( dstHourDictArr == mhhd ) ]
                dateValthishour = nowDayDateVal[ numpy.where( dstHourDictArr == mhhd ) ]
                strmdstScoreThishour = 0

                if len(dstThishour) > 0:
                    dstDictHourArr.append( "%.2f"%min(dstThishour) )

                    if ( ( dstDictHourArr[-1] <= -15. ) & ( dstDictHourArr[-1] > -30. ) ) :
                        strmdstScoreThishour = 1.

                    if ( ( dstDictHourArr[-1] <= -30. ) & ( dstDictHourArr[-1] > -50. ) ) :
                        strmdstScoreThishour = 2.
                    
                    if ( dstDictHourArr[-1] < -50. ) :
                        strmdstScoreThishour = 3.

                if len(dateValthishour) > 0 :
                    dateDstDictArr.append( dateValthishour[0] )
                else :
                    dateDstDictArr.append( float('nan') )
                    print 'something off here!!! in dateDstDictArr'

                stormScoreDstDictArr.append( strmdstScoreThishour )

            dstDictHourArr = numpy.array(dstDictHourArr)
            dateDstDictArr = numpy.array(dateDstDictArr)
            stormScoreDstDictArr = numpy.array(stormScoreDstDictArr)

            # Now we have the required array stuff...
            # write it into a pyton dictionary object
            dstJsonDict = {}

            for j in range( len(dateDstDictArr) ) : 
                dateNow = dateDstDictArr[j]
                strKey = dateNow.strftime('%H%d%m%Y')
                strDateVal = dateNow.strftime('%d%m%Y')

                dstJsonDict.setdefault(strKey, []).append( strDateVal )
                dstJsonDict.setdefault(strKey, []).append( dateDstDictArr[j].hour )

                dstJsonDict.setdefault(strKey, []).append( dstDictHourArr[j] )
		dstJsonDict.setdefault(strKey, []).append( stormScoreDstDictArr[j] )
                

             # now we have the dictionary obj...so goto the function below
            # to write this stuff down into a json file
            # Sometimes may be the dict might not have any values....
            # dont call the function in that case...

            if len( dstJsonDict.keys() ) > 0 :
                popRtDstJson(dstJsonDict)

            
            
            # Get to the plotting part...
            fig = plt.figure(figsize = ( 11, 8.5 ) )
            ax = fig.gca()
            ax.plot_date( date_dst_arr,dst_val,'b-', linewidth = 2 )
            ax.plot_date( date_dst_50nT_arr,dst_val_50nT_arr,'r.', markersize = 10, label="Dst < -50nT " )
            ax.plot_date( date_dst_30nT_arr,dst_val_30nT_arr,'y.', markersize = 10, label="-50nt > Dst < -30nT "  )
            
            
            handles, labels = ax.get_legend_handles_labels()
            fontProp = mp.font_manager.FontProperties( size = 7.5 )
            ax.legend(handles[::-1], labels[::-1], bbox_to_anchor=(1., 0.95), loc = 1, prop = fontProp)
            
            
            # Annotate the date to show the date of latest data    
            last_good_dst_date = date_dst_arr[ -1 ]
            good_dst_last = dst_val[ -1 ]
            ax.annotate( str( last_good_dst_date.month )+ '/'+str( last_good_dst_date.day )+'-'+ str( last_good_dst_date.hour ) + 'UT', xy =( last_good_dst_date, good_dst_last ), size = 8 )
            
            Range_days_currmonth = monthrange(Today.year, Today.month)
            Xtk_dates = [datetime.datetime( Today.year, Today.month, 1, 0 ) , datetime.datetime( Today.year, Today.month, 5, 0 ) , datetime.datetime( Today.year, Today.month, 10, 0 ) , \
                         datetime.datetime( Today.year, Today.month, 15, 0 ) , datetime.datetime( Today.year, Today.month, 20, 0 ), datetime.datetime( Today.year, Today.month, 25, 0 ) , \
                         datetime.datetime( Today.year, Today.month, Range_days_currmonth[1], 23, 0 ) ]
            
            # Annotate dates in the cycle where we max deviations in dst
            count_add_pos = 0
            old_cr_xpos = 0
            
            date_dst_for_annotate = date_dst_arr[ numpy.where( dst_val < -30. ) ]
            dst_val_for_annotate = dst_val[ numpy.where( dst_val < -30. ) ]
            
            for a, b in zip( date_dst_for_annotate, dst_val_for_annotate ) :
                str_curr =str(a.month)+'/'+str(a.day)+"-"+str(a.hour)+" UT"
            
            
                for count_cr_dates in range( len( Xtk_dates ) ) :
                    if ( a >= Xtk_dates[ count_cr_dates ] and a <= Xtk_dates[ count_cr_dates + 1 ] ) :
                        xpos_dates = Xtk_dates[ count_cr_dates ] + datetime.timedelta( days = 1.5 )
                        new_cr_pos = count_cr_dates
                        break
            
            
                if ( new_cr_pos == old_cr_xpos and a != date_dst_for_annotate[0] ) :
                    count_add_pos = count_add_pos + 4
                else :
                    old_cr_xpos = new_cr_pos
                    count_add_pos = 0
                    
                this_color_date = 'y'    
                if b < -50. :
                    this_color_date = 'r'
                    
                 
                ax.annotate( str_curr, xy =( xpos_dates, -195 + count_add_pos ), size = 8, color = this_color_date )
                
                
            
            HMFmt = mp.dates.DateFormatter('%b,%d')
            xtickMins_minor = mp.dates.DayLocator(interval = 1)
            
            ax.xaxis.set_major_formatter(HMFmt)
            ax.xaxis.set_minor_locator(xtickMins_minor)
            
            
            plt.xticks(rotation=45,fontsize = 12 )
            plt.xlabel('Date', fontsize = 12)
            ax.set_xticks( Xtk_dates )
            ax.grid( color = 'gray', linestyle = 'dashed' )
            plt.ylabel('Dst Index [nT]',fontsize = 12 )
            plt.xlim(datetime.datetime( Today.year, Today.month, 1, 0 ), datetime.datetime( Today.year, Today.month, Range_days_currmonth[1], 23) )
            plt.ylim(-200, 50)
            plt.title('Dst Index - ' + Today.strftime("%B") + ' ' + str( Today.year ), fontsize = 15 )
            
            fig.savefig('/var/www/images/Gstrm/Dst-RT.pdf',orientation='portrait',papertype='a4',format='pdf')
            fig.savefig('/var/www/images/Gstrm/Dst-RT.jpeg',orientation='portrait',papertype='a4',format='jpeg')
            
            plt.close(fig)
            fig.clear()
            
            
            # We now have the plotting stuff....
            # We'll go for the looping thing and set this up as an alert
            
            DstVal_latest = dst_val[-1]
            DateDst_latest = date_dst_arr[-1]
            
            
            
            # For now we setup two scoring levels for storm time activity....1) Dst between -30 and -50 nT, 2) Dst < -50 nT
            
            now_email_time = datetime.datetime.today()
            diff_email_time = now_email_time - last_email_time
            last_mail_sent = 'no'
            Dst_storm_score_level = 0.
            
            if ( ( DstVal_latest <= -30. ) & ( DstVal_latest > -50. ) ) :
                Dst_storm_score_level = 1.
            
            if ( DstVal_latest < -50. ) :
                Dst_storm_score_level = 2.
            
                
            # Get to the mailing part    
            
            if ( Dst_storm_score_level == 1. ) :
                    Dst_subject = ' Dst Alert UPDATE : Dst val ' + str( DstVal_latest ) + 'nT : possibility of geomagnetic storm '    
                    text_send_sms = ' Dst Alert : Dst val ' + str( DstVal_latest ) + 'nT : possibility of geomagnetic storm '   
                    
                    text_send_mail = 'Possibility of geomagnetic storms currently'\
                    #+'\n'+'\n'+ ' Alert issued for Dst Value at ' + str( DateDst_latest ) + ' UT'\
                                    
                    
                    attach = "/var/www/images/Gstrm/Dst-RT.pdf"
                    
                    if ( Dst_storm_score_level > old_storm_score and nemails < 3 ) :
                        DstAlertCall( attach, text_send_mail, Dst_subject )
                        print 'sending mail..'
                        last_email_time = now_email_time
                        old_storm_score = Dst_storm_score_level
                        last_mail_sent = 'yes'
                        
                        
            elif ( Dst_storm_score_level == 2. ) :
                    Dst_subject = ' Dst UPDATE : Dst val ' + str( DstVal_latest ) + 'nT : Strong possibility of geomagnetic storm '    
                    text_send_sms = ' Dst UPDATE : Dst val ' + str( DstVal_latest ) + 'nT : Strong possibility of geomagnetic storm '   
                    
                    text_send_mail = 'Strong possibility of geomagnetic storms currently'\
                    +'\n'+'\n'+ ' Alert issued for Dst Value at ' + str( DateDst_latest ) + ' UT'\
                    
                    attach = "/var/www/images/Gstrm/Dst-RT.pdf"
                    
                    if ( Dst_storm_score_level > old_storm_score and nemails < 3 ) :
                        DstAlertCall( attach, text_send_mail, Dst_subject )
                        print 'sending mail..'
                        last_email_time = now_email_time
                        old_storm_score = Dst_storm_score_level
                        last_mail_sent = 'yes'         
                        
            print 'Dst : ', DstVal_latest, 'UT-TIME', last_good_dst_date,'new-score-',Dst_storm_score_level, 'old-score-', old_storm_score       
            
                      
            del dst_val, date_dst_arr, nowDayDateVal, nowDayDstVal, dstDictHourArr, dateDstDictArr, stormScoreDstDictArr, strmdstScoreThishour, dateValthishour, dstThishour, 
            ax.clear()
            
            return last_mail_sent, str( old_storm_score )
    else :
            last_mail_sent = 'no'
            return last_mail_sent, str( 0 )    
    


def popRtDstJson(dstJsonDict):
    # In the latest addition to spaceweather website we are taking the Dst information for a 24-hour period and storing it 
    # in a JSON file. This file is later used by Javascript to display the color bar indicating the geomagnetic and solar 
    # activity levels and they can be made a little interactive as well....like displaying the alert status and dst-index value
    # for the hour and the ACE activity 

    import os
    import json
    import datetime

    # always check if there is any default JSON file in there...
    # We are using this file as our JSON file

    jsonDstFileName = '/var/www/dstVal.json'
    
    # check if the Json file is already there
    checkDstJsonFile = os.path.isfile( jsonDstFileName )
    
    if ( checkDstJsonFile == True ) :
        # get the values already in the file
        with open(jsonDstFileName) as infile :
            oldDataJsonDst = json.load(infile)


        # Check if the data is for the current day else delete the data
        oldKeyVal = oldDataJsonDst.keys()
        oldKeyVal = oldKeyVal[0]

        newKeyVal = dstJsonDict.keys()
        newKeyVal = newKeyVal[0]

        if ( dstJsonDict[newKeyVal][0] != oldDataJsonDst[oldKeyVal][0] ) :
            allDataJsonDst = dstJsonDict
        else :       
            # del keys from old dict that are present in new dict
            # then append new dict to old dict
            for nke in dstJsonDict.keys() :
                if nke in oldDataJsonDst : del oldDataJsonDst[nke]

            allDataJsonDst = dict( oldDataJsonDst.items() + dstJsonDict.items() )


        # write this stuff in to the json file
        with open(jsonDstFileName, 'wb') as outfile:
            json.dump(allDataJsonDst, outfile)

    else :
        with open(jsonDstFileName, 'wb') as outfile:
            json.dump(dstJsonDict, outfile)


    
def DstAlertCall( attach, text, Dst_subject ) :    
    	
    import smtplib
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEBase import MIMEBase
    from email.MIMEText import MIMEText
    from email import Encoders
    import os
    
    gmail_user = "vt.sd.sw@gmail.com"
    gmail_pwd = "more ace"
    gmail_mail_to = [ "bharatr@vt.edu", "mikeruo@vt.edu", "bakerjb@vt.edu",  "kevintyler@vt.edu" , "pje@haystack.mit.edu", "phil.erickson@gmail.com", "nafrissell@vt.edu", "steve.kaeppler@gmail.com" ]

    
    msg = MIMEMultipart()
    
    msg['From'] = gmail_user
    msg['To'] = "bharatr@vt.edu"
    msg['Subject'] = Dst_subject
    
    msg.attach(MIMEText(text))
    
    part = MIMEBase('application', 'octet-stream')
    part.set_payload(open(attach, 'rb').read())
    Encoders.encode_base64(part)
    part.add_header('Content-Disposition',
           'attachment; filename="%s"' % os.path.basename(attach))
    msg.attach(part)
    
    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmail_user, gmail_pwd)
    mailServer.sendmail(gmail_user, gmail_mail_to, msg.as_string())
    mailServer.close()
    
    cmd_alert = "mplayer /usr/share/sounds/gnome/default/alerts/bark.ogg"
    cmd_op_file = "xdg-open /var/www/images/Gstrm/ACE-PAR-RT.pdf"
    
#    os.system( cmd_op_file )
    
    for brk in range( 5 ):
        check = os.popen( cmd_alert )
        check.read()
        check.close()
        
        

def DstRTRunDays():
	import time
	import datetime
	import urllib
	import matplotlib.pyplot as plt
	import matplotlib.gridspec as gridspec
	import math
	from time import gmtime, strftime
	import matplotlib
	
	while True:
		
		
		try :
			nemails
		except NameError :
			nemails = 0
		
		try :
			last_email_time
		except NameError :
			last_email_time = datetime.datetime( 2011, 1, 1 ) # Some old date so that when you start the code for the first time there wouldn't be initialization issues
			
		try :
			old_storm_score_stored
		except NameError :
			old_storm_score_stored = 0.
		
		now_email_time = datetime.datetime.today()
		diff_email_time = now_email_time - last_email_time
		print now_email_time
		

		# Reset the email clock back if it has been more than 24 hours since the last email...
    		# We are changing the email clock thingy when sending emails
		if ( diff_email_time.days >= 1 ) :
        		nemails = 0
        		last_email_time = datetime.datetime( 2011, 1, 1 )
        		old_storm_score_stored = 0.
			
		last_mail_yesno, storm_score_increase_check = DstRTRd( last_email_time = last_email_time, nemails = nemails, old_storm_score = old_storm_score_stored )
		
		if last_mail_yesno == 'yes' :
			 last_email_time = now_email_time
			 nemails = nemails + 1
			 old_storm_score_stored = float( storm_score_increase_check )
		
		time.sleep(1200)
        
