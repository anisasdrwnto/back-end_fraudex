from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

h = hash_password("Password123")
print("Hash:", h[:7] + "...", "| panjang:", len(h))
print("Password benar:", verify_password("Password123", h))
print("Password salah:", verify_password("salah", h))

at = create_access_token("USR01")
rt = create_refresh_token("USR01")
print("Access token dibaca:", decode_token(at, "access"))
print("Access dipakai sbg refresh:", decode_token(at, "refresh"))
print("Refresh token dibaca:", decode_token(rt, "refresh"))
print("Token ngawur:", decode_token("abc.def.ghi", "access"))