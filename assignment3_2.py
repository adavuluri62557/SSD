# One-Time Pad Encryption
import secrets   # Used to create a random key
import string    # Provides A-Z letters

# Original message
plaintext = "MY NAME IS UNKNOWN"

# Remove spaces
message = plaintext.replace(" ", "")

# Create a random key with the same length as the message
key = ''.join(
    secrets.choice(string.ascii_uppercase)
    for _ in range(len(message))
)

# Convert letters to numbers
# A=0, B=1, C=2, ... Z=25
def text_to_numbers(text):
    return [ord(char) - ord('A') for char in text]

# Convert numbers back to letters
def numbers_to_text(numbers):
    return ''.join(
        chr(number + ord('A'))
        for number in numbers
    )

# Convert message and key to numbers
message_numbers = text_to_numbers(message)
key_numbers = text_to_numbers(key)

# Encrypt the message
# Formula: (Plaintext + Key) mod 26
cipher_numbers = [
    (p + k) % 26
    for p, k in zip(message_numbers, key_numbers)
]

# Convert encrypted numbers to letters
ciphertext = numbers_to_text(cipher_numbers)

# Display results
print("Plaintext :", message)
print("OTP Key   :", key)
print("Ciphertext:", ciphertext)