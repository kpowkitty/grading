#include "testing.hpp"
#include <iostream>
#include <vector>
#include <fstream>
#include <string>
#include <sstream>
#include <cctype>
#include <algorithm>

using namespace std;

bool readTestCases(string fileName, vector<testCase>& testCases){
	string nextLine;
	ifstream testFile (fileName);
	
	if (testFile.is_open()){
		int numberTests;
		getline (testFile, nextLine);
		istringstream iss(nextLine);
		iss >> numberTests;

		for (int test = 1; test <= numberTests; test ++){
			// all varibales will be initialized with values from file
			testCase tcase;

			// read the list of input characters
			getline(testFile, nextLine);
			tcase.input_list.assign(nextLine.begin(), nextLine.end());

			// read value in the next line
			getline(testFile, nextLine);
			iss.clear();
			iss.str(nextLine);
			iss >> tcase.k;

			// read the rotated characters
			getline(testFile, nextLine);
			tcase.rotated_list.assign(nextLine.begin(), nextLine.end());

			// read is_palindrome
			getline(testFile, nextLine);
			std::transform(nextLine.begin(), nextLine.end(), nextLine.begin(),
                   [](unsigned char c) { return std::tolower(c); });
			tcase.is_palindrome = (nextLine == "true");

			// add new test case to the list 
			testCases.push_back(tcase);


		}
		
		// close file reader
		testFile.close();
		return true;

	}else{
		return false;
	}
}
