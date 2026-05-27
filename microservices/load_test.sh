#!/bin/zsh

echo "Starting CloudCart API load test..."

for i in {1..100}
do
  curl -s http://localhost:8000/products > /dev/null

  curl -s -X POST http://localhost:8000/cart \
  -H "Content-Type: application/json" \
  -d '{"product_id":1,"quantity":2}' > /dev/null

  curl -s http://localhost:8000/cart > /dev/null

  curl -s -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"user_name":"Ravi","product_id":1,"quantity":2,"address":"Hubballi"}' > /dev/null

  curl -s http://localhost:8000/orders > /dev/null

  echo "Request batch $i completed"
done

echo "Load test completed."
