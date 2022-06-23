__global__ void detection(int *binimage, int *matrix){

    int global_index_thead_x = threadIdx.x + blockDim.x * blockIdx.x;
    int global_index_thead_y = threadIdx.y + blockDim.y * blockIdx.y;

    if(global_index_thead_x < $width_image && global_index_thead_y < $height_image){  
        int gray_Offset = global_index_thead_y * $width_image + global_index_thead_x;

        if(binimage[gray_Offset] == 255){
			if((global_index_thead_y >= 0) && (global_index_thead_y < (64 + $channels))){
				if((matrix[0] != 1) && (global_index_thead_x >= 0) && (global_index_thead_x < (64 + $channels))){
					matrix[0] = 1;
				}
				else if((matrix[1] != 1) && (global_index_thead_x >= (64 + $channels)) && (global_index_thead_x < (192 + $channels))){
					matrix[1] = 1;
				}
				else if((matrix[2] != 1) && (global_index_thead_x >= (192 + $channels)) && (global_index_thead_x < (448 - $channels))){
					matrix[2] = 1;
				}
				else if((matrix[3] != 1) && (global_index_thead_x >= (448 - $channels)) && (global_index_thead_x < (576 - $channels))){
					matrix[3] = 1;
				}
				else if((matrix[4] != 1) && (global_index_thead_x >= (576 - $channels)) && (global_index_thead_x < 640)){
					matrix[4] = 1;
				}
			}

			if((global_index_thead_y >= (64 + $channels)) && (global_index_thead_y < (448 - $channels))){
				if((matrix[5] != 1) && (global_index_thead_x >= 0) && (global_index_thead_x < (64 + $channels))){
					matrix[5] = 1;
				}
				else if((matrix[6] != 1) && (global_index_thead_x >= (64 + $channels)) && (global_index_thead_x < (192 + $channels))){
					matrix[6] = 1;
				}
				else if((matrix[7] != 1) && (global_index_thead_x >= (192 + $channels)) && (global_index_thead_x < (448 - $channels))){
					matrix[7] = 1;
				}
				else if((matrix[8] != 1) && (global_index_thead_x >= (448 - $channels)) && (global_index_thead_x < (576 - $channels))){
					matrix[8] = 1;
				}
				else if((matrix[9] != 1) && (global_index_thead_x >= (576 - $channels)) && (global_index_thead_x < 640)){
					matrix[9] = 1;
				}
			}
            
			if((global_index_thead_y >= (448 - $channels)) && (global_index_thead_y < 480)){
				if((matrix[10] != 1) && (global_index_thead_x >= 0) && (global_index_thead_x < (64 + $channels))){
					matrix[10] = 1;
				}
				else if((matrix[11] != 1) && (global_index_thead_x >= (64 + $channels)) && (global_index_thead_x < (192 + $channels))){
					matrix[11] = 1;
				}
				else if((matrix[12] != 1) && (global_index_thead_x >= (192 + $channels)) && (global_index_thead_x < (448 - $channels))){
					matrix[12] = 1;
				}
				else if((matrix[13] != 1) && (global_index_thead_x >= (448 - $channels)) && (global_index_thead_x < (576 - $channels))){
					matrix[13] = 1;
				}
				else if((matrix[14] != 1) && (global_index_thead_x >= (576 - $channels)) && (global_index_thead_x < 640)){
					matrix[14] = 1;
				}
			}
        }
    }
}
