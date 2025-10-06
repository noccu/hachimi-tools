BUNDLE_BASE_KEY = "532b4631e4a7b9473e7cfb"

def decrypt_asset_bundle(data:bytes, key:int):
    if len(data) < 256:
        return data
    return _decrypt(data, key)

def _decrypt(data:bytes, key:int):
    final_key = _create_final_key(key)
    decrypted_data = bytearray(data)
    for i in range(256, len(decrypted_data)):
        decrypted_data[i] ^= final_key[i % len(final_key)]
    return bytes(decrypted_data)

def _create_final_key(key:int):
    base_key = bytes.fromhex(BUNDLE_BASE_KEY)
    bundle_key = key.to_bytes(8, byteorder="little", signed=True)
    base_len = len(base_key)
    final_key = bytearray(base_len * 8)
    for i, b in enumerate(base_key):
        baseOffset = i << 3 # i * 8
        for j, k in enumerate(bundle_key):
            final_key[baseOffset + j] = b ^ k
    return final_key