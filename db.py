import lmdb
import os

# 📦 Sozlamalar
DB_PATH = "richlist_db"
TEXT_PATH = "richlist.txt"
MAP_SIZE_GB = 2  # 2GB — RAM 8GB bo‘lsa xavfsiz

def load_to_lmdb():
    env = lmdb.open(DB_PATH, map_size=MAP_SIZE_GB * 1024 ** 3)
    count = 0
    with env.begin(write=True) as txn:
        with open(TEXT_PATH, "r") as file:
            for line in file:
                addr = line.strip()
                if addr:
                    txn.put(addr.encode(), b"1")
                    count += 1
                    if count % 1_000_000 == 0:
                        print(f"{count:,} ta address yuklandi...")
    env.close()
    return count

def check_address(address: str):
    env = lmdb.open(DB_PATH, readonly=True, lock=False)
    with env.begin() as txn:
        result = txn.get(address.encode())
    env.close()
    return result is not None

if __name__ == "__main__":
    if not os.path.exists(DB_PATH) or not os.listdir(DB_PATH):
        print("🔄 LMDB bazaga addresslar yuklanmoqda...")
        count = load_to_lmdb()
        print(f"✅ Bazaga yuklandi: {count:,} ta address.")
    else:
        print("✅ LMDB bazasi topildi. Tekshirishga tayyor.")

    while True:
        address = input("\n🔍 BTC addressni kiriting (chiqish uchun 'exit'): ").strip()
        if address.lower() == "exit":
            break
        if check_address(address):
            print("✅ Address RICHLISTDA mavjud.")
        else:
            print("❌ Address topilmadi.")
