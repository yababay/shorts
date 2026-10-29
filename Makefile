DIR_NAME = "${shell: date --iso}"

current:
	mkdir -p "${DIR_NAME}"
	rm -rf .current
	ln -s "${DIR_NAME}" .current

git:
	cp ~/.config/GIMP/3.0/plug-ins/prepare_short_interactive/prepare_short_interactive.py .
	git add .
	git commit -am ok
	git push origin main


