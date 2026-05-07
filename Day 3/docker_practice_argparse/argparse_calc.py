import argparse
import os
import sys

def parse_args():
    parser = argparse.ArgumentParser(
        description="Sum two numbers from CLI args, fallback to default env variables"
    )
    parser.add_argument(
        "--num1", type=float, help="First number (CLI > env)"
    )
    parser.add_argument(
        "--num2", type=float, help="Second number (CLI > env)"
    )
    return parser.parse_args() 

def get_number(value, env_var_name):
    # Get number from CLI arg, fallback to env variable
    if value is not None:
        return value
    env_val = os.getenv(env_var_name)
    if env_val is not None:
        try:
            return float(env_val)
        except ValueError:
            print(f"Error: Environment variable {env_var_name} must be a number.", file=sys.stderr)
            sys.exit(1)
    return None

def main():
    args = parse_args()

    # Get numbers from CLI or environment
    num1 = get_number(args.num1, "NUM1")
    num2 = get_number(args.num2, "NUM2")

    # Validate presence
    if num1 is None or num2 is None:
        print("Error: You must provide both numbers via CLI or environment variables NUM1 and NUM2.", file=sys.stderr)
        sys.exit(1)

    # Perform sum
    result = num1 + num2
    print(f"The sum of {num1} and {num2} is {result}")

if __name__ == "__main__":
    main()