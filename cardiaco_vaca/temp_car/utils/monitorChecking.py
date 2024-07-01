from datetime import datetime, date, time
from temp_car.models import ControlMonitoreo

fecha_actual = datetime.now().date()
hora_actual = time(10, 0)

# Calcular los rangos de tiempo para la mañana y la tarde
startMorning = datetime.combine(fecha_actual, time(hour=7, minute=0))
endMorning = datetime.combine(fecha_actual, time(hour=12, minute=0))
startAfternoon = datetime.combine(fecha_actual, time(hour=13, minute=0))
endAfternoon = datetime.combine(fecha_actual, time(hour=18, minute=0))

def checkingMorning(idBovino):
    controlesMorning = ControlMonitoreo.objects.filter(
        fecha_lectura=fecha_actual,
        id_Lectura__id_Bovino=idBovino,
        hora_lectura__range=(startMorning.time(), endMorning.time())
    ).count()
    return controlesMorning == 0

def checkingAfternoon(idBovino):
    controlesAfternoon = ControlMonitoreo.objects.filter(
        id_Lectura__id_Bovino=idBovino,
        fecha_lectura=fecha_actual,
        hora_lectura__range=(startAfternoon.time(), endAfternoon.time())
    ).count()
    return controlesAfternoon == 0

def checkHoursMorning(timeNow):
    return startMorning.time() <= timeNow <= endMorning.time()

def checkHoursAfternoon(timeNow):
    return startAfternoon.time() <= timeNow <= endAfternoon.time()

def checkDate(dateNow):
    return dateNow == fecha_actual
