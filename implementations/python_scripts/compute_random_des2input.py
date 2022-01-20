import random

N = 256
for i in range(N):
	s1 = "#if RUN=={}\n".format(i)
	s1 = s1 + "uint64_t input = 0x"
	for j in range(8):
		r = hex(random.randint(0,255))[2:]
		s1 = s1 + str(r)
		if j < 7:
			s1 = s1 + ""
	s1 = s1 + ";\n"
	s1 = s1 + "#endif"
	print(s1)
