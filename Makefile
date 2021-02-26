run_servidor:
	./servidor.py 51511

run_cliente_ipv4:
	./cliente.py 127.0.0.1 51511 video.mp4

run_cliente_ipv6:
	./cliente.py ::1 51511 video.mp4

show_tc_lo_config:
	sudo tc qdisc show dev lo

add_tc_lo_config:
	sudo tc qdisc add dev lo root netem delay 10ms limit 20 rate 1mbit loss 10%

del_tc_lo_config:
	sudo tc qdisc del dev lo root
