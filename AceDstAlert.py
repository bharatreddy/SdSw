import datetime


def AceDstRd( last_email_time = datetime.datetime.today(), nemails = 0, old_storm_score = 0. ) :

    
    import time
    import datetime
    import urllib
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    import math
    from time import gmtime, strftime
    import matplotlib
    import urllib2
    import re

    # Files to be downloaded and read

    url_acesw = 'http://www.swpc.noaa.gov/ftpdir/lists/ace/ace_swepam_1m.txt'
    url_acemag = 'http://www.swpc.noaa.gov/ftpdir/lists/ace/ace_mag_1m.txt'
    file_acesw = '/home/bharat/Desktop/file_acesw.txt'
    file_acemag = '/home/bharat/Desktop/file_acemag.txt'

    
# First check if the files exist...then proceed otherwise quit    
 
    check_url_acemag_exist = 'no'
    check_url_acesw_exist = 'no'
    try:
       urllib2.urlopen(url_acemag)
       check_url_acemag_exist = 'yes'
    except urllib2.HTTPError, e:
       print e.code
       check_url_acemag_exist = 'no'
    except urllib2.URLError, e:
       print e.args
       check_url_acemag_exist = 'no'
       
    try:
       urllib2.urlopen(url_acesw)
       check_url_acesw_exist = 'yes'
    except urllib2.HTTPError, e:
       print e.code
       check_url_acesw_exist = 'no'
    except urllib2.URLError, e:
       print e.args
       check_url_acesw_exist = 'no'   


    urllib.urlretrieve(url_acesw,file_acesw)
    urllib.urlretrieve(url_acemag,file_acemag)

    fff_mag = open(file_acemag)
    fff_sw = open(file_acesw)
    liness_mag = fff_mag.readlines()
    liness_sw = fff_sw.readlines()
    fff_mag.close()
    fff_sw.close()

    # Sometimes urlopen (above) doesn't give an error even though
    # the file is not downloaded thats why before doing any operations 
    # I'll search for pattern "not found" in the file
    # The presence of such pattern indicates the file is not downloaded...
    pattern = "not found" 

    for lmag in liness_mag :
        cmag = re.search( pattern, lmag )
        #print lmag
        if cmag :
           check_url_acemag_exist = 'no'
           break

    for lsw in liness_sw :
        csw = re.search( pattern, lsw )
        #print lsw
        if csw :
           check_url_acesw_exist = 'no'
           break

 
    
    if (check_url_acemag_exist == 'yes' and check_url_acesw_exist == 'yes' ) :
       
        
        # open the files...loop through them and read data into arrays
        # start with the swepam files...
        f_acesw = open(file_acesw, 'r')
        
        for line in range(0,18):
            header = f_acesw.readline()
        
        np_sw=[]
        vt_sw=[]
        time_sw=[]
    
        
        for line in f_acesw:
            line = line.strip()
            columns = line.split()
        
            hh_sw = int(int(columns[3])/100)
            mm_sw = int(int(columns[3]) % 100)
            time_sw.append(datetime.datetime(int(columns[0]), int(columns[1]), int(columns[2]), hh_sw, mm_sw))
        
            # check for garbage values in the data
            if abs(float(columns[7])) > 100.:
                columns[7] = float('nan')
        
            if abs(float(columns[8])) > 2000.:
                columns[8] = float('nan')
        
            np_sw.append(float(columns[7]))
            vt_sw.append(float(columns[8]))
        
        f_acesw.close()
        
        # Now the mag files...
        f_acemag = open(file_acemag, 'r')
        
        for line in range(0,20):
            header = f_acemag.readline()
        
        
        Bx_mag=[]
        By_mag=[]
        Bz_mag=[]
        time_mag=[]
    
       
        
        for line in f_acemag:
            line = line.strip()
            columns = line.split()
        
            hh_mag = int(int(columns[3])/100)
            mm_mag = int(int(columns[3]) % 100)
            time_mag.append(datetime.datetime(int(columns[0]), int(columns[1]), int(columns[2]), hh_mag, mm_mag))
        
        
            # check for garbage values in the data
            if abs(float(columns[7])) > 100.:
                columns[7] = float('nan')
        
            if abs(float(columns[8])) > 100.:
                columns[8] = float('nan')
        
            if abs(float(columns[9])) > 100.:
                columns[9] = 0.#float('nan')
        
            Bx_mag.append(float(columns[7]))
            By_mag.append(float(columns[8]))
            Bz_mag.append(float(columns[9]))
        
        
        f_acemag.close()
        
        

        cur_UT_year = strftime("%Y", gmtime())
        cur_UT_mon = strftime("%m", gmtime())
        cur_UT_day = strftime("%d", gmtime())
        cur_UT_hour = strftime("%H", gmtime())
        
 
        Ey_IMF_Bz = []
        Boyle_Index = []
        Time_Par = []
        Kp_Boyle = []
        Pdyn = []
            
        # Notes :
        # Boyle index above 100 indicates the presence of geomagnetic activity...
        
        for tmg, tsw, vs, np, bz, by, bx  in zip( time_mag, time_sw, vt_sw, np_sw, Bz_mag, By_mag, Bx_mag ):
            if ( tmg.hour == tsw.hour and tmg.min == tsw.min and abs(bz) > 0. ) :
                Time_Par.append( tmg )

                Ey_IMF_Bz.append( -1 * vs * 1000 * bz * 1e-9 * 1e3) # This is in mV/m
                Pdyn.append( 1.6726e-6 * np * math.pow( vs, 2 ) )
                Bt = math.sqrt( math.pow( bz, 2) + math.pow( by, 2 ) + math.pow( bx, 2 ) )
                btheta = math.acos( bz / Bt )
                Boyle_Index.append( 1e-4* math.pow( vs, 2 ) + 11.7*Bt*math.pow( math.sin(btheta/2), 3 ) ) # This is in kV ...
                Kp_Boyle.append( 8.93*math.log10( Boyle_Index[-1] ) - 12.55 )

    
       
        # For plotting the time axis (x-axis) we need to get the nearest hour to the last available data...
        # like do some round of stuff .... also need to mark the time of latest downloaded data


        axLabelStartTime = Time_Par[0]
        checkEndTimeLab = Time_Par[-1] 
        
        if (checkEndTimeLab.minute < 30) :
            axLabelEndTime = datetime.datetime(checkEndTimeLab.year,checkEndTimeLab.month,checkEndTimeLab.day, checkEndTimeLab.hour,0,0) + datetime.timedelta( hours = 1 )
        else :
            axLabelEndTime = datetime.datetime(checkEndTimeLab.year,checkEndTimeLab.month,checkEndTimeLab.day, checkEndTimeLab.hour,0,0) + datetime.timedelta( hours = 2 )
        

        
        #	set the format of the ticks -- major ticks are set for 0,15,30,45 and 60th mins of the hour
        #	minor ticks are set every 5 min.
        xtickHours = matplotlib.dates.HourLocator()
        xtickMins_major = matplotlib.dates.MinuteLocator(byminute=range(0,60,30))
        xtickMins_minor = matplotlib.dates.MinuteLocator(byminute=range(0,60,10))
        
        HMFmt = matplotlib.dates.DateFormatter('%H:%M')
        
        #Plot the ACE data
        
        fig = plt.figure()
        
        ax = fig.add_subplot(511)
        ax.plot(time_mag,Bz_mag,label='Bz_GSM',color='r')
        ax.plot([axLabelStartTime, axLabelEndTime],[0,0],color='0.75',linestyle='--')
        ax.plot(time_mag,By_mag,label='By_GSM',color='b',linestyle='--')

        # Need to mark the time when the list was last updated
        ax.plot([time_mag[-1], time_mag[-1]],[-10,10],color='0.75',linestyle='--')
        
        #format the ticks
        ax.xaxis.set_major_formatter(HMFmt)
        ax.xaxis.set_major_locator(xtickMins_major)
        ax.xaxis.set_minor_locator(xtickMins_minor)
        ax.set_xticklabels([])
        
        #	set the labels for the plots
        plt.ylabel('IMF [nT]', fontsize=7.5)
        plt.yticks( fontsize=4.5 )
        plt.axis([axLabelStartTime,axLabelEndTime,-10.,10.])
        plt.title('REAL TIME ACE DATA : '+str(datetime.datetime.date(time_mag[-1])))
        plt.legend(loc=3,prop={'size':5},shadow=True,fancybox=True)
        
        
        #Plot the solarwind velocity data
        
        ax2 = fig.add_subplot(512)
        ax2.plot(time_sw,vt_sw,color='r')
        
        # Need to mark the time when the list was last updated
        ax2.plot([time_mag[-1], time_mag[-1]],[200.,700.],color='0.75',linestyle='--')

        
        #format the ticks
        ax2.xaxis.set_major_formatter(HMFmt)
        ax2.xaxis.set_major_locator(xtickMins_major)
        ax2.xaxis.set_minor_locator(xtickMins_minor)
        ax2.set_xticklabels([])
        
        plt.ylabel('SW.Vel [km/s]', fontsize=7.5)
        plt.yticks( fontsize=4.5 )
        plt.axis([axLabelStartTime,axLabelEndTime,200.,700.])
        
        
        
        #Plot the solarwind Proton Density data
        
        ax3 = fig.add_subplot(513)
        ax3.plot(time_sw,np_sw,color='r')
        
        # Need to mark the time when the list was last updated
        ax3.plot([time_mag[-1], time_mag[-1]],[0.01,100.],color='0.75',linestyle='--')
        
        #format the ticks
        ax3.xaxis.set_major_formatter(HMFmt)
        ax3.xaxis.set_major_locator(xtickMins_major)
        ax3.xaxis.set_minor_locator(xtickMins_minor)
        ax3.set_xticklabels([])
        ax3.set_yscale('log')
        
        #	set the labels for the plots
        plt.ylabel('Np [p/cc]', fontsize=7.5)
        plt.yticks( fontsize=4.5 )
        plt.axis([axLabelStartTime,axLabelEndTime,0.,100.])
        
        
        
        # Plot the parameters derived from ACE
        
        ax4 = fig.add_subplot(514)
        ax4.plot_date( Time_Par, Boyle_Index, 'r-' )

        # Need to mark the time when the list was last updated
        ax4.plot([time_mag[-1], time_mag[-1]],[0,200],color='0.75',linestyle='--')
        
        ax4.xaxis.set_major_formatter(HMFmt)
        ax4.xaxis.set_major_locator(xtickMins_major)
        ax4.xaxis.set_minor_locator(xtickMins_minor)
        ax4.set_xticklabels([])
        
        #	set the labels for the plots
        plt.ylabel('Boyle-Index [kV]', fontsize=7.5)
        plt.yticks( fontsize=4.5 )
        plt.axis([axLabelStartTime,axLabelEndTime,0.,200.])
        
        ax5 = fig.add_subplot(515)
        ax5.plot_date(Time_Par,Kp_Boyle,'r-')
        
        # Need to mark the time when the list was last updated
        ax5.plot([time_mag[-1], time_mag[-1]],[0.,9.],color='0.75',linestyle='--')
        
        #format the ticks
        ax5.xaxis.set_major_formatter(HMFmt)
        ax5.xaxis.set_major_locator(xtickMins_major)
        ax5.xaxis.set_minor_locator(xtickMins_minor)
        ax5.xaxis.set_minor_locator(xtickMins_minor)
        
        plt.ylabel('Est. Kp', fontsize=7.5)
        plt.axis([axLabelStartTime,axLabelEndTime,0.,9.])
        plt.yticks( [0, 3, 6, 9], fontsize=4.5 )
        plt.xlabel('Time (UT)')
        plt.xticks( rotation = 25 )
 
       
        
        #fig.savefig('/home/bharat/Desktop/ACE-PAR-RT.pdf',orientation='portrait',papertype='a4',format='pdf')
        #fig.savefig('/home/bharat/Desktop/ACE-PAR-RT.jpeg',orientation='portrait',papertype='a4',format='jpeg')
        fig.savefig('/var/www/images/Gstrm/ACE-PAR-RT.pdf',orientation='portrait',papertype='a4',format='pdf')
        fig.savefig('/var/www/images/Gstrm/ACE-PAR-RT.jpeg',orientation='portrait',papertype='a4',format='jpeg')
        plt.close(fig)
        fig.clear()
        
        
        # Now for knowing if there is a storm going on..
        # Get the latest good values of all the parameters...
        for kb in Kp_Boyle[ ::-1 ] :
            if not math.isnan( kb ) :
                Kp_Boyle_latest = kb
                break
        
        for bi in Boyle_Index[ ::-1 ] :
            if not math.isnan( bi ) :
                Boyle_Index_latest = bi
                break        
        
                
        for bz,tm in zip( Bz_mag[ ::-1 ], time_mag[::-1] ) :
            if ( abs(bz) > 0. ) :
                Bz_mag_latest = bz
                Time_mag_latest = tm
                break
        
                
        for by in By_mag[ ::-1 ] :
            if not math.isnan( by ) :
                By_mag_latest = by
                break
                
        for vss in vt_sw[ ::-1 ] :
            if not math.isnan( vss ) :
                vt_sw_latest = vss
                break
        
                
        for npp in np_sw[ ::-1 ] :
            if not math.isnan( npp ) :
                np_sw_latest = npp
                break        

        
        
        diff_last_latest_time = time_mag[-1] - Time_mag_latest
        
        
        # Storm predictions...
        # We have new Mike's alert status messages
        # These depend on three things --> Bz, Vsw and Np
        # set up a zero score level (variable -> storm_score_level) to begin with
        # When Bz < -10. then add 1 to score
        # When Vsw > 500. then add 1 to score
        # When Np > 10. then add 1 to score
        # When score = 3, red alert
        # When score = 2, orange alert
        # When only Bz < -10., yellow alert
        # Rest of the times consider quiet conditions
        
        now_email_time = datetime.datetime.today()
        diff_email_time = now_email_time - last_email_time
        last_mail_sent = 'no'
        storm_score_level = 0
        
        if ( Bz_mag_latest <= -10. ) :
		storm_score_level = storm_score_level + 1

        if ( vt_sw_latest >= 500. ) :
		storm_score_level = storm_score_level + 1
		
        if ( np_sw_latest >= 10. ) :
		storm_score_level = storm_score_level + 1
		
		

	if ( storm_score_level == 3. ) :
		ace_subject = ' ACE UPDATE : RED ALERT - Strong possibility of geomagnetic storm '

		text_send_mail = 'ACE Current Conditions : '+' 1) Bz = '+str( Bz_mag_latest )+', 2) By = '+str( By_mag_latest )+', 3) SW.Vel = '+str( vt_sw_latest )+', 4) Np = '+str( np_sw_latest )\
		+'\n'+'\n'+' *** Red Alert Issued *** at ' + str( datetime.datetime.utcnow() ) + ' UT'\
		+'\n'+'\n'+' Notes on alert levels : '\
		+'\n'+' Conditions for issuing a ~1 hour warning of potential for geophysical activity based on real-time ACE data : '\
		+'\n'+' 1) Bz < -10 nT,     2) Vsw > 500 km/s,       3) Np > 10/cc '\
		'\n'+' Yellow alert : One Criterion satisfied'\
		'\n'+' Orange alert : Two out of three criteria satisfied'\
		'\n'+' Red alert : All three criteria satisfied'
		
		
            	text_send_sms = 'ACE - RED Alert - Current Conditions : '+' Bz = '+str( Bz_mag_latest )+' By = '+str( By_mag_latest )+' SW.Vel = '+str( vt_sw_latest )+' Np = '+str( np_sw_latest )
            	
		attach = "/var/www/images/Gstrm/ACE-PAR-RT.pdf"
            	if ( ( diff_email_time.seconds / 60. > 180. and nemails < 2 and storm_score_level == old_storm_score) or ( diff_email_time.seconds / 60. > 5. and storm_score_level > old_storm_score and nemails < 4) ) :
                #send the email
                	AceDstAlertCall( attach, text_send_mail, ace_subject )
                	#AceAlertSms( 'ACE Space weather update - Red Alert : check email for details' )
                	AceAlertSms( text_send_sms )
                	print 'sending mail..'
                	last_email_time = now_email_time
                	old_storm_score = storm_score_level
                	last_mail_sent = 'yes'
                	
                	
	elif ( storm_score_level == 2. ) :
		ace_subject = ' ACE UPDATE : Orange ALERT - Possibility of geomagnetic storm '
		
		text_send_mail = 'ACE Current Conditions : '+' 1) Bz = '+str( Bz_mag_latest )+', 2) By = '+str( By_mag_latest )+', 3) SW.Vel = '+str( vt_sw_latest )+', 4) Np = '+str( np_sw_latest )\
		+'\n'+'\n'+' *** Orange Alert Issued *** at ' + str( datetime.datetime.utcnow() ) + ' UT'\
		+'\n'+'\n'+' Notes on alert levels : '\
		+'\n'+' Conditions for issuing a ~1 hour warning of potential for geophysical activity based on real-time ACE data : '\
		+'\n'+' 1) Bz < -10 nT,     2) Vsw > 500 km/s,       3) Np > 10/cc '\
		'\n'+' Yellow alert : One Criterion satisfied'\
		'\n'+' Orange alert : Two out of three criteria satisfied'\
		'\n'+' Red alert : All three criteria satisfied'		
		
		text_send_sms = 'ACE - Orange Alert - Current Conditions : '+' Bz = '+str( Bz_mag_latest )+' By = '+str( By_mag_latest )+' SW.Vel = '+str( vt_sw_latest )+' Np = '+str( np_sw_latest )
            	
            	attach = "/var/www/images/Gstrm/ACE-PAR-RT.pdf"
		if ( ( diff_email_time.seconds / 60. > 180. and nemails < 2 and storm_score_level == old_storm_score) or ( diff_email_time.seconds / 60. > 5. and storm_score_level > old_storm_score and nemails < 4) ) :
	#send the email
			AceDstAlertCall( attach, text_send_mail, ace_subject )
			#AceAlertSms( 'ACE Space weather update - Orange Alert : check email for details' )
			AceAlertSms( text_send_sms )
			print 'sending mail..'
			last_email_time = now_email_time
			old_storm_score = storm_score_level
			last_mail_sent = 'yes'
			
			
	elif ( Bz_mag_latest <= -10. ) :
		ace_subject = ' ACE UPDATE : Yellow ALERT - Possibility of substorms/storms '

		
		text_send_mail = 'ACE Current Conditions : '+' 1) Bz = '+str( Bz_mag_latest )+', 2) By = '+str( By_mag_latest )+', 3) SW.Vel = '+str( vt_sw_latest )+', 4) Np = '+str( np_sw_latest )\
		+'\n'+'\n'+' *** Yellow Alert Issued *** at ' + str( datetime.datetime.utcnow() ) + ' UT'\
		+'\n'+'\n'+' Notes on alert levels : '\
		+'\n'+' Conditions for issuing a ~1 hour warning of potential for geophysical activity based on real-time ACE data : '\
		+'\n'+' 1) Bz < -10 nT,     2) Vsw > 500 km/s,       3) Np > 10/cc '\
		'\n'+' Yellow alert : One Criterion satisfied'\
		'\n'+' Orange alert : Two out of three criteria satisfied'\
		'\n'+' Red alert : All three criteria satisfied'
		
		text_send_sms = 'ACE - Yellow Alert - Current Conditions : '+' Bz = '+str( Bz_mag_latest )+' By = '+str( By_mag_latest )+' SW.Vel = '+str( vt_sw_latest )+' Np = '+str( np_sw_latest )
		
		attach = "/var/www/images/Gstrm/ACE-PAR-RT.pdf"
		if ( ( diff_email_time.seconds / 60. > 180. and nemails < 2 and storm_score_level == old_storm_score) or ( diff_email_time.seconds / 60. > 5. and storm_score_level > old_storm_score and nemails < 4) ) :
	#send the email
			AceDstAlertCall( attach, text_send_mail, ace_subject )
			#AceAlertSms( 'ACE Space weather update - Yellow Alert : check email for details' )
			AceAlertSms( text_send_sms )
			print 'sending mail..'
			last_email_time = now_email_time
			old_storm_score = storm_score_level
			last_mail_sent = 'yes'
        
                        
        else :
            ace_subject = ' ACE UPDATE : Quiet conditions '
            text_send_mail = 'Current Condition : '+' Bz = '+str( Bz_mag_latest )+' By = '+str( By_mag_latest )+' SW.Vel = '+str( vt_sw_latest )+' Np = '+str( np_sw_latest ) \
            +' Yellow alert : Bz <= -10 nT, Orange alert : Two out of the three condidions are satisfied ( Bz < -10nT, Vsw > 500 km/s, Np > 10 /cc ), Red Alert : All three criteria are satisfied'
            
            text_send_sms = 'Quiet Conditions - Current Condition : '+' Bz = '+str( Bz_mag_latest )+' By = '+str( By_mag_latest )+' SW.Vel = '+str( vt_sw_latest )+' Np = '+str( np_sw_latest )
            
            gmail_mail_to = [ "bharatr@vt.edu" , "mikeruo@vt.edu" ]
            attach = "/var/www/images/Gstrm/ACE-PAR-RT.pdf"
               
   
        Dst_val = []
        datime_Dst = []
        Est_Dst_Val = []
        Est_Dst_Time = []
 	
 	
 	print  'Bz-',Bz_mag_latest, 'Np-',np_sw_latest, 'Vsw-',vt_sw_latest, 'new-score-',storm_score_level, 'old-score-', old_storm_score
 	
        del np_sw, vt_sw, time_sw, Bx_mag, By_mag, Bz_mag, Dst_val, datime_Dst, Ey_IMF_Bz, Boyle_Index, Time_Par, Kp_Boyle, Pdyn, Est_Dst_Val, Est_Dst_Time, 
        ax.clear()
        ax2.clear()
        ax3.clear()
        ax4.clear()
        ax5.clear()
       # ax6.clear()
        
        return last_mail_sent, str( old_storm_score )
     
    else :
	last_mail_sent = 'no'
	return last_mail_sent, str( 0 )
    
       
            
            

