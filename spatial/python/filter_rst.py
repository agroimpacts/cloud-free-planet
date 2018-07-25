#################################################
#This code is design to solve the memory problem in filter.py when processing a large image file
#by read, analyze, and write a block of pixel at a time.
#Another sustaintial change of this code is that each function is a stand-alone function, and 
#works individually, i.e., each funciton starts from open image(s), read pixel values, does analysis and 
# creates output file(s).
#################################################


import gdal
import numpy as np
from scipy import ndimage
import sys
print(sys.version)



def maxmin_img(m,out_name,*args):
    """
    This function creates a maximum or minimum image, which each pixel takes the 
    max or minimum value at that position from the input bands.
    The purpose of this funciton is to help extract shadows and clouds, assuming 
    that the shadow's maximum reflectance is low, whereas the cloud's minimum 
    reflectance is still high.
    
    m           - specify either "max" or "min"
    out_name    - The out put image name. e.g., D:\output.rst
    file_format - This version of code works only for .rst format
    *args       - given any numbers of images in a given format, RST or GTiff.
    """
    try:
        #1. Get the GeoTransform and Projection from the first band of the input bands
        #(bands should have same geotransform and projection)
        #Also get the columns and rows
        in_ds_template = gdal.Open(args[0])
        in_ds_GeoTransform = in_ds_template.GetGeoTransform()
        in_ds_Projection = in_ds_template.GetProjection()

        cols = in_ds_template.GetRasterBand(1).XSize
        rows = in_ds_template.GetRasterBand(1).YSize

        #2. Create a list of opened bands for later iterations
        bands= [] 
        for arg in args:
            bands.append(gdal.Open(arg)) 

        
        #3. Create a output file. The gdal driver will actually create a rst file and a rdc file. 
        # The rdc file holds metadata.  We copied the metadata from input band, since they are mostly same 
        # except the max/value and displayed max/min value.
        rst_driver = gdal.GetDriverByName('rst')
        out_ds = rst_driver.Create(out_name, cols, rows,1,3)
        out_band = out_ds.GetRasterBand(1)

        #4. use nested for loop to read 640x640 block each time for all input bands, and append these
        #band blocks into a list.  Then use np.max/np.min method to get max/min image along the axis-2,
        # which is the penetration direction of a pixel thorugh a stack of bands. 
        block_size = 640
        for col_start in range(0, cols, block_size): 
            if col_start + block_size < cols:
                col_read = block_size
            else:
                col_read = cols - col_start
            for row_start in range(0, rows, block_size):
                if row_start + block_size < rows:
                    row_read = block_size
                else:
                    row_read = rows - row_start


                bands_blocks = []
                for band in bands:
                    current_block= band.ReadAsArray(col_start, row_start, col_read, row_read)
                    bands_blocks.append(current_block)
                
                block_stack = np.dstack(bands_blocks)
                if m == "max":
                    m_arry = np.amax(block_stack,2).astype(np.int16)
                elif m =="min":
                    m_arry = np.amin(block_stack,2).astype(np.int16)
                out_band.WriteArray(m_arry, col_start, row_start)

        #out_band.FlushCache()
        out_ds.SetGeoTransform(in_ds_GeoTransform)
        out_ds.SetProjection(in_ds_Projection)

        del out_ds
    except:
        return "Failed to generate max/min image."
        #with open(out_name.replace(out_name[-3:],"rdc"),"w") as out_rdc:
        #    for line in meta_data:
        #        print(line.rstrip("\n"))
        #        out_rdc.write(line)

        #write rdc for test in Terrset
        #out_rdc = out_name[:-3]+"rdc"
        #with open(out_rdc, "w") as f:

def reclass(cd,in_name,out_name, thre_val):
    """
    Output is a boolin image where 0 is the pixels not meet the condition,
    and 1 means the pixels that meet the condition.
    cd       - ">" or "<"
    in_name  - input image name, with path
    out_name - out put image name, with path
    thre_val - threshold value 
    """
    try:
        #1. Open the input image and get the GeoTransform, Projection, 
        #cols and rows.
        in_ds = gdal.Open(in_name)
        in_ds_GeoTransform = in_ds.GetGeoTransform()
        in_ds_Projection = in_ds.GetProjection()

        in_band = in_ds.GetRasterBand(1)
        cols = in_band.XSize
        rows = in_band.YSize

        #2.Create a output file. The gdal driver will actually create a rst file and a rdc file. 
        #The rdc file holds metadata.  The output metadata will set by using the input metadata, 
        # except the max/min value and display max/min value.
        rst_driver = gdal.GetDriverByName('rst')
        out_ds = rst_driver.Create(out_name, cols, rows,1,3) # here 1 means 1 band in the image,3 means integer datatype
        out_band = out_ds.GetRasterBand(1)

        block_size = 640
        for col_start in range(0, cols, block_size): 
            if col_start + block_size < cols:
                col_read = block_size
            else:
                col_read = cols - col_start
            for row_start in range(0, rows, block_size):
                if row_start + block_size < rows:
                    row_read = block_size
                else:
                    row_read = rows - row_start

                current_block = in_band.ReadAsArray(col_start, row_start, col_read, row_read)
                
                if cd == ">":
                    reclass_arry = np.where(current_block > thre_val, 1, 0).astype(np.int16)
                elif cd =="<":
                    reclass_arry = np.where(current_block < thre_val, 1, 0).astype(np.int16)
                
                out_band.WriteArray(reclass_arry, col_start, row_start)
        
        out_ds.SetGeoTransform(in_ds_GeoTransform)
        out_ds.SetProjection(in_ds_Projection)  

        del out_ds
    except:
        return "Failed to reclass image."

