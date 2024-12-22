
all: Dongsa.ankiaddon

FILES += LICENSE.txt
FILES += __init__.py
FILES += conjugation_row.py
FILES += config.py
FILES += config.json
FILES += manifest.json
FILES += meta.json

# generated code:
FILES += ui/ui_main_dialog.py
FILES += ui/ui_conjugation_row_frame.py

ui:
	mkdir -p $@

ui/ui_%.py: %.ui | ui
	pyuic6 -o $@ $<

Dongsa.ankiaddon: $(FILES)
	zip -9r $@ $^ ../korean/ -x '../korean/__pycache__/*' '../korean/templates/*' '../korean/web/*'

clean:
	-rm -rf ui Dongsa.ankiaddon

.PHONY: clean