def AceDstAlertCall( attach, text, ace_subject ) :
	
    import smtplib
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEBase import MIMEBase
    from email.MIMEText import MIMEText
    from email import Encoders
    import os
    
    gmail_user = "vt.sd.sw@gmail.com"
    gmail_pwd = "more ace"
    gmail_mail_to = [ "bharatr@vt.edu", "mikeruo@vt.edu", "bakerjb@vt.edu",  "kevintyler@vt.edu", "pje@haystack.mit.edu", "phil.erickson@gmail.com", "nafrissell@vt.edu", "steve.kaeppler@gmail.com" ]
#    ace_subject = "ACE UPDATES"
#    text = "TESTING ACE UPDATE MECHANISM"
#    attach = "/home/bharat/Desktop/ACE-PAR-RT.pdf"
#    gmail_mail_to = [ "bharatr@vt.edu"  ]
    
    msg = MIMEMultipart()
    
    msg['From'] = gmail_user
    msg['To'] = "bharatr@vt.edu"
    msg['Subject'] = ace_subject
    
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
        
        
        
def AceAlertSms( sms_text ) :
    import smtplib
    
    
    sms_gmail_user = 'vt.sd.sw@gmail.com'
    sms_gmail_pwd = 'more ace'
    
    
    server = smtplib.SMTP( 'smtp.gmail.com', 587 )
    server.starttls()
    server.login( sms_gmail_user, sms_gmail_pwd )
    server.sendmail( sms_gmail_user, '9785492138@text.wireless.alltel.com', sms_text )


	
def AceDstRunDays():
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
			
		last_mail_yesno, storm_score_increase_check = AceDstRd( last_email_time = last_email_time, nemails = nemails, old_storm_score = old_storm_score_stored )
		
		if last_mail_yesno == 'yes' :
			 last_email_time = now_email_time
			 nemails = nemails + 1
			 old_storm_score_stored = float( storm_score_increase_check )
		
		time.sleep(60)
