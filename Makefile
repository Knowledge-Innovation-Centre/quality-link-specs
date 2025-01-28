all: template.html data_exchange.html

%.html: %.bs
	bikeshed spec $< $@ && open $@

clean:
	rm *.html

