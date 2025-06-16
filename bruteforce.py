import os
import lmdb
import hashlib
import base58
import ecdsa
import signal
from bech32 import encode
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn

# ========== LMDB ochiladi ==========
env = lmdb.open("richlist_db", readonly=True, lock=False, max_readers=2048)
txn = env.begin()

# ========== BTC address yasovchilar ==========
def get_p2pkh_address(pubkey_bytes):
    pubkey_hash = hashlib.new('ripemd160', hashlib.sha256(pubkey_bytes).digest()).digest()
    return base58.b58encode_check(b'\x00' + pubkey_hash).decode()

def get_p2sh_address(pubkey_bytes):
    pubkey_hash = hashlib.new('ripemd160', hashlib.sha256(pubkey_bytes).digest()).digest()
    return base58.b58encode_check(b'\x05' + pubkey_hash).decode()

def get_bech32_address(pubkey_bytes):
    sha = hashlib.sha256(pubkey_bytes).digest()
    rip = hashlib.new('ripemd160', sha).digest()
    return encode('bc', 0, rip)

# ========== Key generatorlar ==========
def generate_private_key():
    return os.urandom(32)

def private_to_public(privkey):
    sk = ecdsa.SigningKey.from_string(privkey, curve=ecdsa.SECP256k1)
    vk = sk.get_verifying_key()
    return b'\x04' + vk.to_string()

# ========== LMDB orqali addressni tekshirish ==========
def check_address(address):
    return txn.get(address.encode()) is not None

# ========== Toza chiqish uchun signal handler ==========
def handle_exit(sig, frame):
    print("\n❗ To‘xtatildi. Dasturdan chiqildi.")
    exit(0)

signal.signal(signal.SIGINT, handle_exit)

# ========== Progress bar bilan bruteforce ==========
with Progress(
    SpinnerColumn(),
    TextColumn("[bold blue]{task.description}"),
    BarColumn(),
    "[progress.percentage]{task.percentage:>3.1f}%",
    TextColumn("Tekshirildi: [yellow]{task.completed}[/]"),
    TimeElapsedColumn(),
    TimeRemainingColumn(),
    transient=True
) as progress:

    task = progress.add_task("Bruteforce ishlayapti...", total=None)

    while True:
        privkey = generate_private_key()
        priv_hex = privkey.hex()
        pubkey = private_to_public(privkey)

        addr1 = get_p2pkh_address(pubkey)
        addr3 = get_p2sh_address(pubkey)
        addrbc1 = get_bech32_address(pubkey)

        for address in [addr1, addr3, addrbc1]:
            if check_address(address):
                print(f"\n🎯 [bold red]TOPILDI![/bold red] {address} | priv: {priv_hex}")
                with open("found.txt", "a") as f:
                    f.write(f"{address} | {priv_hex}\n")

        progress.update(task, advance=1)
