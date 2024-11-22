import socket
import struct
import threading


semaphore = threading.Semaphore(1)

def build_dns_query(domain_name):
    transaction_id = b'\xAA\xAA'
    flags = b'\x01\x00'
    questions = b'\x00\x01'
    answer_rrs = b'\x00\x00'
    authority_rrs = b'\x00\x00'
    additional_rrs = b'\x00\x00'

    dns_header = transaction_id + flags + questions + answer_rrs + authority_rrs + additional_rrs

    qname = b''.join(struct.pack('!B', len(label)) + label.encode() for label in domain_name.split('.')) + b'\x00'
    qtype = b'\x00\x01'  # A
    qclass = b'\x00\x01' # IN

    dns_question = qname + qtype + qclass

    return dns_header + dns_question

def send_dns_query(sock, domain_name, dns_server="8.8.8.8"):
    query = build_dns_query(domain_name)

    try:
        with semaphore:
            sock.sendto(query, (dns_server, 53))
            response, _ = sock.recvfrom(512)

        ip_address = get_ip(response)
        print(f"The IP address of {domain_name} is: {ip_address}")

    except socket.timeout:
        print(f"Request for {domain_name} timed out")

def get_ip(response):
    ip_parts = response[-4:]
    ip_address = ".".join(map(str, ip_parts))
    return ip_address

if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)
    domains = ["stakoverflow.com", "google.com","sess.sku.ac.ir", "bing.com"] # filtered domains behaviour e.g: facebook.com 
    threads = []
    for domain in domains:
        thread = threading.Thread(target=send_dns_query, args=(sock, domain,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    sock.close()