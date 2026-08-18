.PHONY: run test docker docker-run clean verify

PYTHON ?= python3
export PYTHONPATH := src

run:            ## Generate output/dwc_occurrences.csv
	$(PYTHON) -m dwc_etl --verbose

test:           ## Run the unit tests
	$(PYTHON) -m unittest discover -s tests -v

docker:         ## Build the container image
	docker build -t dwc-etl .

docker-run:     ## Run the container, writing to ./output on the host
	docker run --rm -v "$(PWD)/output:/app/output" dwc-etl

verify: run     ## Show the transformations named in the specification
	@echo "--- header ---"; head -n 1 output/dwc_occurrences.csv
	@echo "--- dates ---";  $(PYTHON) -c "import csv;[print(r['occurrenceID'],r['eventDate']) for r in csv.DictReader(open('output/dwc_occurrences.csv'))]"
	@echo "--- authorship ---"; $(PYTHON) -c "import csv;[print(f\"{r['scientificName']!r:38} {r['scientificNameAuthorship']!r}\") for r in csv.DictReader(open('output/dwc_occurrences.csv'))]"

clean:          ## Remove generated output
	rm -f output/dwc_occurrences.csv
