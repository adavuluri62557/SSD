public class assignment9 {

    // --- Primitive example ---
    public static void modifyPrimitive(int number) {
        number = number + 100;
        System.out.println("Inside method: " + number);
    }

    // --- Object example ---
    static class Account {
        double balance;
        Account(double balance) { this.balance = balance; }
    }

    public static void modifyObject(Account acct) {
        acct.balance = acct.balance + 100;
        System.out.println("Inside method: " + acct.balance);
    }

    public static void reassignObject(Account acct) {
        acct = new Account(9999);
        System.out.println("Inside reassign method: " + acct.balance);
    }

    public static void main(String[] args) {
        System.out.println("--- Primitive (pass by value) ---");
        int myNumber = 5;
        modifyPrimitive(myNumber);
        System.out.println("After method call: " + myNumber);

        System.out.println("\n--- Object (reference passed by value) ---");
        Account myAccount = new Account(500);
        modifyObject(myAccount);
        System.out.println("After modifyObject: " + myAccount.balance);

        reassignObject(myAccount);
        System.out.println("After reassignObject: " + myAccount.balance);
    }
}