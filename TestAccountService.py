
class Account:

    def __init__(self, initial_balance):
        self.current_balance = initial_balance
        self.available_balance = initial_balance
        self.vendor_id_and_amount_hold_map = {}
        self.id = id(self)

    def print_details(self):
        print("  Account Details:: "
              "  accountId:", self.id,
              "  current_balance:", self.current_balance,
              ", available_balance:", self.available_balance,
              ", vendor_id_and_amount_hold_map=", self.vendor_id_and_amount_hold_map)


class AccountService:

    def __init__(self):
        self.account_id_and_account_map = {}

    # create account method
    def create_account(self, initial_balance):
        account = Account(initial_balance)
        print("  Account created successfully with account_id:", account.id, " with initial balance", initial_balance)
        self.account_id_and_account_map[account.id] = account
        return account.id

    # Charge method
    def charge(self, account_id, amount):
        if account_id not in self.account_id_and_account_map:
            message = "  Invalid accountId:"+str(account_id)
            raise Exception(message)

        account = self.account_id_and_account_map.get(account_id)
        if account.available_balance < amount:
            message = "  No sufficient balance to charge in the  accountId:"+str(account_id)
            raise Exception(message)
        account.available_balance -= amount
        account.current_balance -= amount
        print("  Charge successful for amount:", amount, " in the account_id:", account.id)

    # Hold method
    def hold(self, account_id, vendor_id, amount):
        if account_id not in self.account_id_and_account_map:
            message = "  Invalid accountId:" + str(account_id)
            raise Exception(message)

        account = self.account_id_and_account_map.get(account_id)

        # for the given vendor, if already hold is there.
        if vendor_id in account.vendor_id_and_amount_hold_map:
            message = "  Already hold is present for vendor_id:" + str(vendor_id) \
                      + "in the  accountId:" + str(account_id)
            raise Exception(message)

        if account.available_balance < amount:
            message = "  Not sufficient balance to hold in the account_id:" + str(account_id)
            raise Exception(message)
        else:
            account.vendor_id_and_amount_hold_map[vendor_id] = amount
            account.available_balance -= amount
            print("  Hold is successful for vendor_id:",vendor_id, "with amount:", amount, " in the account_id:", account.id)

    # Settle hold method
    def settle_hold(self, account_id, vendor_id, actual_amount):
        if account_id not in self.account_id_and_account_map:
            message = "  Invalid accountId:" + str(account_id)
            raise Exception(message)

        account = self.account_id_and_account_map.get(account_id)

        # Check for the given vendor hold is present or not, If not
        if vendor_id not in account.vendor_id_and_amount_hold_map:
            message = "  Hold is not present for vendor_id:" + str(vendor_id)\
                      + " in the account_id:" +str(account_id)
            raise Exception(message)

        hold_amount = account.vendor_id_and_amount_hold_map[vendor_id]
        diff_amount = actual_amount - hold_amount
        if diff_amount > 0:
            if account.available_balance >= diff_amount:
                account.available_balance -= diff_amount
            else:
                account.available_balance += hold_amount
                del account.vendor_id_and_amount_hold_map[vendor_id]
                message = "  No sufficient fund to settle the Hold for vendor_id:" + str(vendor_id) \
                          + " in the account_id:" + str(account_id)+". So, releasing the hold amount."
                raise Exception(message)
        elif diff_amount < 0:
            account.available_balance -= diff_amount

        account.current_balance -= actual_amount
        del account.vendor_id_and_amount_hold_map[vendor_id]
        print("  Settle hold is successful for vendor_id:", vendor_id, "with amount:", actual_amount,
              " in the account_id:", account.id)

    # Print account details method
    def print_details(self, account_id):
        if account_id not in self.account_id_and_account_map:
            message = "  Invalid accountId:" + str(account_id)
            raise Exception(message)
        account = self.account_id_and_account_map.get(account_id)
        account.print_details()


# testing

