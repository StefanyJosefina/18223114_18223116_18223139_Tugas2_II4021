class A51:
    def __init__(self, key: str):
        self.key_bits = self._normalize_key(key)

    def _normalize_key(self, key: str):
        if len(key) == 64 and all(c in "01" for c in key):
            return [int(b) for b in key]

        key_bytes = key.encode("utf-8")
        if len(key_bytes) < 8:
            key_bytes = key_bytes.ljust(8, b"\x00")
        else:
            key_bytes = key_bytes[:8]

        bits = []
        for byte in key_bytes:
            for i in range(8):
                bits.append((byte >> i) & 1)
        return bits

    def _majority(self, x, y, z):
        return 1 if (x + y + z) >= 2 else 0

    def _clock_r1(self, r1):
        fb = r1[13] ^ r1[16] ^ r1[17] ^ r1[18]
        for i in range(18, 0, -1):
            r1[i] = r1[i - 1]
        r1[0] = fb

    def _clock_r2(self, r2):
        fb = r2[20] ^ r2[21]
        for i in range(21, 0, -1):
            r2[i] = r2[i - 1]
        r2[0] = fb

    def _clock_r3(self, r3):
        fb = r3[7] ^ r3[20] ^ r3[21] ^ r3[22]
        for i in range(22, 0, -1):
            r3[i] = r3[i - 1]
        r3[0] = fb

    def _clock_all(self, r1, r2, r3):
        self._clock_r1(r1)
        self._clock_r2(r2)
        self._clock_r3(r3)

    def _clock_majority(self, r1, r2, r3):
        m = self._majority(r1[8], r2[10], r3[10])

        if r1[8] == m:
            self._clock_r1(r1)
        if r2[10] == m:
            self._clock_r2(r2)
        if r3[10] == m:
            self._clock_r3(r3)

    def _output_bit(self, r1, r2, r3):
        return r1[18] ^ r2[21] ^ r3[22]

    def _frame_bits(self, fn):
        return [(fn >> i) & 1 for i in range(22)]

    def generate_keystream(self, fn, length):
        r1 = [0] * 19
        r2 = [0] * 22
        r3 = [0] * 23

        for b in self.key_bits:
            self._clock_all(r1, r2, r3)
            r1[0] ^= b
            r2[0] ^= b
            r3[0] ^= b

        for b in self._frame_bits(fn):
            self._clock_all(r1, r2, r3)
            r1[0] ^= b
            r2[0] ^= b
            r3[0] ^= b

        for _ in range(100):
            self._clock_majority(r1, r2, r3)

        ks = []
        for _ in range(length):
            self._clock_majority(r1, r2, r3)
            ks.append(self._output_bit(r1, r2, r3))

        return ks

    def bytes_to_bits(self, data):
        bits = []
        for byte in data:
            for i in range(8):
                bits.append((byte >> i) & 1)
        return bits

    def bits_to_bytes(self, bits):
        out = bytearray()
        for i in range(0, len(bits), 8):
            byte = 0
            chunk = bits[i:i + 8]
            for j, b in enumerate(chunk):
                byte |= (b & 1) << j
            out.append(byte)
        return bytes(out)

    def process(self, data):
        bits = self.bytes_to_bits(data)
        result = []

        size = 228
        blocks = (len(bits) + size - 1) // size

        for fn in range(blocks):
            block = bits[fn * size:(fn + 1) * size]
            ks = self.generate_keystream(fn, len(block))
            result.extend([b ^ k for b, k in zip(block, ks)])

        return self.bits_to_bytes(result)

    def encrypt(self, data):
        return self.process(data)

    def decrypt(self, data):
        return self.process(data)