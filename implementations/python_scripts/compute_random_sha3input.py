import random

N = 256
for i in range(N):
	s1 = "#if RUN=={}\n".format(i)
	s1 = s1 + "uint8_t msg[104] = {"
	for j in range(104):
		r = random.randint(0,255)
		s1 = s1 + str(r)
		if j < 103:
			s1 = s1 + ", "
	s1 = s1 + "};\n"
	s1 = s1 + "#endif"
	print(s1)
