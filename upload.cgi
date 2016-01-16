#!/usr/bin/python

import os
import cgi
import sys
import shutil
import smtplib
import os.path

# set these
UPLOAD_DIR="/some/writable/but/not/web/accessible/dir"
UPLOAD_WATCHER="pj@place.org"
EMAIL_SENDER="pj@place.org"

# dont mess with anything below this line
print "Content-Type: text/html\n"   # HTML is following ; don't forget the extra newline

def askForFile(errormsg=""):
    if errormsg:
        errormsg = '\n<EM>'+errormsg+'</EM>\n<P>\n'
    print """
    <H1>Anonymous Upload</H1>
    %s
    <form enctype="multipart/form-data" method=post>
      Upload a file: <input type="file" name="userfile">
      <P>
      <input type="submit" value="Upload">
    </form>
    """ % (errormsg)

def sanitize(filename):
    # chop off everything up to the right-most '/' in the filename
    f = filename.split('/')[-1]
    f = f.split('\\')[-1]
    return f

def notifyByEmail(notifiee, filename):
    mailinfo = { 'from' : EMAIL_SENDER,
                 'to' : notifiee,
                 'filename': filename,
                 'client' : os.environ.get('REMOTE_ADDR',''),
                 'server' : os.environ.get('SERVER_NAME',''),
                 'script' : os.environ.get('SCRIPT_FILENAME', '')
               }

    if 'REMOTE_HOST' in os.environ:
        mailinfo['client'] = "%s (%s)" % (os.environ['REMOTE_HOST'], mailinfo['client'])

    msg = """From: %(from)s\r\nTo: %(to)s\r\nSubject: New file uploaded\r\n

File '%(filename)s' uploaded by %s

Just thought you should know!

...this message brought to you by the letter P, the number 5,
the server %(server)s and %(script)s

    """ % mailinfo

    server = smtplib.SMTP('localhost')
    server.sendmail(EMAIL_SENDER, (notifiee,), msg)
    server.quit()

# check if we have been given a file yet
form = cgi.FieldStorage()
if "userfile" not in form:
    askForFile()
else:
    fileitem = form["userfile"]
    if not fileitem.file:
        askForFile("File is of invalid type")
    else:
        # append the filename to the upload dir
        name = sanitize(fileitem.filename)
        filename = os.path.join(UPLOAD_DIR, name)

        # open the output file
        try:
            outfile = open(filename,"w")
        except IOError as e:
            print '''
                  <H1>Fatal Error</H1>
                  Can't open output file: %s
                  Contact the person you're uploading to with this message.
                  ''' %  str(e)
            sys.exit(1)

        # It's an uploaded file; keep from having to hold the entire thing in memory
        shutil.copyfileobj(fileitem.file, outfile)
        notifyByEmail(UPLOAD_WATCHER, filename)

    askForFile('Success! %s uploaded successfully!' % name)


