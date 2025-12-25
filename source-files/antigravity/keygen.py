import argparse
import dlnk_license_manager

def main():
    parser = argparse.ArgumentParser(description="dLNk AI License Generator (Admin Tool)")
    parser.add_argument("--days", type=int, default=30, help="Number of days the license is valid for")
    parser.add_argument("--owner", type=str, default="Customer", help="Name of the license owner")
    
    args = parser.parse_args()
    
    print("-" * 50)
    print(f" [*] Generating dLNk AI License for: {args.owner}")
    print(f" [*] Duration: {args.days} days")
    print("-" * 50)
    
    try:
        key = dlnk_license_manager.generate_license(days_valid=args.days, owner=args.owner)
        print("\n[SUCCESS] LICENSE KEY GENERATED:\n")
        print(key)
        print("\n" + "-" * 50)
        print("Copy this key and give it to the customer.")
        
    except Exception as e:
        print(f"\n[ERROR] Failed to generate key: {e}")

if __name__ == "__main__":
    main()
