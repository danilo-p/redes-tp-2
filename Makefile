run_servidor:
	./servidor.py 51511

run_cliente_ipv4:
	./cliente.py 127.0.0.1 51511 arquivo.pdf

run_cliente_ipv6:
	./cliente.py ::1 51511 arquivo.pdf
