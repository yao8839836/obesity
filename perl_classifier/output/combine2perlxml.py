f = open('system_intuitive_annotation.xml','r')
content = f.read()
f.close()
intuitive_lines = content.split('\n')

f = open('system_textual_annotation.xml','r')
content = f.read()
f.close()
textual_lines = content.split('\n')

combined = textual_lines[0:-2] + intuitive_lines[2:-2] + textual_lines[-2:]

f = open('perl_annotation6.xml', 'wb+')
string = '\n'.join(combined)
f.write(string)
f.close()