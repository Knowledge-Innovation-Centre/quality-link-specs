all: template.html data_exchange.html discovery.html

%.html: %.bs
	bikeshed spec $< $@ && open $@

clean:
	rm *.html

