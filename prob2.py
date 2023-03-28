sum = 0
x1 = 1
x2 = 2
c = 2
while x2 < 4000000:
    if c % 2 == 0:
        sum += c
        print(c, sum)
    c = x1 + x2
    x1 = x2
    x2 = c
print(sum)
