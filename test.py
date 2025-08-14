def ksa() -> bytes:
    S = list(range(256))
    j = 0
    key_len = len([208, 248, 14, 182, 76, 61, 3, 131, 93, 60, 233, 164, 150, 153, 27, 23])
    for i in range(256):
        j = (j + S[i] + [208, 248, 14, 182, 76, 61, 3, 131, 93, 60, 233, 164, 150, 153, 27, 23][i % key_len]) & 0xFF
        S[i], S[j] = S[j], S[i]
    return S


def enc(S: bytes, data: bytes) -> bytes:
    i = j = 0
    out = bytearray()
    for b in data:
        i = (i + 1) & 0xFF
        j = (j + S[i]) & 0xFF
        S[i], S[j] = S[j], S[i]
        K = S[(S[i] + S[j]) & 0xFF]
        out.append(b ^ K)
    return list(out)


if enc(ksa(), input().encode()) == [101, 251, 204, 28, 208, 102, 172, 182, 60, 88, 80]:
    print("Correct!")
else:
    print("Incorrect!")