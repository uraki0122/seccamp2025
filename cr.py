x = 5
if x > 0:
    print("positive")
else:
    print("non-positive")

    x = 5
state = 0


while True:
    if state == 0:
        if x > 0:
            state = 1
        else:
            state = 2
    elif state == 1:
        print("positive")
        break
    elif state == 2:
        print("non-positive")
        break

    import random

x = 5
state = 42  # 無意味な初期値

while True:
    if state == 42:
        state = 99 if random.random() > -1 else 100  # 常に99になるが分かりにくい
    elif state == 99:
        tmp = x * 2 - x  # 無意味な計算
        if tmp > 0:
            state = 1
        else:
            state = 2
    elif state == 1:
        print("positive")
        state = 123  # ダミー状態へ
    elif state == 2:
        print("non-positive")
        state = 123  # ダミー状態へ
    elif state == 123:
        break
    else:
        state = 42