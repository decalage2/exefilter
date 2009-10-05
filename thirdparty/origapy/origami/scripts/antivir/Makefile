EICARSIG='X5O!P%@AP[4\PZX54(P^)7CC)7}$$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$$H+H*'
CALCSIG='calc.exe'

all:
	ruby detectsig.rb $(EICARSIG) *.pdf
	ruby detectsig.rb $(CALCSIG) *.pdf
	@echo
	ruby detectjs.rb *.pdf
	@echo
	ruby cleaner.rb -i calc.pdf -o clean_calc.pdf -t all
