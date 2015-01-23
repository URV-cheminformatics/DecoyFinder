import sip, os, sys

sip.setapi(u'QDate', 2)
sip.setapi(u'QDateTime', 2)
sip.setapi(u'QString', 2)
sip.setapi(u'QTextStream', 2)
sip.setapi(u'QTime', 2)
sip.setapi(u'QUrl', 2)
sip.setapi(u'QVariant', 2)


os.environ['BABEL_DATADIR'] = sys._MEIPASS
os.environ['BABEL_LIBDIR'] = sys._MEIPASS
#%_MEIPASS2% is the directory where the package is decompressed and where all libraries and data are.
os.environ['PATH'] =  sys._MEIPASS + os.pathsep + os.environ['PATH']
print 'BABEL_DATADIR set to ', os.environ['BABEL_DATADIR']
