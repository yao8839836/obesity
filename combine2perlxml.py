f = open('perl_classifier/output/prod_134_0_5.xml','r')
content = f.read()
f.close()
intuitive_lines = content.split('\n')

f = open('perl_classifier/output/prod_134_0_2.xml','r')
content = f.read()
f.close()
textual_lines = content.split('\n')

combined = textual_lines[0:-2] + intuitive_lines[2:-2] + textual_lines[-2:]

f = open('perl_classifier/output/perl_annotation_as_paper.xml', 'wb+')
string = '\n'.join(combined)
f.write(string)
f.close()