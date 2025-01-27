all: template.html

%.html: %.bs
	bikeshed spec $< $@ && open $@

clean:
	rm *.html

