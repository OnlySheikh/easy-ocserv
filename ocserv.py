#Imports
import os
import socket
from os import chdir as cd

#Main
print("Welcome to OCServ Auto Config v1.0 by Only Sheikh!")
serverIP = os.popen("curl ifconfig.me").read()
print("Your Server IP: "+str(serverIP))
serverIP = str(serverIP)
print(" ")
vpnPORT = input("Enter your desire VPN port(number): ")
vpnUsername = input("Enter a username(text): ")

maxClient = input("Max Client(number): ")
maxSame = input("Max Same Client(number): ")
connectionMessage = input("Connection Banner Message(text): ")

aptgetUPDATE = 'sudo apt-get update'
os.system(aptgetUPDATE)

installOCServ = 'sudo apt-get install ocserv gnutls-bin -y'
os.system(installOCServ)

caTMPL = """cn = "VPN CA"
organization = "CUI Wah"
serial = 1
expiration_days = 3650
ca
signing_key
cert_signing_key
crl_signing_key"""

createCAtmpl = open("/etc/ocserv/ca.tmpl","x")
createCAtmpl.write(caTMPL)
createCAtmpl.close()

cd('/etc/ocserv/')

caKEY = 'certtool --generate-privkey --outfile ca-key.pem'
os.system(caKEY)

caCert = 'certtool --generate-self-signed --load-privkey ca-key.pem --template ca.tmpl --outfile ca-cert.pem'
os.system(caCert)

serverTMPL = """cn = "{ip}"
organization = "CUI Wah"
expiration_days = 3650
signing_key
encryption_key
tls_www_server""".format(ip = serverIP)

createServerTMPL = open("/etc/ocserv/server.tmpl","x")
createServerTMPL.write(serverTMPL)
createServerTMPL.close()

serverKEY = 'certtool --generate-privkey --outfile server-key.pem'
os.system(serverKEY)

serverCert = 'certtool --generate-certificate --load-privkey server-key.pem --load-ca-certificate ca-cert.pem --load-ca-privkey ca-key.pem --template server.tmpl --outfile server-cert.pem'
os.system(serverCert)

with open('/etc/ocserv/ocserv.conf') as f:
    lines = f.read()

lines = lines.replace('auth = "pam[gid-min=1000]"','auth = "plain[/etc/ocserv/ocpasswd]"')
lines = lines.replace("server-cert = /etc/pki/ocserv/public/server.crt","server-cert = /etc/ocserv/server-cert.pem")
lines = lines.replace("server-key = /etc/pki/ocserv/private/server.key","server-key = /etc/ocserv/server-key.pem")
lines = lines.replace("dns = 192.168.1.2","dns = 8.8.8.8")
lines = lines.replace("tcp-port = 443","tcp-port = "+vpnPORT)
lines = lines.replace("udp-port = 443","udp-port = "+vpnPORT)
lines = lines.replace("#tunnel-all-dns = true","tunnel-all-dns = true")
lines = lines.replace("route = 10.10.10.0/255.255.255.0","#route = 10.10.10.0/255.255.255.0")
lines = lines.replace("route = 192.168.0.0/255.255.0.0","#route = 192.168.0.0/255.255.0.0")
lines = lines.replace("no-route = 192.168.5.0/255.255.255.0","#no-route = 192.168.5.0/255.255.255.0")
lines = lines.replace("max-clients = 16","max-clients = "+maxClient)
lines = lines.replace("max-same-clients = 2","max-same-clients = "+maxSame)
lines = lines.replace('#banner = "Welcome"','banner = "'+connectionMessage+'"')

ocservCONFIG = open("/etc/ocserv/ocserv.conf","w")
ocservCONFIG.write(lines)
ocservCONFIG.close()

with open('/lib/systemd/system/ocserv.socket') as f:
    ocSocket = f.read()

ocSocket = ocSocket.replace("443",vpnPORT)

ocservSocket = open("/lib/systemd/system/ocserv.socket","w")
ocservSocket.write(ocSocket)
ocservSocket.close()

deamon = 'sudo systemctl daemon-reload'
os.system(deamon)

restartOCSERV = 'sudo systemctl restart ocserv'
os.system(restartOCSERV)

with open('/etc/sysctl.conf') as f:
    conf = f.read()

conf = conf.replace("#net.ipv4.ip_forward=1","net.ipv4.ip_forward=1")

sysctl = open("/etc/sysctl.conf","w")
sysctl.write(conf)
sysctl.close()

cmd = 'sudo sysctl -p'
os.system(cmd)

ipTables = 'sudo apt-get install iptables-persistent -y'
os.system(ipTables)

cmd = 'sudo iptables -A INPUT -p tcp --dport '+vpnPORT+' -j ACCEPT'
os.system(cmd)

cmd = 'sudo iptables -A INPUT -p udp --dport '+vpnPORT+' -j ACCEPT'
os.system(cmd)

cmd = 'sudo iptables -t nat -A POSTROUTING -j MASQUERADE'
os.system(cmd)

cmd = 'sudo dpkg-reconfigure iptables-persistent'
os.system(cmd)

cmd = 'sudo netstat -tulpn | grep '+vpnPORT
os.system(cmd)

cmd = 'sudo systemctl stop ocserv.socket'
os.system(cmd)

cmd = 'sudo ocserv -c /etc/ocserv/ocserv.conf'
os.system(cmd)

cmd = 'sudo netstat -tulpn | grep '+vpnPORT
os.system(cmd)

print("Choose a password for '"+vpnUsername+"':")
cmd = 'sudo ocpasswd -c /etc/ocserv/ocpasswd '+vpnUsername
os.system(cmd)

print("The End! Enjoy and Eshqo hallll :D")
os.remove("/root/ocserv.py")
