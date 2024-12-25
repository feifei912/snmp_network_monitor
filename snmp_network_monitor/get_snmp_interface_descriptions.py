from pysnmp.hlapi import *

def get_interface_descriptions():
    iterator = nextCmd(SnmpEngine(),
                       CommunityData('public', mpModel=0),
                       UdpTransportTarget(('127.0.0.1', 161)),
                       ContextData(),
                       ObjectType(ObjectIdentity('1.3.6.1.2.1.2.2.1.2')),
                       lexicographicMode=False)

    for errorIndication, errorStatus, errorIndex, varBinds in iterator:
        if errorIndication:
            print(f"SNMP 错误: {errorIndication}")
            break
        elif errorStatus:
            print(f"SNMP 错误: {errorStatus.prettyPrint()}")
            break
        else:
            for varBind in varBinds:
                print(f"{varBind[0]} = {varBind[1]}")

# 调用函数来获取接口描述
if __name__ == '__main__':
    get_interface_descriptions()
    input("Press Enter to exit...")