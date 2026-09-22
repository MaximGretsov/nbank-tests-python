import random
import string


class RandomData:
    @staticmethod
    def generate_valid_deposit_amount() -> float:
        amount_in_cents = random.randint(2, 499_999)
        return amount_in_cents / 100

    @staticmethod
    def generate_negative_deposit_amount() -> float:
        amount_in_cents = random.randint(1, 500_000)
        return -(amount_in_cents / 100)

    @staticmethod
    def generate_deposit_amount_more_than_max() -> float:
        amount_in_cents = random.randint(500_002, 1_000_000)
        return amount_in_cents / 100

    @staticmethod
    def generate_non_existing_account_id_based(existing_account_id: int) -> int:
        offset = random.randint(100_000, 999_999)
        return existing_account_id + offset

    @staticmethod
    def generate_valid_transfer_amount() -> float:
        amount_in_cents = random.randint(2, 999_999)
        return amount_in_cents / 100

    @staticmethod
    def generate_negative_transfer_amount() -> float:
        amount_in_cents = random.randint(1, 1_000_000)
        return -(amount_in_cents / 100)

    @staticmethod
    def generate_transfer_amount_more_than_max() -> float:
        amount_in_cents = random.randint(1_000_002, 2_000_000)
        return amount_in_cents / 100

    @staticmethod
    def generate_transfer_amount_more_than_balance(current_balance: float) -> float:
        if current_balance >= 10_000:
            raise ValueError(
                "Current balance must be less than max transfer amount"
            )

        current_balance_in_cents = round(current_balance * 100)

        amount_in_cents = random.randint(
            current_balance_in_cents + 1,
            1_000_000
        )

        return amount_in_cents / 100

    @staticmethod
    def generate_valid_profile_name() -> str:
        return (
            RandomData._generate_random_letters_word()
            + " "
            + RandomData._generate_random_letters_word()
        )

    @staticmethod
    def generate_single_word_profile_name() -> str:
        return RandomData._generate_random_letters_word()

    @staticmethod
    def generate_three_word_profile_name() -> str:
        return (
            RandomData._generate_random_letters_word()
            + " "
            + RandomData._generate_random_letters_word()
            + " "
            + RandomData._generate_random_letters_word()
        )

    @staticmethod
    def generate_profile_name_with_leading_space() -> str:
        return " " + RandomData.generate_valid_profile_name()

    @staticmethod
    def generate_profile_name_with_trailing_space() -> str:
        return RandomData.generate_valid_profile_name() + " "

    @staticmethod
    def generate_profile_name_with_double_space() -> str:
        return (
            RandomData._generate_random_letters_word()
            + "  "
            + RandomData._generate_random_letters_word()
        )

    @staticmethod
    def generate_profile_name_with_special_character() -> str:
        return (
            RandomData._generate_random_letters_word()
            + " "
            + RandomData._generate_random_letters_word()
            + "%"
        )

    @staticmethod
    def generate_profile_name_with_digit() -> str:
        return (
            RandomData._generate_random_letters_word()
            + " "
            + RandomData._generate_random_letters_word()
            + "1"
        )

    @staticmethod
    def generate_profile_name_with_hyphen() -> str:
        return (
            RandomData._generate_random_letters_word()
            + " "
            + RandomData._generate_random_letters_word()
            + "-"
            + RandomData._generate_random_letters_word()
        )

    @staticmethod
    def generate_only_spaces_profile_name() -> str:
        spaces_count = random.randint(2, 10)
        return " " * spaces_count

    @staticmethod
    def _generate_random_letters_word() -> str:
        word_length = random.randint(3, 7)

        return ''.join(
            random.choices(
                string.ascii_letters,
                k=word_length
            )
        )

    @staticmethod
    def generate_username() -> str:
        return ''.join(
            random.choices(string.ascii_letters, k=10)
        )

    @staticmethod
    def generate_password() -> str:
        uppercase_part = ''.join(
            random.choices(string.ascii_uppercase, k=3)
        )
        lowercase_part = ''.join(
            random.choices(string.ascii_lowercase, k=5)
        )
        digits_part = ''.join(
            random.choices(string.digits, k=3)
        )

        return uppercase_part + lowercase_part + digits_part + "$"