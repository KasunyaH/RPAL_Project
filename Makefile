PY = python3
SCRIPT = myrpal.py

# Default target: runs the RPAL processor with the specified file
run:
	$(PY) $(SCRIPT) $(file)

# Target to print the AST
tree:
	$(PY) $(SCRIPT) $(file) -ast

# Target to print the standardized AST
stree:
	$(PY) $(SCRIPT) $(file) -sast

clean:
	rm -f *.pyc
	rm -rf */__pycache__

# Phony targets to avoid conflicts with files named 'run', 'tree', or 'stree'
.PHONY: run tree stree clean
