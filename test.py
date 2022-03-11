from time import sleep

gain = 1

for t in range(120):
    print(t, gain)
    gain -= 0.1
    sleep(1)