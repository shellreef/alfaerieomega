all:
	python process_images.py

clean: clean-colors clean-rotations

clean-colors:
	rm [yrgcopek]*.gif

clean-rotations:
	rm -rf generated-rotations/
