S_i = [i for i in range(0, 256)]
j = 0

for i in range(0, 256):
    j = (j + S_i[i]) % 256
    S_i[i], S_i[j] = S_i[j], S_i[i]

print(S_i)
