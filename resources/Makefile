all: ontology-shacl.html ontology.html

ontology-shacl.html: ontology-shacl.ttl
	docker run --rm -v $$(pwd):/mnt shacl-play doc -i /mnt/ontology-shacl.ttl -l en -o /mnt/$@
	sed -i -e "s|latestVersion:\s*null\s*,|edDraftURI: null, latestVersion: \"https://specs.quality-link.eu/resources/$@\",|" $@

ontology.html: ontology-shacl.ttl
	docker run --rm -v $$(pwd):/mnt widoco -ontFile /mnt/ontology-shacl.ttl -uniteSections -outFolder /mnt/widoco-out -excludeProvenance
	cp -a widoco-out/index-en.html ontology.html

