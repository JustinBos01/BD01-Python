Onderstaand zijn de stappen om de webapplicatie te kunnen draaien:

1) Download Github Desktop
2) Clone de github repository. Link: https://github.com/JustinBos01/BD01-Python
3) Download The GO Language. Link: https://golang.org/
4) Set your GOROOT/GOPATH. Link: https://www.jetbrains.com/help/go/configuring-goroot-and-gopath.html
5) Download PostGreSQL
6) Kopieer het sql CREATE script binnen de directory van de applicatie onder *directory tot project*/BD01-python onder de naam SQL.txt
7) Verander binnen *directory tot project*/BD01-python/DB-connection/backend.go de waarden naar uw PostGreSQL account gegevens en database gegevens
8) Binnen PostGreSQL, klik op tools > Query Tool en plak het sql CREATE script
9) Download NodeJS. Link: https://nodejs.org/en/
10) In Node.js, kopieer en plak de volgende regels in nodejs
	> pip install Flask
	> cd *directory tot project*/BD01-Python
	> venv\Scripts\activate
	> set FLASK_APP = app.py
	> flask run