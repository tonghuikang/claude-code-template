def main():
    try:
        # Some operation that might raise an exception
        result = risky_operation()
        print(f"Success: {result}")
    except (ValueError, ZeroDivisionError) as e:
        print(f"An error occurred: {e}")


def risky_operation():
    """Example function that could raise exceptions."""
    value = int(input("Enter a number: "))
    return 100 / value


if __name__ == "__main__":
    main()
