# Security Guidance

## Threat Model (Transfer Scenario)
This project is designed for **offline encryption** and manual sharing of ciphertext and keys.
The core risk comes from how you transmit those artifacts:

- **Ciphertext interception**: Attackers can copy ciphertext in transit, but without the key it should remain confidential.
- **Key interception**: If the key is exposed, the ciphertext can be decrypted.
- **Key + ciphertext exposure**: Sending both over the same channel defeats the purpose of encryption.
- **Clipboard leakage**: Clipboard contents can be read by malware or remote desktop software.

## Recommended Transfer Practices
1. **Separate channels**: Send ciphertext and key via different channels (e.g., email + secure messenger).
2. **Use a passphrase-protected key package**: Protect the key with a passphrase and share the passphrase via a different channel.
3. **Verify fingerprints**: Compare the key fingerprint out-of-band to detect tampering.
4. **Avoid long-lived storage**: Delete ciphertext/keys after use.
5. **Prefer TLS/secure transport**: If files must be sent via network, use trusted encrypted channels.

## Key Package Details
The key package uses PBKDF2-HMAC-SHA256 (200k iterations) to derive a key that encrypts the actual encryption key.
This allows the key to be transported safely as long as the passphrase remains secret.

## Limitations
- This tool does not manage identity verification or key exchange.
- Clipboard operations are convenient but risky in shared/remote environments.
- File encryption uses the same key material; protect the key and key package as rigorously as the ciphertext.
