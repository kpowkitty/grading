#include <iostream>
#include "LinkedBag.h"

int main() {
    // Create and populate first bag
    LinkedBag<int> bag1;
    bag1.add(10);
    bag1.add(20);
    bag1.add(30);

    // Test assignment operator
    LinkedBag<int> bag2;
    bag2.add(999);  // Give it different data first

    bag2 = bag1;  // Assignment operator called here

    // Verify bag2 has bag1's contents
    std::cout << "bag2 contents after assignment:" << std::endl;
    std::vector<int> items = bag2.toVector();
    for (int item : items) {
        std::cout << item << " ";
    }
    std::cout << std::endl;

    // Test that it's a deep copy (modify bag1, bag2 shouldn't change)
    bag1.add(40);
    bag1.clear();

    std::cout << "bag2 after modifying bag1:" << std::endl;
    items = bag2.toVector();
    for (int item : items) {
        std::cout << item << " ";
    }
    std::cout << std::endl;

    // Test self-assignment
    bag2 = bag2;
    std::cout << "bag2 after self-assignment:" << std::endl;
    items = bag2.toVector();
    for (int item : items) {
        std::cout << item << " ";
    }
    std::cout << std::endl;

    return 0;
}
