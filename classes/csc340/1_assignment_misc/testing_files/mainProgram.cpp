#include "testing.hpp"
#include <iostream>
#include <vector>
#include <algorithm>
#include <fstream>
#include <string>
#include <sstream>
// TO DO 
// add necessary include for your library
#include "myLibrary.hpp"

using namespace std;


int main () {
	// testCase data structure is defined in testing.h
	vector<testCase> testCases;
	bool verbose = true; 

	/* test cases are defined in the file testFileName
	The file is expected to have to following formatting: 
	<Number of tests>
	<list of characters as a string> e.g. 12334 or hello
	<k> e.g. 3
	<expected list after rotation> e.g. 33412
	<is palindrome after rotation?> e.g. false
	-- REPEAT -- for as many test cases as <Number of tests>
	*/
	string testFileName = "test_cases.txt";

	if (readTestCases(testFileName, testCases)){
		int rotate_pass = 0; 
		int palind_pass = 0; 

		for (int i = 0; i < testCases.size(); i++){
			testCase tc = testCases[i];

			// test your function
			bool funcTestRotate = true; 
			bool funcTestPalindrome = true; 

			// ---------- Call the functions you will implement --
			rotateList(tc.input_list, tc.k);
			bool check_palindrome = isPalindrome(tc.rotated_list);
			// ---------------------------------------------------

			// Convert the vectors to strings
			std::string result(tc.input_list.begin(), tc.input_list.end());
			std::string expected(tc.rotated_list.begin(), tc.rotated_list.end());
			// Check correctness
			funcTestRotate = (result == expected);
			funcTestPalindrome = (tc.is_palindrome == check_palindrome);

			// Diplay details if verbose == true
			if (verbose){
				cout << "-------------- Testcase " << i+1 << endl;
				cout << "rotateList   -- " << (funcTestRotate ? "PASSED" : "* FAILED *") << endl;
				cout << "isPalimdrome -- " << (funcTestPalindrome ? "PASSED" : "* FAILED *") << endl;
			}

			// count the number of tests passed
			if (funcTestRotate) { rotate_pass++;}
			if (funcTestPalindrome) { palind_pass++;}


		}
		cout << "rotateList   - tests passed: " << rotate_pass << "/" << testCases.size() << endl;
		cout << "isPalimdrome - tests passed: " << palind_pass << "/" << testCases.size() << endl;   

	}else{
		cout << "Testing file was not found!" << endl ;
	}
	return 0;
}
