env:
	virtualenv .env
	.env/bin/pip install requests
	.env/bin/pip install requests[security]
	.env/bin/pip install PyJWT

run:
	.env/bin/python demo.py

clean:
	rm -r .env
