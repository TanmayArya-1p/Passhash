# Passhash
Store passwords locally with PBKDF2 encryption.

####  Default Master Password is `112358`

# Architecture

* Master Password used to access encrypted passwords
* Master Password verified with SHA256 HASH stored with pseudo-randomly generated hex as salts.
* Once verified,the encoded password is sent to a PBKDF2(Password-Based Key Derivation Function) Function which returns a unique Fernet.
* The returned Fernet is used to decrypt stored passwords.


