/* map a value from min_in-max_in to min_out-max_out 
//
// i personally use this for converting ffxiv character customization
// slider values into bone scale values for use in blender
*/

#include <iostream>
#include <string>

double mapRange(const double min_in, const double max_in, 
                const double min_out, const double max_out, 
                const double value){
    double slope = (max_out - min_out) / (max_in - min_in);
    
    return min_out + slope * (value - min_in);
}

int main(){
    double min_out;
    double max_out;

    double desiredScale;

    std::cout << "Initial range is 0 to 100. Input slider value: ";
    std::cin >> desiredScale;

    std::cout << "Input minimum of output range: ";
    std::cin >> min_out;
    std::cout << "Input maximum of output range: ";
    std::cin >> max_out;

    double finalScale = mapRange(0.0, 100.0, min_out, max_out, desiredScale);

    std::cout << "Final scale: " << finalScale << std::endl;

    return 0;
}
