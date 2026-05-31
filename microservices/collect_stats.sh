#!/bin/zsh

OUTPUT_FILE="profiling_samples.csv"

echo "timestamp,container,cpu_percent,memory_usage" > $OUTPUT_FILE

echo "Collecting Docker resource usage samples..."
echo "Output file: $OUTPUT_FILE"

for i in {1..20}
do
  timestamp=$(date "+%Y-%m-%d %H:%M:%S")

  docker stats --no-stream --format "{{.Name}},{{.CPUPerc}},{{.MemUsage}}" | while IFS= read -r line
  do
    container=$(echo "$line" | cut -d',' -f1)
    cpu=$(echo "$line" | cut -d',' -f2 | sed 's/%//g')
    memory=$(echo "$line" | cut -d',' -f3 | cut -d'/' -f1 | xargs)

    if [[ "$container" == "api-gateway" || "$container" == "product-service" || "$container" == "cart-service" || "$container" == "order-service" ]]; then
      echo "$timestamp,$container,$cpu,$memory" >> $OUTPUT_FILE
    fi
  done

  echo "Sample $i collected"
  sleep 2
done

echo "Resource profiling completed."
echo "Saved to $OUTPUT_FILE"
