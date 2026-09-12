all: data_exchange.html discovery.html policy.html course_identifier.html

%.html: %.bs
	bikeshed spec $< $@ && open $@

clean:
	rm *.html

