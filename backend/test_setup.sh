export JWT_SECRET='khair5345'
export DATABASE_URL="postgresql://khairallah:Najdawi@localhost:5432/casting_system_test"
dropdb --if-exists casting_system_test && createdb casting_system_test
psql casting_system_test <  casting_system_test.sql
gunicorn -b 0.0.0.0:5000 flaskr:app
