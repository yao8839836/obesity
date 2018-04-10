f = open('data/Obesity_data/ObesitySen_remove_familiy_history.dms','r')
content = f.read()
f.close()

records = content.strip().split('RECORD #')

for record in records:
    id = record[:record.find('\n')]
    if(record.find('[report_end]') != -1):
        str_to_write = record[record.find('\n') + 1: record.find('[report_end]')].strip()
        print(str_to_write)
        f_write = open('data/obesity_records_no_fam/'+ id +'.txt','w')
        f_write.write(str_to_write)
        f_write.close()