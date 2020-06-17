fastapi-API
===========
It is an implementation of REST API application, written using fastapi. It implements functionality for adding users, their posts, likes, unlikes and getting info about requests. Fastapi was chosen as a very quick and effective tool. It also already has built-in documentation, which serves as an alternative frontend for the client. Json web token(JWT) is being used for authorization, mysql for the database, and docker for deployment. Therefore, you can very quickly untap this API by following the instructions below.


After cloning this repository locally, be sure to add yourself two .env files with important keys for the database and for the api server itself. In the following formats:

* database(into database directory):
  * DB_PASS = 'password'
* fastapi_server(into current repo directory):
  * ALGORITHM = 'HS256'
  * ACCESS_TOKEN_EXPIRE_MINUTES = 30
  * SECRET_KEY = 'ffd3fccf1...eca3d111' (can be genereted by `$openssl rand -hex 32`)
  * DB_PASS = 'password'
  
Afterwards up docker-compose into database directory, **then** into current directory. Check your api http://localhost:8000/docs



