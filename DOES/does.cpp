#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <unordered_map>
#include <vector>
#include <algorithm>
#include <chrono>
#include <thread>


using namespace std;

void remove_and(string& lines) {
    size_t start = 0;
    size_t end = lines.find('\n');

    while (end != string::npos) {
        if (end > start && lines[end - 1] == '&') {
            lines.erase(end - 1, 1); // Remove '&' if it is the last character in the line
        }
        start = end + 1;
        end = lines.find('\n', start);
    }

    // Check the last line
    if (!lines.empty() && lines.back() == '&') {
        lines.pop_back(); // Remove '&' if it is the last character in the last line
    }
}

string transformURL(const string& url) {
    unordered_map<string, string> params;
    stringstream ss(url.substr(url.find('?') + 1)); // Extract parameters and values

    string param;
    while (getline(ss, param, '&')) {
        string key = param.substr(0, param.find('='));
        string value = param.substr(param.find('=') + 1);
        value="ok";
        params[key] = value;
    }

    // Sort parameters alphabetically
    vector<pair<string, string>> sorted_params(params.begin(), params.end());
    sort(sorted_params.begin(), sorted_params.end());

    string base_url = url.substr(0, url.find('?') + 1);
    string transformed_url;
    string transformed_urls;

    // Generate transformed URL
    for (size_t i = 0; i < sorted_params.size(); ++i) {
        transformed_url += sorted_params[i].first + "=" + sorted_params[i].second;
        if (i < sorted_params.size() - 1) transformed_url += "&";
        transformed_urls +=  base_url + transformed_url + "\n";
        }
    remove_and(transformed_urls);
    return transformed_urls;
}

void transformURLsFromFile(const string& inputFilename, const string& outputFilename) {
    ifstream inputFile(inputFilename);
    ofstream outputFile(outputFilename);
    
    if (!inputFile.is_open()) {
        cerr << "Error: Unable to open input file: " << inputFilename << endl;
        return;
    }
    if (!outputFile.is_open()) {
        cerr << "Error: Unable to open output file: " << outputFilename << endl;
        return;
    }

    const int maxChunkSize = 1024; // Maximum chunk size in bytes
    string buffer;
    string line;

    while (inputFile) {
        int chunkSize = maxChunkSize;

        // Read a chunk from the input file
        getline(inputFile, buffer);

        while (!inputFile.eof() && buffer.size() < maxChunkSize) {
            getline(inputFile, line);
            buffer += '\n' + line; // Append line to buffer
            
            // Adjust chunk size if line is too long
            if (line.size() > maxChunkSize) {
                chunkSize = line.size();
            }
        }

        // Process lines within the chunk
        stringstream ss(buffer);
        while (getline(ss, line)) {
            outputFile << transformURL(line) ;
        }

        // Clear buffer for the next chunk
        buffer.clear();
    }

    inputFile.close();
    outputFile.close();

    cout << "Transformation completed successfully." << endl;
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

void copyFile(const std::string& inputFilename, const std::string& outputFilename) {
    std::ifstream inputFile(inputFilename, std::ios::binary);
    std::ofstream outputFile(outputFilename, std::ios::binary);

    if (!inputFile.is_open()) {
        std::cerr << "Error: Unable to open input file: " << inputFilename << std::endl;
        return;
    }
    if (!outputFile.is_open()) {
        std::cerr << "Error: Unable to open output file: " << outputFilename << std::endl;
        return;
    }

    // Set the buffer size (e.g., 4 KB)
    const size_t bufferSize = 4096;
    std::vector<char> buffer(bufferSize);

    while (!inputFile.eof()) {
        // Read a chunk of data from the input file
        inputFile.read(buffer.data(), bufferSize);
        
        // Get the number of bytes read
        size_t bytesRead = inputFile.gcount();
        
        // Write the data to the output file
        outputFile.write(buffer.data(), bytesRead);
    }

    // Close the files
    inputFile.close();
    outputFile.close();

    std::cout << "File copied successfully." << std::endl;
}

class Timer {
public:
    Timer() : start_time(chrono::high_resolution_clock::now()), running(true) {
        // Start the timer thread
        timer_thread = thread([this]() {
            while (running) {
                auto current_time = chrono::high_resolution_clock::now();
                auto duration = chrono::duration_cast<chrono::milliseconds>(current_time - start_time);
                cout << "\rElapsed time: " << duration.count() << " milliseconds." << flush;
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
        cout << "\rElapsed time: " << duration.count() << " milliseconds." << endl;
    }

private:
    chrono::high_resolution_clock::time_point start_time;
    thread timer_thread;
    bool running;
};

int main() {
     string inputFilename, outputFilename;

    cout << "Enter the path to the input file: ";
    getline(cin, inputFilename);

    cout << "Enter the path to the output file: ";
    getline(cin, outputFilename);

    Timer timer;
    string tempfile= outputFilename + "/../temp.txt";
    transformURLsFromFile(inputFilename, outputFilename);
    deduplicateFile(outputFilename, tempfile );
    copyFile(tempfile, outputFilename);
    eraseFileContents(tempfile);
    remove(tempfile.c_str());

    return 0;
}

