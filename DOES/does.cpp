#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <vector>
#include <unordered_set>
#include <algorithm>
#include <cctype>
#include <unordered_map>
#include <chrono>
#include <thread>

using namespace std;

const size_t BUFFER_SIZE = 4096; // Adjust the buffer size as needed

class Timer {
public:
    Timer() : start_time(chrono::high_resolution_clock::now()), running(true) {
        // Start the timer thread
        timer_thread = thread([this]() {
            while (running) {
                auto current_time = chrono::high_resolution_clock::now();
                auto duration = chrono::duration_cast<chrono::milliseconds>(current_time - start_time);
                cout << "\r\t\t\t\t\t\t\t\t\t\t\t\tElapsed time: " << duration.count() << " milliseconds." << flush;
                this_thread::sleep_for(chrono::milliseconds(100)); // Update every 100 milliseconds
            }
        });
    }

    ~Timer() {
        // Stop the timer thread
        running = false;
        if (timer_thread.joinable()) {
            timer_thread.join();
        }

        // Print the final elapsed time
        auto end_time = chrono::high_resolution_clock::now();
        auto duration = chrono::duration_cast<chrono::milliseconds>(end_time - start_time);
        cout << "\rElapsed time: " << duration.count() << " milliseconds.";
    }

private:
    chrono::high_resolution_clock::time_point start_time;
    thread timer_thread;
    bool running;
};

void processLine(const string& line, ofstream& output) {
    size_t equalPos = line.find('=');

    if (equalPos != string::npos) {
        string prefix = line.substr(0, equalPos);
        string remaining = line.substr(equalPos);

        // Remove leading and trailing whitespaces from remaining
        remaining.erase(0, remaining.find_first_not_of(" \t\n\r\f\v"));
        remaining.erase(remaining.find_last_not_of(" \t\n\r\f\v") + 1);

        vector<string> values;
        istringstream iss(remaining);
        string value;

        string modifiedline;
        modifiedline = prefix;
        // Split remaining part by '&'
        while (getline(iss, value, '&')) {
            values.push_back(value);
        }

        // Write the modified lines to the output file
        for (const auto& v : values) {
            modifiedline = modifiedline + v+ '&';
            output <<modifiedline << endl;
        }
    }
}

void writeok(const string& inputFilePath, const string& finalfile) {
    ifstream inputFile(inputFilePath);
    ofstream outputFile(finalfile, ios::out | ios::trunc);

    if (!inputFile.is_open() || !outputFile.is_open()) {
        cerr << "Error opening files." << endl;
        return;
    }

    string line;

    while (getline(inputFile, line)) {
        size_t lastEqualPos = line.find_last_of('=');

        if (lastEqualPos != string::npos) {
            //replace whatever comes after the last "=" sign with "ok"
            line.replace(lastEqualPos + 1, string::npos, "ok");
        }

        // Write the modified line to the output file
        outputFile << line << endl;
    }

    inputFile.close();
    outputFile.close();
    // cout<<"\r\nDone preparing the parameters to the kxss tool."<<endl;
}

string trim(const string& str) {
    auto start = str.find_first_not_of(" \t\r\n");
    auto end = str.find_last_not_of(" \t\r\n");
    return (start != string::npos && end != string::npos) ? str.substr(start, end - start + 1) : "";
}

void deduplicateFile(const string& inputFilePath, const string& outputFilePath) {
    ifstream inputFile(inputFilePath);
    ofstream outputFile(outputFilePath,ios::out);

    if (!inputFile.is_open()) {
        cerr << "Error opening input file: " << inputFilePath << endl;
        return;
    }

    if (!outputFile.is_open()) {
        cerr << "Error opening output file: " << outputFilePath << endl;
        inputFile.close();
        return;
    }

    unordered_map<string, int> lineCounts;
    string line;

    // First pass: Count occurrences of each line
    while (getline(inputFile, line)) {
        lineCounts[line]++;
    }

    // Second pass: Write only unique lines to the output file
    inputFile.clear(); // Reset file state
    inputFile.seekg(0); // Move back to the beginning

    while (getline(inputFile, line)) {
        if (lineCounts[line] > 0) {
            outputFile << line << endl;
            lineCounts[line] = 0; // Mark as written to avoid duplicates
        }
    }

    inputFile.close();
    outputFile.close();

    cout << "\r\nDuplicates removed succesfuly." << endl;
}

void eraseFileContents(const string& filePath) {
    ofstream outputFile(filePath, ios::out | ios::trunc);

    if (outputFile.is_open()) {
        cout << "\r\nContents of the temp file erased successfully." << endl;
    } else {
        cerr << "Error erasing file contents." << endl;
    }
}

int main() {
    
    cout.rdbuf(cout.rdbuf());
    cerr.rdbuf(cerr.rdbuf());
    
    string inputFilePath, finalfile, tempfile;

    //finalfile = "finalok.txt";

    cout << "Enter the path to the input file: ";
    getline(cin, inputFilePath);

    cout << "Enter the path to the output file: ";
    getline(cin, finalfile);
   
    tempfile =finalfile + "\\..\\temp.txt";

    Timer timer;

    ifstream inputFile(inputFilePath, ios::binary);
    ofstream outputFile(finalfile, ios::binary);

    if (!inputFile.is_open() || !outputFile.is_open()) {
        cerr << "Error opening files." << endl;
        return 1;
    }

    char buffer[BUFFER_SIZE];
    string remaining;

    while (inputFile.read(buffer, BUFFER_SIZE)) {
        stringstream ss(remaining + string(buffer, inputFile.gcount()));
        string line;

        while (getline(ss, line)) {
            processLine(line, outputFile);
        }

        remaining = line;
    }

    processLine(remaining, outputFile);

    inputFile.close();
    outputFile.close();

    writeok(finalfile,tempfile);

    //eraseFileContents(finalfile);

    deduplicateFile(tempfile,finalfile);

    eraseFileContents(tempfile); //just incase it does't get deleted in the next step
    
    remove(tempfile.c_str());

    cout << "\r\nProcessing completed. Check'"<<finalfile<<"' for results." << endl;
    cout <<"Done";
    
    return 0;
}