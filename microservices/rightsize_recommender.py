import csv
import math
import re
from collections import defaultdict

INPUT_FILE = "profiling_samples.csv"
REPORT_FILE = "resource_recommendation_report.txt"
COMPOSE_FILE = "docker-compose-rightsized.yml"

SERVICES = {
    "product-service": {
        "dockerfile": "product-service/Dockerfile",
        "port": "8001:8001"
    },
    "cart-service": {
        "dockerfile": "cart-service/Dockerfile",
        "port": "8002:8002"
    },
    "order-service": {
        "dockerfile": "order-service/Dockerfile",
        "port": "8003:8003"
    },
    "api-gateway": {
        "dockerfile": "api-gateway/Dockerfile",
        "port": "8000:8000"
    }
}

def memory_to_mib(memory_text):
    """
    Converts Docker memory values such as 45MiB, 1.2GiB, 900KiB to MiB.
    """
    memory_text = memory_text.strip()
    match = re.match(r"([\d.]+)\s*([A-Za-z]+)", memory_text)

    if not match:
        return 0.0

    value = float(match.group(1))
    unit = match.group(2).lower()

    if unit in ["gib", "gb"]:
        return value * 1024
    if unit in ["mib", "mb"]:
        return value
    if unit in ["kib", "kb"]:
        return value / 1024
    if unit in ["b"]:
        return value / (1024 * 1024)

    return value

def round_memory_limit(mib):
    """
    Rounds memory to practical Docker limits.
    Minimum is 128 MB.
    """
    recommended = mib * 2.0

    if recommended <= 128:
        return 128
    if recommended <= 256:
        return 256
    if recommended <= 512:
        return 512

    return int(math.ceil(recommended / 128) * 128)

def recommend_cpu(cpu_peak, container_name):
    """
    Recommends CPU limits.
    Minimum is kept practical because FastAPI services are lightweight.
    API Gateway gets slightly higher limit because all traffic passes through it.
    """
    if container_name == "api-gateway":
        if cpu_peak <= 20:
            return "0.50"
        if cpu_peak <= 50:
            return "1.00"
        return "1.50"

    if cpu_peak <= 20:
        return "0.25"
    if cpu_peak <= 50:
        return "0.50"
    return "1.00"

def main():
    data = defaultdict(lambda: {"cpu": [], "memory": []})

    try:
        with open(INPUT_FILE, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                container = row["container"]
                cpu = float(row["cpu_percent"])
                memory = memory_to_mib(row["memory_usage"])

                data[container]["cpu"].append(cpu)
                data[container]["memory"].append(memory)
    except FileNotFoundError:
        print("ERROR: profiling_samples.csv not found.")
        print("Run ./collect_stats.sh first.")
        return

    recommendations = {}

    for container, values in data.items():
        if not values["cpu"] or not values["memory"]:
            continue

        avg_cpu = sum(values["cpu"]) / len(values["cpu"])
        peak_cpu = max(values["cpu"])
        avg_memory = sum(values["memory"]) / len(values["memory"])
        peak_memory = max(values["memory"])

        recommended_cpu = recommend_cpu(peak_cpu, container)
        recommended_memory = round_memory_limit(peak_memory)

        recommendations[container] = {
            "avg_cpu": avg_cpu,
            "peak_cpu": peak_cpu,
            "avg_memory": avg_memory,
            "peak_memory": peak_memory,
            "recommended_cpu": recommended_cpu,
            "recommended_memory": recommended_memory
        }

    with open(REPORT_FILE, "w") as report:
        report.write("EcoCart-RS: Container Resource Profiling and Right-Sizing Report\n")
        report.write("=" * 70 + "\n\n")

        report.write("Project: CloudCart E-Commerce Microservices\n")
        report.write("Goal: Profile CPU/RAM usage and recommend right-sized container limits.\n\n")

        for container, rec in recommendations.items():
            report.write(f"Container: {container}\n")
            report.write("-" * 50 + "\n")
            report.write(f"Average CPU Usage: {rec['avg_cpu']:.2f}%\n")
            report.write(f"Peak CPU Usage: {rec['peak_cpu']:.2f}%\n")
            report.write(f"Average Memory Usage: {rec['avg_memory']:.2f} MiB\n")
            report.write(f"Peak Memory Usage: {rec['peak_memory']:.2f} MiB\n")
            report.write(f"Recommended CPU Limit: {rec['recommended_cpu']} CPU\n")
            report.write(f"Recommended Memory Limit: {rec['recommended_memory']} MB\n\n")

        report.write("Explanation:\n")
        report.write("The recommendation is based on observed peak CPU and memory usage.\n")
        report.write("A safety buffer is added so containers have enough resources during load.\n")
        report.write("API Gateway receives slightly higher resources because all requests pass through it.\n")
        report.write("Product, Cart, and Order services are lightweight, so they are assigned smaller limits.\n")

    with open(COMPOSE_FILE, "w") as compose:
        compose.write("services:\n")

        for service_name in ["product-service", "cart-service", "order-service", "api-gateway"]:
            service = SERVICES[service_name]
            rec = recommendations.get(service_name)

            if rec:
                cpu_limit = rec["recommended_cpu"]
                memory_limit = rec["recommended_memory"]
            else:
                cpu_limit = "0.25"
                memory_limit = 128

            compose.write(f"  {service_name}:\n")
            compose.write("    build:\n")
            compose.write("      context: .\n")
            compose.write(f"      dockerfile: {service['dockerfile']}\n")
            compose.write(f"    container_name: {service_name}\n")
            compose.write("    ports:\n")
            compose.write(f"      - \"{service['port']}\"\n")

            if service_name == "api-gateway":
                compose.write("    depends_on:\n")
                compose.write("      - product-service\n")
                compose.write("      - cart-service\n")
                compose.write("      - order-service\n")

            compose.write(f"    cpus: \"{cpu_limit}\"\n")
            compose.write(f"    mem_limit: {memory_limit}m\n\n")

    print("Right-sizing analysis completed.")
    print(f"Generated report: {REPORT_FILE}")
    print(f"Generated optimized compose file: {COMPOSE_FILE}")

if __name__ == "__main__":
    main()