def filter_window(in_name, out_name, filter_size,cd):
    """
    in_name     - input image name with path
    out_name    - output image name with path
    filter_size - e.g., 7 stands for a 7x7 filter
    cd          - "max" or min
    """
    try:
        #1. Open the input image and get the GeoTransform, Projection, 
        #cols and rows.
        in_ds = gdal.Open(in_name)
        in_ds_GeoTransform = in_ds.GetGeoTransform()
        in_ds_Projection = in_ds.GetProjection()
        
        in_band = in_ds.GetRasterBand(1)
        cols = in_band.XSize
        rows = in_band.YSize
        
        #2.Create a output file. The gdal driver will actually create a rst file and a rdc file. 
        #The rdc file holds metadata.  The output metadata will set by using the input metadata, 
        # except the max/min value and display max/min value.
        rst_driver = gdal.GetDriverByName('rst')
        out_ds = rst_driver.Create(out_name, cols, rows,1,3) # here 1 means 1 band in the image,3 stands for integer datatype

        out_band = out_ds.GetRasterBand(1)

        #3.read 7 lines from the image each time for a 7x7 filter.  Create a current_row, and let numpy read three lines above it,
        #,three lines below it, and itself.  Althogh all the pixel will be processed in this 7 lines, only the centerline(4th line) 
        # will be written as output each time.
        #The scipy's ndimage.maximum_filter deals with the situation when there is no enough neibor for a 7x7 filter,
        #by using as much neighbor as it can.
        #We only need to deal with the first or last three lines in the image when they are the centerline, 
        # so they won't create three lines above or below then thus made the image out of index.
        
        if cd =="max":
            current_row  = 0
            while current_row <= rows-1:
                if current_row -3 < 0:
                    current_block = in_band.ReadAsArray(0, 0, cols, current_row + 4) #col_start, row_start, col read, row read
                    filtered_block = ndimage.maximum_filter(current_block, filter_size)
                    out_band.WriteArray(filtered_block[-4:-3], 0, current_row) #data, col_start, rows_start

                elif current_row -3 >=0 and current_row+3 <= rows-1:
                    current_block = in_band.ReadAsArray(0, current_row-3, cols, 7)
                    filtered_block = ndimage.maximum_filter(current_block, filter_size)
                    out_band.WriteArray(filtered_block[3:4], 0, current_row) #data, col_start, rows_start


                if current_row +3 > rows-1: 
                    current_block = in_band.ReadAsArray(0, current_row-3, cols, rows- 1 - current_row+4)              
                    filtered_block = ndimage.maximum_filter(current_block, filter_size)
                    out_band.WriteArray(filtered_block[3:4], 0, current_row) #data, col_start, rows_start

                current_row +=1

        elif cd =="min":
            current_row  = 0
            while current_row <= rows-1:
                if current_row -3 < 0:
                    current_block = in_band.ReadAsArray(0, 0, cols, current_row + 4) #col_start, row_start, col read, row read
                    filtered_block = ndimage.minimum_filter(current_block, filter_size)
                    out_band.WriteArray(filtered_block[-4:-3], 0, current_row) #data, col_start, rows_start

                elif current_row -3 >=0 and current_row+3 <= rows-1:
                    current_block = in_band.ReadAsArray(0, current_row-3, cols, 7)
                    filtered_block = ndimage.minimum_filter(current_block, filter_size)
                    out_band.WriteArray(filtered_block[3:4], 0, current_row) #data, col_start, rows_start


                if current_row +3 > rows-1: 
                    current_block = in_band.ReadAsArray(0, current_row-3, cols, rows- 1 - current_row+4)              
                    filtered_block = ndimage.minimum_filter(current_block, filter_size)
                    out_band.WriteArray(filtered_block[3:4], 0, current_row) #data, col_start, rows_start

                current_row +=1
        
        out_ds.SetGeoTransform(in_ds_GeoTransform)
        out_ds.SetProjection(in_ds_Projection)
    except:
        print(current_row,current_row+3, current_row-3)
        return "Failed to apply spatial filter to the input image."

