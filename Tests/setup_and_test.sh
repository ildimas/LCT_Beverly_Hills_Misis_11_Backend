#!sh
docker kill db
docker kill db_test
cd ../API/Scripts
docker-compose -f docker-compose-db.yml up --build -d
cd ../../Tests
pytest