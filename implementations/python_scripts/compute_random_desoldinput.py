import random

N = 256
for i in range(N):
	s1 = "#if ROUND=={}".format(i)
	s2 = "uint64_t data = "
	s3 = "0x"
	for j in range(16):
		r = hex(random.randint(0,15))[2:]
		s3 = s3 + str(r)				
	s2 = s2 + s3 + ";"
	s4 = "#endif"
	print(s1)
	print(s2)
	print(s4)
