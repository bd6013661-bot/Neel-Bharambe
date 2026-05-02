def main_menu():

    while True:

        print("")
        print("===== Storefront =====")
        print("1) Browse products")
        print("2) View cart")
        print("3) Checkout")
        print("4) Exit")
        print("")

        choice = input("Pick an option (1-4): ").strip()

        if choice == '1':
            print("Browsing products... (not implemented yet)")

        elif choice == '2':
            print("Viewing cart... (not implemented yet)")

        elif choice == '3':
            print("Checking out... (not implemented yet)")

        elif choice == '4':
            print("Exiting...")
            break

        else:
            print("That wasn't on the menu. Try again, and read it this time.")


main_menu()
