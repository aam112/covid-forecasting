ENV=covid-forecast

setup:
	conda env create -f environment.yml || conda env update -f environment.yml
	python -m ipykernel install --user --name $(ENV) --display-name "$(ENV)"

fetch:
	python src/fetch_data.py

train:
	python src/train_prophet.py

report:
	jupyter nbconvert --to html --output-dir docs notebooks/01_evaluation.ipynb
	python -m http.server --directory docs 8000

pages:
	@echo "Enable GitHub Pages: Settings → Pages → Branch main, Folder /docs"
