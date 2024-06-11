from django.utils import timezone
from datetime import datetime

ecuador = timezone.get_fixed_timezone(-5*60)

def getDate():
    now = datetime.now()
    now_ecuador = now.astimezone(ecuador)
    return now_ecuador.date()

def getTime():
    now = datetime.now()
    now_ecuador = now.astimezone(ecuador)
    return now_ecuador.time()
    