def main():
    account_service = AccountService()
    run = True
    while run:
        display_options()
        try:
            choice = int(input("Enter your option:"))
            if choice == 0:
                run_test_case()
            elif choice == 1:
                try:
                    init_amount = float(input("Enter your initial amount:"))
                    account_id = account_service.create_account(init_amount)
                except Exception as ex:
                    print("Invalid Input")
            elif choice == 2:
                try:
                    account_id = int(input("Enter account_id:"))
                    amount = float(input("Enter charge amount:"))
                except Exception as ex:
                    print("Invalid Input")

                try:
                    account_service.charge(account_id, amount)
                except Exception as ex:
                    print(ex)
            elif choice == 3:
                try:
                    account_id = int(input("Enter account_id:"))
                    vendor_id = int(input("Enter vendor_id:"))
                    amount = float(input("Enter hold amount:"))
                except Exception as ex:
                    print("Invalid Input")
                try:
                    result = account_service.hold(account_id,vendor_id, amount)
                except Exception as ex:
                    print(ex)
            elif choice == 4:
                try:
                    account_id = int(input("Enter account_id:"))
                    vendor_id = int(input("Enter vendor_id:"))
                    amount = float(input("Enter settle hold amount:"))
                except Exception as ex:
                    print("Invalid Input")

                try:
                    result = account_service.settle_hold(account_id,vendor_id, amount)
                except Exception as ex:
                    print(ex)
            elif choice == 5:

                if not account_service.account_id_and_account_map:
                    print("Accounts not found.")
                else:
                    for account_id in account_service.account_id_and_account_map.keys():
                        account_service.print_details(account_id)
            elif choice == 6:
                run = False
            else:
                print("Invalid Choice")
        except Exception as ex:
            print("Invalid Choice:",choice)


def display_options():
    print("---------------------------------")
    print("0 --> Run existing test case")
    print("1 --> Create account")
    print("2 --> charge")
    print("3 --> Hold")
    print("4 --> Settle Hold")
    print("5 --> Display account details")
    print("6 --> Exit")
    print("---------------------------------")


def run_test_case():
    account_service = AccountService()
    print("==========================================test case report =================================================")
    init_amount = 1000
    available_balance = init_amount
    print("\n", "1.Creating new account with initial amount:", init_amount)
    account_id = account_service.create_account(init_amount)

    charge_mount = 2000
    print("\n", "2.Calling charge with charge amount:",charge_mount," which is greater than available balance:",
          available_balance)
    try:
        account_service.charge(account_id , charge_mount)
    except Exception as ex:
        print(ex)
    account_service.print_details(account_id)

    charge_mount = 100
    print("\n", "3.Calling charge with charge amount:", charge_mount, " which is lesser than available balance:",
          available_balance)
    account_service.charge(account_id , charge_mount)
    available_balance -= charge_mount
    account_service.print_details(account_id)

    more_hold_amount = 1000
    vendor_id = 1
    print("\n", "4.Calling hold for vendor id:",vendor_id, " with hold amount:",more_hold_amount,
          " which is greater than available balance:", available_balance)
    try:
        result = account_service.hold(account_id, vendor_id, more_hold_amount)
    except Exception as ex:
        print(ex)

    hold_amount = 500
    print("\n", "5.Calling hold for vendor id:",vendor_id, " with hold amount:",hold_amount,
          " which is lesser than available balance:", available_balance)
    try:
        result = account_service.hold(account_id, vendor_id, hold_amount)
        available_balance -= hold_amount
    except Exception as ex:
        print(ex)
    account_service.print_details(account_id)

    settle_hold_amount = 1000
    print("\n", "6.Calling settle hold for vendor id:",vendor_id, " with settle hold amount:", settle_hold_amount,
          " which is greater than available balance including hold amount:", available_balance+hold_amount)
    try:
        account_service.settle_hold(account_id, vendor_id, settle_hold_amount)
    except Exception as ex:
        available_balance += hold_amount
        print(ex)
    account_service.print_details(account_id)

    print("\n", "7. Once again calling hold for vendor id:", vendor_id, " with hold amount:", hold_amount,
          " which is lesser than available balance:", available_balance)
    try:
        account_service.hold(account_id, vendor_id, hold_amount)
        available_balance -= hold_amount
    except Exception as ex:
        print(ex)
    account_service.print_details(account_id)

    print("\n", "8.Calling settle hold for vendor id:",vendor_id, " with settle hold amount:", hold_amount,
          " which is lesser than available balance including hold amount:", available_balance+hold_amount)
    try:
        account_service.settle_hold(account_id, vendor_id, hold_amount)
    except Exception as ex:
        print(ex)
    account_service.print_details(account_id)

    print("==========================================End of test case report ==========================================")


if __name__ == '__main__':
    main()




