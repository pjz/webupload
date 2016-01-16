#!/usr/bin/python

import os
import cgi
import sys
import shutil
import string
import smtplib

# set these
uploaddir="/some/writable/but/not/web/accessible/dir"
uploadwatcher="pj@place.org"
emailfrom="pj@place.org"

# dont mess with anything below this line
print "Content-Type: text/html"     # HTML is following
print                               # blank line, end of headers

def askForFile(errormsg=""):
    print "<H1>Anonymous Upload</H1>"
    if errormsg:
        print '<EM>'+errormsg+'</EM>\n<P>\n'
    print '<form enctype="multipart/form-data" method=post>\n'
    print 'Upload a file: <input type="file" name="userfile">'
    print '<P>'
    print '<input type="submit" value="Upload">'
    print "</form>"
    return

def sanitize(filename):
    # chop off everything up to the right-most '/' in the filename
    f = filename
    r = string.rfind(f, '/') + 1
    if r > 0:
       f = filename[r:]
    r = string.rfind(f, '\\') + 1
    if r > 0:
       f = filename[r:]
    return f

def notifyByEmail(notifiee, filename):
    fromaddr = "pj@place.org"
    toaddrs = notifiee
    client = os.environ['REMOTE_ADDR']
    if os.environ.has_key('REMOTE_HOST'):
        client = "%s (%s)" % (os.environ['REMOTE_HOST'], client)

    msg = """From: %s\r\nTo: %s\r\nSubject: New file uploaded\r\n

File '%s' uploaded by %s

Just thought you should know!

...this message brought to you by the letter P, the number 5,
the server %s and %s

    """ % (fromaddr,
           toaddrs,
           filename,
           client,
           os.environ['SERVER_NAME'],
           os.environ['SCRIPT_FILENAME'])

    server = smtplib.SMTP('localhost')
    server.sendmail(fromaddr, (toaddrs,), msg)
    server.quit()

# check if we have been given a file yet
form = cgi.FieldStorage()
if not form.has_key("userfile"):
    askForFile()
else:
    fileitem = form["userfile"]
    if not fileitem.file:
        askForFile("File is of invalid type")
    else:
        # append the filename to the upload dir
        name = sanitize(fileitem.filename)
        filename = uploaddir + '/' + name

        # open the output file
        try:
            outfile = open(filename,"w")
        except:
            print '''
                  <H1>Fatal Error</H1>
                  Can't open output file.
                  Contact the person you're uploading to with this message.
                  '''
            sys.exit(0)

        fileitem = form["userfile"]
        # It's an uploaded file; keep from having to hold the entire thing in memory
	shutil.copyfileobj(fileitem.file, outfile)
	notifyByEmail(uploadwatcher, filename)

    askForFile('Success! %s uploaded successfully!' % name)


