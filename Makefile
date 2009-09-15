clean:
	@echo "Cleaning up build and *.pyc files..."
	@find . -name '*.pyc' -exec rm -rf {} \;
	@rm -rf build
	@echo "removing (.coverage)"
	@rm -f .coverage
	@echo "removing (test_data)"
	@rm -rf `pwd`/test_data
	@echo "Done!"
	
unit: clean
	@echo "Running unit tests..."
	@export PYTHONPATH=`pwd`:`pwd`/staticgenerator::$$PYTHONPATH && \
		nosetests -d -s --verbose --with-coverage --cover-inclusive --cover-package=staticgenerator \
			staticgenerator/tests/unit
	
functional: clean
	@echo "Running unit tests..."
	@mkdir `pwd`/test_data
	@export PYTHONPATH=`pwd`:`pwd`/staticgenerator::$$PYTHONPATH && \
		nosetests -d -s --verbose --with-coverage --cover-inclusive --cover-package=staticgenerator \
			staticgenerator/tests/functional
	
