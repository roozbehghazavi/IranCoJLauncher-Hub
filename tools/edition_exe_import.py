"""Makes the Edition's CoJBiBGame_x86.exe load irancojfx.dll (IranCoJ Graphics) when the game starts.

The mod loader (dinput8.dll) loads the mods only once the game sets up its input, after the engine has created its
post-process buffers. The render scale (TAA upscaling) has to size those buffers, so irancojfx.dll must be in before
the engine starts: the exe imports it (IrnFx_Early, which does nothing - the import is what matters).

A new section (.irn) holds a copy of the exe's import table with irancojfx.dll added; the import directory points at
it. Nothing else in the exe changes (it has no checksum, signature or bound imports). Running it again is a no-op.

    python tools/edition_exe_import.py edition/files/CoJBiBGame_x86.exe
"""

import struct
import sys

DLL = b"irancojfx.dll"
FUNC = b"IrnFx_Early"


def align(v, a):
    return (v + a - 1) // a * a


def main(path):
    b = bytearray(open(path, "rb").read())
    pe = struct.unpack_from("<I", b, 0x3C)[0]
    nsec = struct.unpack_from("<H", b, pe + 6)[0]
    opt_size = struct.unpack_from("<H", b, pe + 20)[0]
    opt = pe + 24
    sect_align, file_align = struct.unpack_from("<II", b, opt + 32)
    size_headers = struct.unpack_from("<I", b, opt + 60)[0]
    first = opt + opt_size
    secs = [struct.unpack_from("<8sIIII", b, first + i * 40) for i in range(nsec)]
    if any(s[0].rstrip(b"\0") == b".irn" for s in secs):
        print("already imports irancojfx.dll")
        return
    if struct.unpack_from("<II", b, opt + 96 + 11 * 8) != (0, 0) or struct.unpack_from("<II", b, opt + 96 + 4 * 8) != (0, 0):
        sys.exit("bound imports or a signature: not handled")
    if first + (nsec + 1) * 40 > size_headers:
        sys.exit("no room for another section header")

    def off(rva):
        for name, vs, va, rs, ro in secs:
            if va <= rva < va + max(vs, rs):
                return rva - va + ro
        raise ValueError(hex(rva))

    imp_rva, imp_size = struct.unpack_from("<II", b, opt + 96 + 8)
    old = []
    o = off(imp_rva)
    while True:
        d = struct.unpack_from("<5I", b, o)
        if d == (0, 0, 0, 0, 0):
            break
        old.append(d)
        o += 20

    va = align(max(s[2] + s[1] for s in secs), sect_align)
    raw = align(len(b), file_align)
    n = len(old) + 2                                    # the old ones, ours, the null one
    p_ilt = align(n * 20, 16)
    p_iat = p_ilt + 8
    p_hint = p_iat + 8
    p_name = align(p_hint + 2 + len(FUNC) + 1, 4)
    size = p_name + len(DLL) + 1
    data = bytearray(align(size, file_align))
    for i, d in enumerate(old):
        struct.pack_into("<5I", data, i * 20, *d)
    struct.pack_into("<5I", data, len(old) * 20, va + p_ilt, 0, 0, va + p_name, va + p_iat)
    struct.pack_into("<II", data, p_ilt, va + p_hint, 0)
    struct.pack_into("<II", data, p_iat, va + p_hint, 0)
    data[p_hint + 2:p_hint + 2 + len(FUNC)] = FUNC
    data[p_name:p_name + len(DLL)] = DLL

    b.extend(b"\0" * (raw - len(b)))
    b.extend(data)
    hdr = first + nsec * 40
    struct.pack_into("<8sIIIIIIHHI", b, hdr, b".irn", align(size, sect_align), va, len(data), raw, 0, 0, 0, 0,
                     0xC0000040)                        # initialised data, read / write (the loader fills our IAT)
    struct.pack_into("<H", b, pe + 6, nsec + 1)
    struct.pack_into("<I", b, opt + 56, va + align(size, sect_align))          # SizeOfImage
    struct.pack_into("<II", b, opt + 96 + 8, va, n * 20)                        # the import directory
    open(path, "wb").write(b)
    print(f"{path}: imports {DLL.decode()} ({len(old)} DLLs kept), section .irn at {va:#x}")


if __name__ == "__main__":
    main(sys.argv[1])
