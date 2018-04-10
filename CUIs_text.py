f = open('data/CUIs_text_weng_no_fam.txt','w')

count = []
for i in range(1249):
    f_read = open('data/obesity_records_no_fam_cuis/'+ str(i+1)+'.txt.out','r')
    content = f_read.readlines()
    f_read.close()

    cuis = []
    for line in content:
        temp = line.split('|')
        if len(temp) >= 6:
            if (temp[5] == '[dsyn]' or temp[5] == '[bpoc]' or temp[5] == '[fndg]' or temp[5] == '[lbtr]' 
                or temp[5] == '[mobd]' or temp[5] == '[comd]' or temp[5] == '[lbpr]' or temp[5] == '[diap]' 
                or temp[5] == '[topp]' or temp[5] == '[phsu]' or temp[5] == '[bodm]'
                or temp[5] == '[bacs]' or temp[5] == '[sosy]') and temp[1] == 'MMI':
                print(temp[4])
                cuis.append(temp[4])
    string = ' '.join(cuis)
    if len(cuis) == 0:
       string = '<PAD>' 
    count.append(len(cuis))
    f.write(string + '\n')
print(max(count))
f.close()