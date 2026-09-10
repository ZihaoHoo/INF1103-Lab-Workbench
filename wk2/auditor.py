# HOO ZI HAO (2603028) Week 2 Lab

#region Global Variables
inventory_qty = 0
inventory_max_qty = 500
failed_entries = 0
#endregion

#region headers_formatted
def formattedHeader(message, char="*"):
    divider = char * len(message)
    return(f"{divider}\n{message}\n{divider}")
#endregion

#region Main Program
def main_program():
    print(formattedHeader("Welcome to the Smart Inventory Auditor!"))
#endregion

if __name__ == "__main__":
    main_program()