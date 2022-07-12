# kaz_dream_test_task
Тестовое задание в kazdream


<h1>How to Run Webserver</h1>
<h3>First Step: Build container</h3>
<code>docker build . -t fa_webserver</code>
<p></p>
<h3>Second Step: Run container</h3>
<code>docker run -p 8080:8080 -d fa_webserver</code>
<p></p>
<h3>Third Step: Check it out in:</h3>
<code>http://localhost:8080/smartphones?price=46990</code>

<h1>How to Run Parser</h1>
Enter command <code>python3 parser/shop_kz_parser.py</code>
