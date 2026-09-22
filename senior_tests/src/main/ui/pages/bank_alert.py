from enum import Enum


class BankAlert(str, Enum):
    USER_CREATED_SUCCESSFULLY = ("✅ User created successfully!")

    USERNAME_MUST_BE_BETWEEN_3_AND_15_CHARACTERS = ("Username must be between 3 and 15 characters")

    NEW_ACCOUNT_CREATED = ("✅ New Account Created! Account Number: ")

    GOOD_DEPOSIT = (
        "✅ Successfully deposited ${} "
        "to account ACC{}!"
    )

    BAD_DEPOSIT = ("❌ Please enter a valid amount.")

    PROFILE_UPDATED_SUCCESSFULLY = ("✅ Name updated successfully!")

    ENTER_VALID_NAME = ("Name must contain two words with letters only")

    GOOD_TRANSFER = (
        "✅ Successfully transferred ${} "
        "to account {}!"
    )

    AMOUNT_MUST_BE_MORE_THAN_MINIMUM = ("❌ Error: Transfer amount must be at least 0.01")

    REPEAT_TRANSFER_SUCCESS = (
        "✅ Transfer of ${} successful "
        "from Account {} to {}!")

    NO_MATCHING_USERS_FOUND = ("❌ No matching users found.")

    REPEAT_TRANSFER_FAILED = ("❌ Transfer failed: Please try again.")