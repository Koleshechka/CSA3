c=0
sum = 0
x1 = 1
x2 = 2
counter = 2
while c < 4000000:
    c = x1 + x2
    if c % 2 == 0:
        sum += c
    x1 = x2
    x2 = c
    counter+=1
print(sum)
print(counter)