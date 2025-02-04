all: template.html data_exchange.html discovery.html policy.html

%.html: %.bs
	bikeshed spec $< $@ && open $@

clean:
	rm *.html

