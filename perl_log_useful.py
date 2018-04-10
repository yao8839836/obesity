### intuitive ###
nfile = open('perl_classifier/intuitive/negated.log','r')
content = nfile.read()
nfile.close()
lines = content.split('\n')

# keep only + in intuitive/negated.log
f_truly_usful = open('perl_classifier/intuitive/negated_truly_useful.log','w')
for line in lines:
    if(line.find("+") == 0):
        f_truly_usful.write(line + '\n')
f_truly_usful.close()

qfile = open('perl_classifier/intuitive/questionable.log','r')
content = qfile.read()
qfile.close()
lines = content.split('\n')

# keep only + in intuitive/questionable.log

f_truly_usful = open('perl_classifier/intuitive/questionable_truly_useful.log','w')
for line in lines:
    if(line.find("+") == 0):
        f_truly_usful.write(line + '\n')
f_truly_usful.close()                             
                             

pfile = open('perl_classifier/intuitive/positive.log','r')
content = pfile.read()
pfile.close()
lines = content.split('\n')

# keep only + in intuitive/positive.log
f_useful = open('perl_classifier/intuitive/positive_useful.log','w')
for line in lines:
    if(line.find('+') == 0):
        f_useful.write(line + '\n')
f_useful.close()


### textual ###
nfile = open('perl_classifier/textual/negated.log','r')
content = nfile.read()
nfile.close()
lines = content.split('\n')

# keep only + in textual/negated.log
f_truly_usful = open('perl_classifier/textual/negated_truly_useful.log','w')
for line in lines:
    if(line.find("+") == 0):
        f_truly_usful.write(line + '\n')
f_truly_usful.close()

qfile = open('perl_classifier/textual/questionable.log','r')
content = qfile.read()
qfile.close()
lines = content.split('\n')

# keep only + in textual/questionable.log
f_truly_usful = open('perl_classifier/textual/questionable_truly_useful.log','w')
for line in lines:
    if(line.find("+") == 0):
        f_truly_usful.write(line + '\n')
f_truly_usful.close()                             
                             

pfile = open('perl_classifier/textual/positive.log','r')
content = pfile.read()
pfile.close()
lines = content.split('\n')

# keep only + in textual/positive.log
f_useful = open('perl_classifier/textual/positive_useful.log','w')
for line in lines:
    if(line.find('+') == 0):
        f_useful.write(line + '\n')
f_useful.close()
