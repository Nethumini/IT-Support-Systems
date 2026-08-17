from fastapi import APIRouter
from pydantic import BaseModel
from app.services.predictive_service import predictive_service
import psutil

router = APIRouter(tags=["System Monitoring"])

# Define what data we expect from the frontend
class SystemMetrics(BaseModel):
    cpu_usage: float
    ram_usage: float
    disk_usage: float
    temperature: float

@router.post("/predict-health")
async def predict_system_health(metrics: SystemMetrics):
    """
    Analyzes system metrics to predict potential failures.
    """
    result = predictive_service.predict_health(
        metrics.cpu_usage,
        metrics.ram_usage,
        metrics.disk_usage,
        metrics.temperature
    )
    
    # Format response for frontend
    status = result["status"]
    risk_score = result["risk_score"]
    
    # Generate alerts based on metrics
    alerts = []
    if metrics.cpu_usage > 80:
        alerts.append(f"High CPU usage detected: {metrics.cpu_usage}%")
    if metrics.ram_usage > 85:
        alerts.append(f"High RAM usage detected: {metrics.ram_usage}%")
    if metrics.disk_usage > 90:
        alerts.append(f"Critical disk usage: {metrics.disk_usage}%")
    if metrics.temperature > 75:
        alerts.append(f"High temperature warning: {metrics.temperature}°C")
    
    # Generate recommendations
    recommendations = ""
    if status == "critical":
        recommendations = "Immediate action required: Consider scaling resources, clearing disk space, or investigating resource-intensive processes."
    elif alerts:
        recommendations = "Monitor system closely. Consider optimizing resource usage to prevent potential issues."
    else:
        recommendations = "System operating normally. Continue regular monitoring."
    
    return {
        "status": status.upper() if status == "critical" else status.capitalize(),
        "confidence": round(100 - risk_score, 1),  # Invert risk to confidence
        "metrics": {
            "cpu_usage": metrics.cpu_usage,
            "ram_usage": metrics.ram_usage,
            "disk_usage": metrics.disk_usage,
            "temperature": metrics.temperature
        },
        "alerts": alerts,
        "recommendations": recommendations
    }

@router.get("/system-metrics")
async def get_system_metrics():
    """
    Get current system resource usage metrics.
    """
    try:
        # Get CPU usage (1 second interval for accurate reading)
        cpu_usage = round(psutil.cpu_percent(interval=1), 1)
        
        # Get RAM usage
        ram = psutil.virtual_memory()
        ram_usage = round(ram.percent, 1)
        
        # Get disk usage for the main partition
        disk = psutil.disk_usage('/')
        disk_usage = round(disk.percent, 1)
        
        # Try to get temperature (may not work on all systems)
        temperature = 50.0  # Default fallback
        try:
            if hasattr(psutil, 'sensors_temperatures'):
                temps = psutil.sensors_temperatures()
                if temps:
                    # Try to get coretemp, or the first available sensor
                    if 'coretemp' in temps and temps['coretemp']:
                        temperature = round(temps['coretemp'][0].current, 1)
                    else:
                        # Use first available temperature sensor
                        for sensor_list in temps.values():
                            if sensor_list:
                                temperature = round(sensor_list[0].current, 1)
                                break
        except:
            pass  # Keep default temperature
        
        return {
            "cpu_usage": cpu_usage,
            "ram_usage": ram_usage,
            "disk_usage": disk_usage,
            "temperature": temperature
        }
    except Exception as e:
        # Return safe defaults if unable to read metrics
        return {
            "cpu_usage": 50.0,
            "ram_usage": 50.0,
            "disk_usage": 50.0,
            "temperature": 50.0
        }