# USB FlashKey Auth

USB FlashKey Auth is a Python module for simple hardware-based authentication using a USB flash drive on Windows.

The project allows you to turn a regular USB flash drive into a physical access “key” tied to a specific device and (optionally) a secret. It is suitable for protecting applications, scripts, or internal tools without using network licenses or servers.

---

## Features

- 🔐 USB flash drive authentication
- 🧩 Binding the key to a specific USB drive (PNPDeviceID)
- 🔑 Support for an additional secret
- 🖥 Secret binding options:
  - to the Machine GUID (system HWID)
  - to the hardware (changes with upgrades)
  - or completely without a secret
- 👻 Hidden key file on the flash drive
- ⚙️ Automatic detection of USB drives

---

## How It Works

1. A hidden `.usbkey` file is created on the flash drive
2. The file stores a SHA-256 hash: `hash = sha256(PNPDeviceID + secret)`
3. During verification, the library:
   - searches for connected USB drives
   - reads `.usbkey`
   - recalculates the hash and compares it

If the hash matches — access is granted.

---

## Requirements

- Windows (uses WMI and WinAPI)
- Python 3.9+
- Packages:
  - `wmi`
  - `pywin32` (indirectly, for `winreg` and WinAPI)

---

## Installing Dependencies

```bash
pip install wmi pywin32
````

---

## Usage

An example usage of the module is provided in the file `test.py`.

### Initializing a Key (One-Time Setup)

```python
from flashkey import FlashKeyAuth

auth = FlashKeyAuth()
auth.init_key()  # auth.check_key()
```

During initialization, you will be prompted to choose a secret mode:

1. Auto-generated
2. Manually entered
3. System HWID
4. Hardware HWID
5. No secret

### Key Verification

```python
from flashkey import FlashKeyAuth

auth = FlashKeyAuth(secret="YOUR_SECRET")  # or omit, the module will ask via input

if auth.check_key():
    print("Access granted")
else:
    print("Key not found or invalid")
```

---

## Limitations

* ❗ Works only on Windows
* ❗ USB drive must be physically connected (no virtual devices)
* ❗ Not intended to protect against professional reverse engineering

---

## Possible Use Cases

* Running internal utilities
* Protecting scripts and admin tools
* Offline licensing without a server
* Physical “key” for applications

---

## Security

This project is **not** intended to provide high-level cryptographic security. It implements a hardware access factor, not DRM.

---
