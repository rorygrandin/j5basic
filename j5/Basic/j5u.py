from j5.Database import MailImport
import sys
from email import utils
importer = MailImport.pop3importer(None)
j5u = open(sys.argv[1],'r')
j5utext = j5u.read()
j5u.close()
key = '65537,155450449298717211500593304271216493957586778598025892751649425759952939380863768841830321776765999783199153510383026935646312436967551033099627352940306269731001608473496556689686520769410508727384281543319503980813795260103039786526663894227305994508708309294021136700002021264196068620494907614439056781853'
components = j5utext.split('|')
print components[1]
print components[2]
decryptedtext = importer.decrypt_file(components[0], components[1], components[2], key)
file = open('testing.zip','wb')
file.write(decryptedtext)
file.close()
print 'done'