import xml.etree.ElementTree as et
import xml.dom.minidom as Dom

f = open('data/Obesity_data/Obesity1.dms','r')
content = f.read()
f.close()

doc = Dom.Document() 
docs_node = doc.createElement("root")
doc.appendChild(docs_node)

records = content.strip().split('RECORD #')
corpus = []
for record in records:
    if(record.find('[report_end]') != -1):
        record_content = record[record.find('\n') + 1: record.find('[report_end]')].strip()
        corpus.append(record_content)
        id = record[:record.find('\n')]
        doc_node = doc.createElement("doc")
        doc_node.setAttribute("id", id)
        text_node =  doc.createElement("text")
        text_node_text = doc.createTextNode('\n' + record_content + '\n')
        text_node.appendChild(text_node_text)
        doc_node.appendChild(text_node)
        docs_node.appendChild(doc_node)
print(len(corpus))
f = open('perl_classifier/input/records_1.xml','w')
f.write(doc.toprettyxml(indent = "", newl = "\n", encoding = "utf-8")) 
f.close()