## globals

#RECORDS = ./orig/obesity_patient_records_training.xml
RECORDS = input/records.xml
#TEXTUAL_ANNOTATIONS = all_textual_annotations.xml
#INTUITIVE_ANNOTATIONS = all_intuitive_annotations.xml

TEXTUAL_ANNOTATION_TEMPLATE   = input/textual_annotation_template.xml
INTUITIVE_ANNOTATION_TEMPLATE = input/intuitive_annotation_template.xml

TEXTUAL_OUTPUT   = output/system_textual_annotation.xml
INTUITIVE_OUTPUT = output/system_intuitive_annotation.xml

RESULTS_HTML_OUTPUT = output/results.html


## includes

include Makefile.textual
include Makefile.intuitive


## human readable output

${RESULTS_HTML_OUTPUT}: i2b2html.pl de_abbrev.pl
	cat ${RECORDS} \
	| ./de_abbrev.pl \
	| ./i2b2html.pl \
		${TEXTUAL_OUTPUT} \
		${INTUITIVE_OUTPUT} \
	| perl -W -p \
	-e '$$r += (s/(D[rR]s?\.?(([ ,\n]+[A-Z]([a-z]+|\.?))+|([ ,\n]+[A-Z]([A-Z]+|\.?))+)|((([A-Z]([A-Z]*|[a-z]*|\.))[ \n,]+)+(M\.D\.?|MD)( , PH\.D\.)?))/<span class="doctor_name">$$1<\/span>/g);' \
	-e 'BEGIN{$$r=0;} END{ print STDERR "$$r doctor names replaced\n";}' \
	| perl -W -p \
	-e '$$r += (s/((Mr|Mrs|Ms)\.?([ \n][A-Z]([a-z]+|\.?))+)/<span class="patient_name">$$1<\/span>/g);' \
	-e 'END{ print STDERR "$$r patient names replaced\n"; } BEGIN{$$r=0;} ' \
	> $@

## all

all: ${TEXTUAL_OUTPUT} ${INTUITIVE_OUTPUT} ${RESULTS_HTML_OUTPUT} 


## validate

eval:
	java -jar evaluation/evaluation.jar \
		all_textual_annotations.xml \
		res_textual.xml
