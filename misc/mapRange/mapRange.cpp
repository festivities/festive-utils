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
    /* CHANGE THESE VALUES */
    const double min_out_X = 0.92;
    const double min_out_Y = 0.8;
    const double min_out_Z = 0.816;

    const double max_out_X = 1.08;
    const double max_out_Y = 1.2;
    const double max_out_Z = 1.184;

    const double desiredScale = 39;
    /* CHANGE THESE VALUES */

    double finalScale_X = mapRange(0.0, 100.0, min_out_X, max_out_X, desiredScale);
    double finalScale_Y = mapRange(0.0, 100.0, min_out_Y, max_out_Y, desiredScale);
    double finalScale_Z = mapRange(0.0, 100.0, min_out_Z, max_out_Z, desiredScale);

    const double &finalScale_Y_Blender = finalScale_Z;
    const double &finalScale_Z_Blender = finalScale_Y;

    std::cout << "X, Y, Z:                           " << finalScale_X 
              << ", " << finalScale_Y << ", " << finalScale_Z << std::endl;
    std::cout << "X, Y, Z (for Z-up (i.e. Blender)): " << finalScale_X 
              << ", " << finalScale_Y_Blender << ", " << finalScale_Z_Blender 
              << std::endl;

    return 0;
}