def masks(in_image, mask_img, out_name):
    try:
        #1. open the input image and read as array
        in_ds = gdal.Open(in_image)
        in_band = in_ds.GetRasterBand(1)
        in_array = in_ds.ReadAsArray()

        #2. Get metadata from input image
        in_ds_GeoTransform = in_ds.GetGeoTransform()
        in_ds_Projection = in_ds.GetProjection()
        cols = in_band.XSize
        rows = in_band.YSize
        #get mask and read as array
        mask_array = gdal.Open(mask_img).ReadAsArray()

        #apply the mask array on the input array
        #array_mask = np.ma.make_mask(mask_array)
        img_masked = np.where(mask_array == 1, in_array, 0)

        #output the array to rst
        rst_driver = gdal.GetDriverByName('rst')
        out_ds = rst_driver.Create(out_name, cols, rows,1,3) # here 1 means 1 band in the image,3 means integer datatype
        out_band = out_ds.GetRasterBand(1)

        out_band.WriteArray(img_masked, 0, 0)
        
        out_ds.SetGeoTransform(in_ds_GeoTransform)
        out_ds.SetProjection(in_ds_Projection)     
    except:
        return "Failed to return masked image."

def cloud_shadow(cloud_name, shadow_name, out_name):
    try:
        cloud_ds = gdal.Open(cloud_name)
        cloud_band = cloud_ds.GetRasterBand(1)

        shadow_ds = gdal.Open(shadow_name)
        shadow_band = shadow_ds.GetRasterBand(1)
        cols = cloud_band.XSize
        rows = cloud_band.YSize

        cloud_array = cloud_ds.ReadAsArray()
        shadow_array = shadow_ds.ReadAsArray()

        cloud_and_shadow = cloud_array*2 + shadow_array
        #write output image and metadata
        in_ds_GeoTransform = cloud_ds.GetGeoTransform()
        in_ds_Projection = cloud_ds.GetProjection()

        rst_driver = gdal.GetDriverByName('rst')
        out_ds = rst_driver.Create(out_name, cols, rows,1,3) # here 1 means 1 band in the image,3 means integer datatype
        out_band = out_ds.GetRasterBand(1)
        out_band.WriteArray(cloud_and_shadow, 0, 0)


        out_ds.SetGeoTransform(in_ds_GeoTransform)
        out_ds.SetProjection(in_ds_Projection)  

        del out_ds
           
    except:
        return "Failed to make cloud_shadow image."


#create a loop for files:
file_list = [
"20180228_095050_102f_3B_AnalyticMS_SR_",
"20180228_095154_1025_3B_AnalyticMS_SR_",
"20180303_095157_1014_3B_AnalyticMS_SR_",
"20180303_105144_1050_3B_AnalyticMS_SR_",
"20180306_095153_0f52_3B_AnalyticMS_SR_",
"20180310_095138_102e_3B_AnalyticMS_SR_",
"20180314_095225_1042_3B_AnalyticMS_",
"20180314_095225_1042_3B_AnalyticMS_SR_",
"20180314_095225_1042_3B_AnalyticMS_SR_win_",
"20180314_095229_1042_3B_AnalyticMS_",
"20180314_095229_1042_3B_AnalyticMS_SR_"

]



for thresh_val in range(3150, 3800, 50):
    i = 1
    for fn in file_list:

        print("processing {}th image, {}".format(i, fn))
        #1.Set the input band path and names; out put path
        in_path = r"D:\Extracting_Clouds\cloud_shadow_test_rst\\"
        in_name = fn

        out_path = r"D:\Extracting_Clouds\cloud_shadow_test_{}\img{}\\".format(str(thresh_val),str(i))

        b1 = in_path + in_name + "b1.rst"
        b2 = in_path + in_name + "b2.rst"
        b3 = in_path + in_name + "b3.rst"
        b4 = in_path + in_name + "b4.rst"

        i+=1



        #2.Get the max and min image
        maxmin_img("max", out_path + "max_img.rst",b1,b2,b3,b4)
        maxmin_img("min", out_path + "min_img.rst",b1,b2,b3,b4)

        filter_window(out_path + "max_img.rst", out_path + "max7x7.rst",7,"max")
        filter_window(out_path + "min_img.rst", out_path +"min7x7.rst",7,"min")

        #Shadow and Water
        reclass("<", out_path + "max7x7.rst", out_path + "Shadow_and_Water.rst", 2000)

        #Cloud 
        reclass(">", out_path + "min7x7.rst", out_path + "Cloud.rst", thresh_val)

        #Land
        reclass(">", b4, out_path + "Land.rst", 1000)

        #Shadow
        masks(out_path + "Shadow_and_Water.rst", out_path + "Land.rst", out_path + "Shadow.rst")

        #put shadow and cloud together

        cloud_shadow(out_path + "Cloud.rst", out_path + "Shadow.rst", out_path + "Cloud_Shadow.rst")




#use text file accessing method to read and write metadata.
#            with open(args[0].replace(args[0][-3:],"RDC")) as rdc: #readin col and rows, for determin the block size
#                meta_data = rdc.readlines()
#                cols = int(meta_data[4].split(": ")[1].rstrip("\n"))
#                rows = int(meta_data[5].split(": ")[1].rstrip("\n"))



