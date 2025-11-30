#ifndef TESTING_HPP
	#define TESTING_HPP

	#include <string>
	#include <vector>
	#include <sstream>
	
	typedef struct {
		std::vector<char> input_list, rotated_list;
		int k;
		bool is_palindrome;
	} testCase;


	/**
	 * This function reads structured test data from the specified file. The expected format is:
	 * 
	 *     <Number of tests>
	 *     <list of characters as a string>
	 *     <k (rotation amount)>
	 *     <expected list after rotation>
	 *     <is palindrome after rotation?> (true/false, case-insensitive)
	 *     -- repeated for each test case --
	 *
	 * Each block of four lines after the header is parsed into a `testCase` struct,
	 * which is then added to the `testCases` vector.
	 *
	 * @param fileName The name of the file containing the test cases.
	 * @param testCases A reference to a vector of `testCase` structs where the parsed data will be stored.
	 * @return `true` if the file was successfully opened and all test cases were read;
	 *         `false` if the file could not be opened.
	 *
	 */
	bool readTestCases(std::string fileName, std::vector<testCase>& testCases);

#endif
