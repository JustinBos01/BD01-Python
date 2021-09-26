from spherov2 import scanner
from spherov2.adapter.tcp_adapter import get_tcp_adapter
from spherov2.sphero_edu import SpheroEduAPI

with scanner.find_toy(adapter=get_tcp_adapter('localhost')) as toy:
    print("test")

#python -m spherov2.adapter.tcp_server 0.0.0.0 50004