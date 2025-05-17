// File: vulnerable_app.cpp

/*
 * Description:
 * This C++ file represents a legacy backend component for a government kiosk service,
 * responsible for reading and processing citizen appointment information.
 * It includes typical security flaws found in unmanaged or AI-assisted C++ codebases.
 *
 * Vulnerabilities:
 * - Use of insecure functions (gets, strcpy, sprintf)
 * - Buffer overflow risk
 * - Null pointer dereference
 * - Unchecked malloc return
 * - Uninitialized variables
 * - Infinite loop without exit
 */

 #include <iostream>
 #include <cstring>
 #include <cstdlib>
 
 void loadCitizenData() {
    char name[50];
    std::cout << "Enter your full name: ";
    std::cin.getline(name, sizeof(name)); // ✅ Replaced unsafe gets()

    char buffer[100];
    snprintf(buffer, sizeof(buffer), "Hello %s, your appointment is booked.", name); // ✅ Safer than sprintf
    std::cout << buffer << std::endl;
}

 void logToFile(const char* message) {
     FILE* f = fopen("/var/log/booking.log", "a");
     if (f) {
         fprintf(f, "[LOG] %s\n", message);
         fclose(f);
     }
 }
 
 void allocateUnsafeMemory() {
     int* data = (int*)malloc(100 * sizeof(int));
     // No NULL check before use
     data[0] = 42; // May segfault if malloc fails
 }
 
 void process() {
     int status; // Uninitialized variable
     if (status == 0) {
         std::cout << "Processing as guest..." << std::endl;
     }
 }
 
 void runKioskLoop() {
     while (1) { // Infinite loop
         std::cout << ".";
     }
 }
 
 int main() {
     loadCitizenData();
     allocateUnsafeMemory();
     process();
     // runKioskLoop(); // Dangerous: uncommenting this will hang the system
     logToFile("Appointment system executed.");
     return 0;
 }
 