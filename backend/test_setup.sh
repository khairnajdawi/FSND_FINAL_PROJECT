export JWT_SECRET='khair5345'
export DATABASE_URL="postgresql://khairallah:Najdawi@localhost:5432/casting_system_test"
export AUTH0_DOMAIN='kj-casting-agency.us.auth0.com'
export API_AUDIENCE='https://kj-casting-system.herukoapp.com'
dropdb --if-exists casting_system_test && createdb casting_system_test
psql casting_system_test <  backend/casting_system_test.sql
gunicorn -b 0.0.0.0:5000 backend.flaskr:app
