
;---------------------------------------------------------------------------
;      ATSA method for masking cloud, shadow in Landsat time-series images or
;      similar multi-spectral time-series data        
;              
;                            Coded by Xiaolin Zhu
;                      Contact info: zhuxiaolin55@gmail.com
;              Department of Land Surveying and Geo-Informatics
;                     The Hong Kong Polytechnic University
;                     
;                     co-developer: Eileen H. Helmer 
;           International Institute of Tropical Forestry, USDA Forest Service
;           
;                                
;   Update history: 2018-05-26: first version released
;                       
;                *This code is copyright to Dr. Xiaolin Zhu*
;Reference: Zhu,X.,and Helmer,E.H. An automatic method for screening clouds and 
;cloud shadows in optical satellite image time series in cloudy regions, 
;Remote Sensing of Environment, Volume 214, 2018, Pages 135-153
;----------------------------------------------------------------------------

;open the image

Pro GetData,ImgData = ImgData,ns = ns,nl = nl,nb = nb,Data_Type = Data_Type,$
    FileName = FileName,Map_info = map_Info, Fid = Fid
    Filter = ['all file;*.*']
    Envi_Open_File,FileName,R_Fid = Fid
    Envi_File_Query,Fid,ns = ns,nl = nl,nb = nb,Data_Type = Data_Type
    map_info = envi_get_map_info(fid=Fid)
    dims = [-1,0,ns - 1 ,0,nl - 1]
    case Data_Type Of
        1:ImgData = BytArr(ns,nl,nb)    ;  BYTE  Byte
        2:ImgData = IntArr(ns,nl,nb)    ;  INT  Integer
        3:ImgData = LonArr(ns,nl,nb)    ;  LONG  Longword integer
        4:ImgData = FltArr(ns,nl,nb)    ;  FLOAT  Floating point
        5:ImgData = DblArr(ns,nl,nb)    ;  DOUBLE  Double-precision floating
        6:ImgData = COMPLEXARR(ns,nl,nb); complex, single-precision, floating-point
        9:ImgData = DCOMPLEXARR(ns,nl,nb);complex, double-precision, floating-point
        12:ImgData = UINTARR(ns,nl,nb)   ; unsigned integer vector or array
        13:ImgData = ULONARR(ns,nl,nb)   ;  unsigned longword integer vector or array
        14:ImgData = LON64ARR(ns,nl,nb)   ;a 64-bit integer vector or array
        15:ImgData = ULON64ARR(ns,nl,nb)   ;an unsigned 64-bit integer vector or array
    EndCase
    For i = 0,nb-1 Do Begin
       Dt = Envi_Get_Data(Fid = Fid,dims = dims,pos=i)
       ImgData[*,*,i] = Dt[*,*]
    EndFor
End


Function Compute_HOT,data_blue,data_red,rmin,rmax,n_bin,slop=slop,intercept=intercept
  bin_size=(rmax-rmin)/float(n_bin)
  x=fltarr(n_bin)
  y=fltarr(n_bin)
  ii=0
  ;find samples on clear line
  for i=0, n_bin-1, 1 do begin
    ind_bin=where(data_blue ge rmin+i*bin_size and data_blue lt rmin+(i+1)*bin_size, num_bin)
    if (num_bin ge 20) then begin
      x_bin=data_blue[ind_bin]
      y_bin=data_red[ind_bin]
      ;remove outliers
      ind_good=where(y_bin le mean(y_bin)+3.0*stddev(y_bin), num_good)
      x_bin=x_bin[ind_good]
      y_bin=y_bin[ind_good]
      order=sort(y_bin)
      top_num=min([20, ceil(0.01*num_good)])
      x_bin_select=x_bin[order[num_good-top_num:num_good-1]]
      y_bin_select=y_bin[order[num_good-top_num:num_good-1]]
      x[ii]=mean(x_bin_select)
      y[ii]=mean(y_bin_select)
      ii=ii+1
    endif
  endfor

  ind_0=where(x gt 0, num_sample)
  x=x[ind_0]
  y=y[ind_0]
  if (num_sample ge 0.5*n_bin) then begin  ;make sure enough sample for clear-line regression
     ;compute slop of clear line
     result = Ladfit( x, y)
     slop=result[1]
     intercept=result[0]
     if (result[1] le 1.5) then begin  ;correct abnormal slop
       result[1]=1.5
       result[0]=mean(y)-result[1]*mean(x)
       slop=0
       intercept=0
     endif
  endif else begin  ;if no enough sample
     result=[mean(y)-1.5*mean(x),1.5]
     slop=0
     intercept=0
  endelse
  hot_img=abs(data_blue*result[1]-data_red+result[0])/((1.0+result[1]^2))^0.5
  return,hot_img
End

Function K_means,data,N_interation,k_class  ;data is n*m matrix, n is number of variables, m is number of samples
;get initial center
size_data=size(data)
n_variable=size_data[1]
n_sample=size_data[2]

;get initial center
center=fltarr(n_variable,k_class)
for i_v=0,n_variable-1, 1 do begin
    meanv=mean(data[i_v,*])
    sdv=stddev(data[i_v,*])
    lower=max([meanv-2.0*sdv,min(data[i_v,*])])
    upper=min([meanv+2.0*sdv,max(data[i_v,*])])
    interval=(upper-lower)/(k_class)
    center[i_v,*]=lower+(indgen(k_class)+0.5)*interval
endfor

diff=100
time=0
class_label=intarr(n_sample)

while diff gt 0 and time le N_interation do BEGIN
   ;classify all samples
   class_label0=class_label 
   ;Work arrays.
   WorkRow = REPLICATE(1.0, 1, n_variable) + 0.0
   WorkCol = REPLICATE(1.0, 1, k_class) + 0.0
   for Sample = 0L, n_sample-1 do begin
     Vector = data[*,Sample] # WorkCol - center
     Metric = WorkRow # (ABS(Vector))^2
     class_label[Sample] = (WHERE(Metric eq MIN(Metric)))[0]
   endfor
   
   ;update center
   for ic=0,k_class-1, 1 do begin
      ind_C=where(class_label eq ic)
      center[*,ic]=mean(data[*,ind_C],DIMENSION=2)
   endfor
   
   ;find the change
   change=where( class_label-class_label0 ne 0, diff)
   
   time=time+1
 ENDWHILE
 
 return,center 
end

;*******************************************************************
;                         main program
;*******************************************************************

pro  ATSA

;set the following parameters
dn_max=10000  ;maximum value of DN, e.g. 7-bit data is 127, 8-bit is 255
tempfile='C:\Users\lsxlzhu.LSGI\Desktop\ATSA update 20180526\Temp' ; folder for storing intermediate results
background=0  ;DN value of background or missing values, such as SLC-off gaps
buffer=1    ;width of buffer applied to detected cloud and shadow, recommend 1 or 2 

;parameters for HOT caculation and cloud detection
;------------------------------
n_image=18   ; number of images in the time-series
n_band=5     ; numebr of bands of each image
blue_b=1    ; band index of blue band, note: MSS does not have blue, use green as blue
green_b=2   ; band index of green band
red_b=3     ; band index of red band
nir_b=4     ; band index of nir band
swir_b=5    ; band index of swir band
A_cloud=0.5 ; threshold to identify cloud (mean+A_cloud*sd), recommend 0.5-1.5, smaller values can detect thinner clouds
maxblue_clearland=dn_max*0.15; estimated maximum blue band value for clear land surface
maxnir_clearwater=dn_max*0.05; estimated maximum nir band value for clear water surface

;parameters for shadow detection
;------------------------------
shortest_d=7.0       ;shortest distance between shadow and cloud, unit is pixel resolution
longest_d=50.0  ;longest distance between shadow and its corresponding cloud, unit is "pixel",can be set empirically by inspecting images
B_shadow=1.5 ;  threshold to identify shadow (mean-B_shadow*sd), recommend 1-3, smaller values can detect lighter shadows
;------------------------------


 t0=systime(1)                  ;Initial time

;open landsat image time-series
     FileName0= Dialog_PickFile(title = 'open time-series images:')    
     GetData,ImgData=data,ns = ns,nl = nl,nb = nb,Data_Type = Data_Type,FileName = FileName0,Map_info = map_Info, Fid = Fid1
     data=float(data)
     
 ;open water mask    
     FileName= Dialog_PickFile(title = 'open water mask data (water is with 0 value):')
     GetData,ImgData=water,ns = ns,nl = nl,FileName = FileName,Map_info = map_Info,Fid = Fid1
     
     ;open sun angle data
     FileName= Dialog_PickFile(title = 'open sun angle txt file:')
     Data1 = fltarr(2, n_image)
     openr, lun, FileName, /get_lun
     readf, lun, Data1
     free_lun, lun
     
     
         
     ;col and row index
     row_ind=intarr(ns,nl)
     col_ind=intarr(ns,nl)
     for i=0,ns-1,1 do begin
       col_ind[i,*]=i
     endfor
     for i=0,nl-1,1 do begin
       row_ind[*,i]=i
     endfor
     
         
;***** caculate HOT as cloud index*********
mask=bytarr(ns,nl,n_image)+1
HOT=fltarr(ns,nl,n_image)
rmin0=0.01*dn_max    ; minmum DN value of blue band for computing clear line
rmax=maxblue_clearland   ; maximum DN value of blue band for computing clear line
n_bin=50.0  ; number of bins between rmin and rmax

HOT_slop_land=fltarr(n_image)
HOT_int_land=fltarr(n_image)
;for land surface
for ii=0,n_image-1, 1 do begin  
  ind_l=where(water eq 1 or data[*,*,n_band*ii+nir_b-1] ge dn_max*0.1 and data[*,*,n_band*ii+nir_b-1] ne background, num_l) 
  if (num_l gt 0) then begin
   data_blue=(data[*,*,n_band*ii+blue_b-1])[ind_l]
   ind_valid=where(data_blue ge rmin0 and data_blue le rmax, num_valid)
   if (num_valid gt 500) then begin                    ;make sure enough samples to compute clear-sky line
       data_red=(data[*,*,n_band*ii+red_b-1])[ind_l]
       temp=HOT[*,*,ii]
       rmin=min(data_blue[ind_valid])
       temp[ind_l]=Compute_HOT(data_blue,data_red,rmin,rmax,n_bin,slop=slop,intercept=intercept)
       HOT[*,*,ii]=temp
       HOT_slop_land[ii]=slop
       HOT_int_land[ii]=intercept
    endif
  endif
endfor

;find images totally covered by clouds or unreasonable clear-sky line
ind_t=where(HOT_slop_land eq 0, num_t)
if (num_t lt n_image) then begin
   mean_slop=mean((HOT_slop_land[0,*])[where(HOT_slop_land[0,*] ne 0)])
   mean_int=mean((HOT_int_land[0,*])[where(HOT_int_land[0,*] ne 0)])
endif else begin
   mean_slop=1.5  ;for extreme case: no image can get valid clear-skye line
   mean_int=0
endelse

if (num_t gt 0) then begin             ;use average slop for those totally covered images
  for it=0, num_t-1, 1 do begin
    data_blue=data[*,*,n_band*ind_t[it]+blue_b-1]
    data_red=data[*,*,n_band*ind_t[it]+red_b-1]
    HOT[*,*,ind_t[it]]=abs(data_blue*mean_slop-data_red+mean_int)/((1.0+mean_slop^2))^0.5
  endfor
endif
  
  ;for water surface
for ii=0,n_image-1, 1 do begin     
  ind_w=where(water eq 0 and data[*,*,n_band*ii+nir_b-1] lt dn_max*0.1 and data[*,*,n_band*ii+nir_b-1] ne background, num_w)
  if (num_w gt 0) then begin
  data_nir=(data[*,*,n_band*ii+nir_b-1])[ind_w]
  data_blue=(data[*,*,n_band*ii+blue_b-1])[ind_w]
  rminw=max([min(data_nir),0])
  rmaxw=rminw+maxnir_clearwater
  n_binw=30

  ind_valid=where(data_nir ge rminw and data_nir le rmaxw, num_valid)
  if (num_valid gt 500) then begin
    temp=HOT[*,*,ii]
    temp[ind_w]=Compute_HOT(data_nir,data_blue,rminw,rmaxw,n_binw,slop=slop,intercept=intercept)
    HOT[*,*,ii]=temp
  endif else begin                       ;if all water are covered by clouds, compute HOT for land and water together
    data_blue=data[*,*,n_band*ii+blue_b-1]
    data_red=data[*,*,n_band*ii+red_b-1]
    HOT[*,*,ii]=abs(data_blue*mean_slop-data_red+mean_int)/((1.0+mean_slop^2))^0.5
  endelse
  endif
   
  ;exclude background and missing gaps: these pixels marked as class 3 and HOT=0
  ind_back=where(data[*,*,n_band*ii+nir_b-1] eq background, num_back)
  if (num_back gt 0) then begin
    temp=mask[*,*,ii]
    temphot=HOT[*,*,ii]
    temp[ind_back]=3
    temphot[ind_back]=0
    mask[*,*,ii]=temp
    HOT[*,*,ii]=temphot
  endif
endfor

print,'finish cloud index calculation!'
FileName =tempfile+'\hot_image'
Envi_Write_Envi_File,HOT,Out_Name = FileName,Map_info = map_Info

print, 'time used', floor((systime(1)-t0)/3600), 'h',floor(((systime(1)-t0) mod 3600)/60),'m',(systime(1)-t0) mod 60,'s'


;step 1 get initial mask from k-means classification
;collect samples using systematic sampling method
n_sample_kmean=10000.0
;convert water to a size with with shadow_new
water_n=bytarr(ns,nl,n_image)
for ib=0,n_image-1, 1 do begin
  water_n[*,*,ib]=water
endfor
;for land surface
land_cloud_p=where(mask ne 3 and water_n eq 1,num_land_cloud,/L64)
if (num_land_cloud gt 100) then begin
n_sample_kmean=min([n_sample_kmean,num_land_cloud])
inter_sample=floor(num_land_cloud/n_sample_kmean)
index_sample=indgen(n_sample_kmean)*inter_sample  ;find the location of samples
sample_cloud=fltarr(1,n_sample_kmean)
sample_cloud[0,*]=HOT[land_cloud_p[index_sample]] ;extract cloud index of samples and store them in a vector

;use k-means to classify HOT samples into two classes
center_class=K_means(sample_cloud,50,3)
print,'HOT centers of clear, thin and thick cloudy pixels on land:',center_class

;;polt histogram
;pdf = HISTOGRAM(sample_cloud, LOCATIONS=xbin)
;phisto = PLOT(xbin, pdf, TITLE='Histogram', XTITLE='Pixel value', YTITLE='Frequency', AXIS_STYLE=1, COLOR='red')
  
;classify each image by k-means centers
for ib=0,n_image-1, 1 do begin
  ind_cloud_ib=where(mask[*,*,ib] ne 3 and water eq 1)
  cloud_i=(HOT[*,*,ib])[ind_cloud_ib]
  dis_c1=abs(cloud_i-center_class[0])
  dis_c2=abs(cloud_i-center_class[1])
  temp=mask[*,*,ib]
  temp[ind_cloud_ib]=(dis_c1 ge dis_c2)+1
  mask[*,*,ib]=temp
endfor
endif
Th_initial=fltarr(2)
Th_initial[1]=(center_class[0]+center_class[1])/2.0

;for Water surface
n_sample_kmean=10000.0
water_cloud_p=where(mask ne 3 and water_n eq 0,num_water_cloud,/L64)
if (num_water_cloud gt 100) then begin
n_sample_kmean=min([n_sample_kmean,num_water_cloud])
inter_sample=floor(num_water_cloud/n_sample_kmean)
index_sample=indgen(n_sample_kmean)*inter_sample  ;find the location of samples
sample_cloud=fltarr(1,n_sample_kmean)
sample_cloud[0,*]=HOT[water_cloud_p[index_sample]] ;extract cloud index of samples and store them in a vector

;use k-means to classify HOT samples into two classes
center_class=K_means(sample_cloud,50,3)
print,'HOT centers of clear, thin and thick cloudy pixels on water:',center_class

;classify each image by k-means centers
for ib=0,n_image-1, 1 do begin
  ind_cloud_ib=where(mask[*,*,ib] ne 3 and water eq 0)
  cloud_i=(HOT[*,*,ib])[ind_cloud_ib]
  dis_c1=abs(cloud_i-center_class[0])
  dis_c2=abs(cloud_i-center_class[1])
  temp=mask[*,*,ib]
  temp[ind_cloud_ib]=(dis_c1 ge dis_c2)+1
  mask[*,*,ib]=temp
endfor
endif

Th_initial[0]=(center_class[0]+center_class[1])/2.0

;remove isoloate cloud pixels in initial cloud mask
mask0=mask
for ii=0,n_image-1, 1 do begin 
    for i=0, ns-1, 1 do begin
      for j=0, nl-1, 1 do begin
        ;moving window
        if (mask[i,j,ii] eq 2) then begin
          a1=max([0, i-2])
          a2=min([ns-1, i+2])
          b1=max([0, j-2])
          b2=min([nl-1, j+2])
          mask_win=mask0[a1:a2,b1:b2,ii]
          ind_c=where(mask_win eq 2, num_c)
          if (num_c le 7 ) then mask[i,j,ii]=1        ;remove isolate cloud pixels
        endif
      endfor
    endfor 
endfor
mask0=0

print,'finish initial cloud detection'
print, 'time used', floor((systime(1)-t0)/3600), 'h',floor(((systime(1)-t0) mod 3600)/60),'m',(systime(1)-t0) mod 60,'s'

;a glable threshold for detect cloud in a time seires with clear points<2
 indc=where(mask eq 2)
 meanv=mean(HOT[indc])
 sdv=stddev(HOT[indc])
 g_th=meanv-1.0*sdv
     
; get mask for cloud pixels from HOT time-series
for i=0,ns-1,1 do begin
  for j=0,nl-1,1 do begin
      
    ;judge cloud
    ;only use samples<theshold to compute the mean and sd
    ind_valid=where(mask[i,j,*] ne 2 and mask[i,j,*] ne 3,num_nonc)
    if (num_nonc ge 2) then begin
      b2_mean=mean((HOT[i,j,*])[ind_valid])
      b2_sd=stddev((HOT[i,j,*])[ind_valid])
      Th_initial_ij=Th_initial[water[i,j]]
      b2_range=max((HOT[i,j,*])[ind_valid])-min((HOT[i,j,*])[ind_valid])
      adjust_T=(Th_initial_ij-b2_range)/(Th_initial_ij+b2_range)
      ;refine initial cloud
      ind_ini_cloud=where(HOT[i,j,*] le b2_mean+(adjust_T+A_cloud)*b2_sd and mask[i,j,*] eq 2, num_miss_cloud)
      if (num_miss_cloud gt 0) then begin
        temp=mask[i,j,*]
        temp[ind_ini_cloud]=1
        mask[i,j,*]=temp
      endif
      ;Add missed clouds
      ind_cloud=where(HOT[i,j,*] gt b2_mean+(adjust_T+A_cloud)*b2_sd and data[i,j,n_band*indgen(n_image)+nir_b-1] gt dn_max*0.1 and mask[i,j,*] ne 3, num_cloud)
      if (num_cloud gt 0) then begin
        temp=mask[i,j,*]
        temp[ind_cloud]=2
        mask[i,j,*]=temp
      endif
    endif else begin      
      ind_cloud=where(HOT[i,j,*] gt g_th and mask[i,j,*] ne 3, num_cloud)
      if (num_cloud gt 0) then begin
        temp=mask[i,j,*]
        temp[ind_cloud]=2
        mask[i,j,*]=temp
      endif
    endelse
       
    endfor
 endfor
; 

;remove isoloate cloud pixels by an iterative process
for ii=0,n_image-1, 1 do begin
  diff=1000
  itime=0
 while (diff ge 5 and itime le 5) do begin
   mask0=mask[*,*,ii]
   for i=0, ns-1, 1 do begin
     for j=0, nl-1, 1 do begin
       ;moving window
       if (mask[i,j,ii] eq 2) then begin
         a1=max([0, i-2])
         a2=min([ns-1, i+2])
         b1=max([0, j-2])
         b2=min([nl-1, j+2])
         mask_win=mask0[a1:a2,b1:b2]
         ind_c=where(mask_win eq 2, num_c)
         if (num_c le 7 ) then mask[i,j,ii]=1        ;missmarked if isolate
       endif
     endfor
   endfor
   diff=total(abs(mask[*,*,ii]- mask0))
   itime=itime+1
 endwhile
endfor
 

 
 ;buffer cloud by a window
 cloud=mask
 for i=0,ns-1,1 do begin
   for j=0,nl-1,1 do begin
     for ii=0,n_image-1, 1 do begin

       ;get the buffer zone
       if (mask[i,j,ii] eq 2) then begin
         a1=max([0, i-buffer])
         a2=min([ns-1, i+buffer])
         b1=max([0, j-buffer])
         b2=min([nl-1, j+buffer])
         ind_nonback=where(mask[a1:a2,b1:b2,ii] ne 3)
         temp=cloud[a1:a2,b1:b2,ii]
         temp[ind_nonback]=2
         cloud[a1:a2,b1:b2,ii]=temp
       endif

     endfor
   endfor
 endfor
 mask=cloud

print,'finish final cloud detection!'
print, 'time used', floor((systime(1)-t0)/3600), 'h',floor(((systime(1)-t0) mod 3600)/60),'m',(systime(1)-t0) mod 60,'s'


;*********detect shadows***************

;find possible shadow area
data1=data1/180.0*3.1415926
longest_d=min([longest_d,ns-1,nl-1])
h_high=longest_d/(((tan(data1[0,*])*sin(data1[1,*]))^2+(tan(data1[0,*])*cos(data1[1,*]))^2)^0.5)
h_low=shortest_d/(((tan(data1[0,*])*sin(data1[1,*]))^2+(tan(data1[0,*])*cos(data1[1,*]))^2)^0.5)

shadow_image=bytarr(ns,nl,n_image)
shadow_edge=bytarr(ns,nl,n_image)

for ii=0,n_image-1, 1 do begin
  mask0=bytarr(ns,nl)
  
  num_int=ceil((h_high[ii]-h_low[ii])/3.0)
  height=h_low[ii]+indgen(num_int)*3.0

 
  num_int1=ceil((h_high[ii]-1)/3.0)
  height1=1+indgen(num_int1)*3.0
  
  start_x1=round(-height[0]*tan(data1[0,ii])*sin(data1[1,ii]))
  start_y1=round(height[0]*tan(data1[0,ii])*cos(data1[1,ii]))
  end_x1=round(-height[num_int-1]*tan(data1[0,ii])*sin(data1[1,ii]))
  end_y1=round(height[num_int-1]*tan(data1[0,ii])*cos(data1[1,ii]))
  
  ;there are four cases for the shadow shifting from clouds
  if (end_x1 le 0 and end_y1 le 0) then begin 
    for ih=0, num_int-1, 1 do begin
      shift_x1=round(-height[ih]*tan(data1[0,ii])*sin(data1[1,ii]))
      shift_y1=round(height[ih]*tan(data1[0,ii])*cos(data1[1,ii]))
      mask_last=mask0
      mask0[0:ns-1+shift_x1,0:nl-1+shift_y1]=mask[-shift_x1:ns-1,-shift_y1:nl-1,ii] 
      shadow_image[*,*,ii]=(mask0 eq 2) or (mask_last eq 2) or (shadow_image[*,*,ii] eq 1)
    endfor
  endif
  
  if (end_x1 le 0 and end_y1 gt 0) then begin
    for ih=0, num_int-1, 1 do begin
      shift_x1=round(-height[ih]*tan(data1[0,ii])*sin(data1[1,ii]))
      shift_y1=round(height[ih]*tan(data1[0,ii])*cos(data1[1,ii]))
      mask_last=mask0
      mask0[0:ns-1+shift_x1,shift_y1:nl-1]=mask[-shift_x1:ns-1,0:nl-1-shift_y1,ii]
      shadow_image[*,*,ii]=(mask0 eq 2) or (mask_last eq 2) or (shadow_image[*,*,ii] eq 1)
    endfor
  endif
  
  if (end_x1 gt 0 and end_y1 le 0) then begin
    for ih=0, num_int-1, 1 do begin
      shift_x1=round(-height[ih]*tan(data1[0,ii])*sin(data1[1,ii]))
      shift_y1=round(height[ih]*tan(data1[0,ii])*cos(data1[1,ii]))
      mask_last=mask0
      mask0[shift_x1:ns-1,0:nl-1+shift_y1]=mask[0:ns-1-shift_x1,-shift_y1:nl-1,ii]
      shadow_image[*,*,ii]=(mask0 eq 2) or (mask_last eq 2) or (shadow_image[*,*,ii] eq 1)
    endfor
  endif
  
  if (end_x1 gt 0 and end_y1 gt 0) then begin
    for ih=0, num_int-1, 1 do begin
      shift_x1=round(-height[ih]*tan(data1[0,ii])*sin(data1[1,ii]))
      shift_y1=round(height[ih]*tan(data1[0,ii])*cos(data1[1,ii]))
      mask_last=mask0
      mask0[shift_x1:ns-1,shift_y1:nl-1]=mask[0:ns-1-shift_x1,0:nl-1-shift_y1,ii]
      shadow_image[*,*,ii]=(mask0 eq 2) or (mask_last eq 2) or (shadow_image[*,*,ii] eq 1)
    endfor
  endif
  
      ;for edge: 4 cases     
   if (end_x1 le 0 and end_y1 le 0) then begin 
      shadow_edge[ns-1+end_x1:ns-1,*,ii]=99 
      shadow_edge[*,nl-1+end_y1:nl-1,ii]=99     
   endif
  
  if (end_x1 le 0 and end_y1 gt 0) then begin
      shadow_edge[ns-1+end_x1:ns-1,*,ii]=99 
      shadow_edge[*,0:end_y1,ii]=99  
  endif
  
  if (end_x1 gt 0 and end_y1 le 0) then begin
      shadow_edge[0:end_x1,*,ii]=99 
      shadow_edge[*,nl-1+end_y1:nl-1,ii]=99  
  endif
  
  if (end_x1 gt 0 and end_y1 gt 0) then begin
      shadow_edge[0:end_x1,*,ii]=99 
      shadow_edge[*,0:end_y1,ii]=99   
  endif

endfor

;overlay possible shadow to cloud mask
mask2=mask
ind_shadow_all=where(shadow_image eq 1 and mask2 eq 1)
mask2[ind_shadow_all]=0
ind_shadow_edge=where(shadow_edge eq 99 and mask2 eq 1)
mask2[ind_shadow_edge]=99

;buffer possible shadow by 5*5 window
possible_shadow=mask2
for i=0,ns-1,1 do begin
  for j=0,nl-1,1 do begin
    for ii=0,n_image-1, 1 do begin

      ;get the buffer zone
      if (possible_shadow[i,j,ii] eq 0) then begin
        a1=max([0, i-2])
        a2=min([ns-1, i+2])
        b1=max([0, j-2])
        b2=min([nl-1, j+2])
        ind_nonback=where(mask2[a1:a2,b1:b2,ii] eq 1,num_cad)
        if (num_cad gt 0) then begin
           temp=mask2[a1:a2,b1:b2,ii]
           temp[ind_nonback]=0
           mask2[a1:a2,b1:b2,ii]=temp
        endif
      endif
    endfor
  endfor
endfor
shadow_image=0
print,'finish potential shadow location estimation!'

FileName =tempfile+'\potential_shadow_zone'
Envi_Write_Envi_File,mask2,Out_Name = FileName,Map_info = map_Info
print, 'time used', floor((systime(1)-t0)/3600), 'h',floor(((systime(1)-t0) mod 3600)/60),'m',(systime(1)-t0) mod 60,'s'

;compute initial shadow index
shadow=fltarr(ns,nl,n_image)

;compute the propotion of cloud in each image
p_clear_land=fltarr(n_image)
for ii=0,n_image-1, 1 do begin
  ind_l=where(water eq 1 or data[*,*,n_band*ii+nir_b-1] ge dn_max*0.1 and mask2[*,*,ii] eq 1, num_l)
  p_clear_land[ii]=num_l
endfor
;find image with least clouds
land_least_cloud=(where(p_clear_land eq max(p_clear_land)))[0]

for ii=0,n_image-1, 1 do begin

  ind_l=where(water eq 1 or data[*,*,n_band*ii+nir_b-1] ge dn_max*0.1 and mask[*,*,ii] le 1, num_l)
  ind_comon=where(water eq 1 and mask2[*,*,ii] eq 1 and mask2[*,*,land_least_cloud] eq 1, num_comon)

  if (num_comon gt 100) then begin
    gain1=stddev((data[*,*,n_band*land_least_cloud+nir_b-1])[ind_comon])/stddev((data[*,*,n_band*ii+nir_b-1])[ind_comon])
    bias1=mean((data[*,*,n_band*land_least_cloud+nir_b-1])[ind_comon])-gain1*mean((data[*,*,n_band*ii+nir_b-1])[ind_comon])
    gain2=stddev((data[*,*,n_band*land_least_cloud+swir_b-1])[ind_comon])/stddev((data[*,*,n_band*ii+swir_b-1])[ind_comon])
    bias2=mean((data[*,*,n_band*land_least_cloud+swir_b-1])[ind_comon])-gain2*mean((data[*,*,n_band*ii+swir_b-1])[ind_comon])
  endif else begin
    gain1=1
    bias1=0
    gain2=1
    bias2=0
  endelse
  ;for land surface
  if (num_l gt 0) then begin
    data5=(data[*,*,n_band*ii+nir_b-1])[ind_l]
    data6=(data[*,*,n_band*ii+swir_b-1])[ind_l]
    data5=gain1*data5+bias1
    data6=gain2*data6+bias2
    temp=shadow[*,*,ii]
    temp[ind_l]=data5+data6
    shadow[*,*,ii]=temp
  endif

  ;for water
  ind_w=where(water eq 0 and data[*,*,n_band*ii+nir_b-1] lt dn_max*0.1 and mask[*,*,ii] le 1, num_w)
  if (num_w gt 0) then begin
    data_2=(data[*,*,n_band*ii+blue_b-1])[ind_w]
    data_3=(data[*,*,n_band*ii+green_b-1])[ind_w]
    temp=shadow[*,*,ii]
    temp[ind_w]=data_2+data_3
    shadow[*,*,ii]=temp
  endif
endfor

;adjust the 1st image
shadow[*,*,0]=1.4*(data[*,*,3]+data[*,*,4])

FileName =tempfile+'\shadow_index'
Envi_Write_Envi_File,shadow,Out_Name = FileName,Map_info = map_Info
print, 'finish shadow index', floor((systime(1)-t0)/3600), 'h',floor(((systime(1)-t0) mod 3600)/60),'m',(systime(1)-t0) mod 60,'s'


;compute new shadow index
shadow_new=fltarr(ns,nl,n_image)

;base shadow image from maximum value of the time-series
shadowbase=max(shadow,DIMENSION=3)

;*******************************
;use IDW function in IDL
;use buffer pixels as input
;buffer cloud by a window
shadow_buffer=mask2
for i=0,ns-1,1 do begin
  for j=0,nl-1,1 do begin
    for ii=0,n_image-1, 1 do begin
      ;get the buffer zone
      if (mask2[i,j,ii] eq 0) then begin
        a1=max([0, i-5])
        a2=min([ns-1, i+5])
        b1=max([0, j-5])
        b2=min([nl-1, j+5])
        ind_nonback=where(mask2[a1:a2,b1:b2,ii] eq 1 or mask2[a1:a2,b1:b2,ii] eq 99, num_valid)
        if (num_valid gt 0) then begin
          temp=shadow_buffer[a1:a2,b1:b2,ii]
          temp[ind_nonback]=10
          shadow_buffer[a1:a2,b1:b2,ii]=temp
        endif
      endif
    endfor
  endfor
endfor

for ii=0,n_image-1, 1 do begin

  ;for land surface
  ind_l_good=where(water eq 1  and shadow_buffer[*,*,ii] eq 10, num_l_good)
  ind_l_shadow=where(water eq 1  and mask2[*,*,ii] eq 0, num_l_shadow)

  if (num_l_good gt 100 and num_l_shadow gt 0) then begin  ;if the image has both good pixels and potential shadow pixels
    shadow_good=(shadow[*,*,ii])[ind_l_good]
    col_ind_good=col_ind[ind_l_good]
    row_ind_good=row_ind[ind_l_good]
    col_ind_shadow=col_ind[ind_l_shadow]
    row_ind_shadow=row_ind[ind_l_shadow]
    ;spatial interpolation by InverseDistance
    ; The following example requires triangulation.
    TRIANGULATE, col_ind_good, row_ind_good, tr
    miss_p=mean(shadowbase[ind_l_shadow])
    ;grid=GRIDDATA(col_ind_good,row_ind_good,shadow_good, XOUT=col_ind_shadow,YOUT=row_ind_shadow)
    grid=GRIDDATA(col_ind_good,row_ind_good,shadow_good,METHOD='InverseDistance',TRIANGLES=tr, MIN_POINTS=100,XOUT=col_ind_shadow,YOUT=row_ind_shadow,MISSING=miss_p)
    ;PRINT,'idw done'
    temp=shadow_new[*,*,ii]
    temp[ind_l_shadow]=(shadow[*,*,ii])[ind_l_shadow]-grid
    shadow_new[*,*,ii]=temp
  endif else begin
    if (num_l_shadow gt 0) then begin
      temp=shadow_new[*,*,ii]
      temp[ind_l_shadow]=(shadow[*,*,ii])[ind_l_shadow]-shadowbase[ind_l_shadow]
      shadow_new[*,*,ii]=temp
    endif
  endelse

  ;print,'finish land'
  ;for water
  ind_w_good=where(water eq 0 and shadow_buffer[*,*,ii] eq 10, num_w_good)
  ind_w_shadow=where(water eq 0 and mask2[*,*,ii] eq 0, num_w_shadow)

  if (num_w_good gt 100 and num_w_shadow gt 0) then begin  ;if the image has both good pixels and potential shadow pixels
    shadow_good=(shadow[*,*,ii])[ind_w_good]
    col_ind_good=col_ind[ind_w_good]
    row_ind_good=row_ind[ind_w_good]
    col_ind_shadow=col_ind[ind_w_shadow]
    row_ind_shadow=row_ind[ind_w_shadow]
    ;spatial interpolation by InverseDistance
    TRIANGULATE, col_ind_good, row_ind_good, tr
    ;grid=GRIDDATA(col_ind_good,row_ind_good,shadow_good, XOUT=col_ind_shadow,YOUT=row_ind_shadow)
    miss_p=mean(shadowbase[ind_w_shadow])
    grid=GRIDDATA(col_ind_good,row_ind_good,shadow_good,METHOD='InverseDistance',TRIANGLES=tr,MIN_POINTS=100, XOUT=col_ind_shadow,YOUT=row_ind_shadow,MISSING=miss_p)
    temp=shadow_new[*,*,ii]
    temp[ind_w_shadow]=(shadow[*,*,ii])[ind_w_shadow]-grid
    shadow_new[*,*,ii]=temp
  endif else begin
    if (num_w_shadow gt 0 and num_w_good le 100) then begin
      temp=shadow_new[*,*,ii]
      temp[ind_w_shadow]=(shadow[*,*,ii])[ind_w_shadow]-shadowbase[ind_w_shadow]
      shadow_new[*,*,ii]=temp
    endif
  endelse

endfor

FileName =tempfile+'\IDW_shadow_darkness'
Envi_Write_Envi_File,shadow_new,Out_Name = FileName,Map_info = map_Info
print, 'finish IDW shadow darkness', floor((systime(1)-t0)/3600), 'h',floor(((systime(1)-t0) mod 3600)/60),'m',(systime(1)-t0) mod 60,'s'


;detect shadow from the shadow index
;step 1 get initial mask from k-means classification
mask_shadow_ini=mask
;collect samples using systematic sampling method
n_sample_kmean=10000.0
;for land surface
land_shadow_p=where(shadow_new lt 0 and water_n eq 1,num_land_shadow,/L64)
if (num_land_shadow gt 100) then begin
  n_sample_kmean=min([n_sample_kmean,num_land_shadow])
  inter_sample=floor(num_land_shadow/n_sample_kmean)
  index_sample=indgen(n_sample_kmean)*inter_sample  ;find the location of samples
  sample_shadow=fltarr(1,n_sample_kmean)
  sample_shadow[0,*]=shadow_new[land_shadow_p[index_sample]] ;extract shadow index of samples and store them in a vector
;use k-means to classify shadow samples into two classes
center_class=K_means(sample_shadow,50,2)
print,'centers of shadow and nonshadow pixels on land:',center_class



;classify each shadow image by k-means centers
for ib=0,n_image-1, 1 do begin
  ind_shadow_ib=where(shadow_new[*,*,ib] lt 0 and water eq 1)
  shadow_i=(shadow_new[*,*,ib])[ind_shadow_ib]
  dis_c1=abs(shadow_i-center_class[0])
  dis_c2=abs(shadow_i-center_class[1])
  temp=mask_shadow_ini[*,*,ib]
  temp[ind_shadow_ib]=dis_c1 ge dis_c2
  mask_shadow_ini[*,*,ib]=temp
endfor
endif

;for water surface
n_sample_kmean=10000.0
water_shadow_p=where(shadow_new lt 0 and water_n eq 0,num_water_shadow,/L64)
if (num_water_shadow gt 100) then begin
n_sample_kmean=min([n_sample_kmean,num_water_shadow])
inter_sample=floor(num_water_shadow/n_sample_kmean)
index_sample=indgen(n_sample_kmean)*inter_sample  ;find the location of samples
sample_shadow=fltarr(1,n_sample_kmean)
sample_shadow[0,*]=shadow_new[water_shadow_p[index_sample]] ;extract shadow index of samples and store them in a vector
;use k-means to classify shadow samples into two classes
center_class=K_means(sample_shadow,50,2)
print,'centers of shadow and nonshadow pixels on water:',center_class

;classify each shadow image by k-means centers
for ib=0,n_image-1, 1 do begin
  ind_shadow_ib=where(shadow_new[*,*,ib] ne 0 and water eq 0)
  shadow_i=(shadow_new[*,*,ib])[ind_shadow_ib]
  dis_c1=abs(shadow_i-center_class[0])
  dis_c2=abs(shadow_i-center_class[1])
  temp=mask_shadow_ini[*,*,ib]
  temp[ind_shadow_ib]=dis_c1 ge dis_c2
  mask_shadow_ini[*,*,ib]=temp
endfor
endif

print,'finish initial shadow detection'
print, 'time used', floor((systime(1)-t0)/3600), 'h',floor(((systime(1)-t0) mod 3600)/60),'m',(systime(1)-t0) mod 60,'s'

; refine mask for shadow pixels from shadow time-series
for i=0,ns-1,1 do begin
  for j=0,nl-1,1 do begin
    ;only use non-initial-shadow points to compute the mean and sd
    ind_valid=where(mask_shadow_ini[i,j,*] eq 1,num_nonc)
    if (num_nonc ge 2) then begin
      sample=(shadow[i,j,*])[ind_valid]
      b2_mean=mean(sample)
      b2_sd=stddev(sample)
      ;refine initial shadow
      ind_shadow=where(shadow[i,j,*] lt b2_mean and mask_shadow_ini[i,j,*] eq 0, num_shadow)  ;consider edge pixels   
      if (num_shadow gt 0) then begin
        temp=mask[i,j,*]
        temp[ind_shadow]=0
        mask[i,j,*]=temp
      endif
      ;add shadow from non-initial shadow
       ind_shadow=where(shadow[i,j,*] lt b2_mean-B_shadow*b2_sd and shadow[i,j,*] lt dn_max*0.5 and mask2[i,j,*] eq 0, num_shadow)    
      if (num_shadow gt 0) then begin   
        temp=mask[i,j,*]
        temp[ind_shadow]=0
        mask[i,j,*]=temp
      endif
      ;for edge pixels
      ind_shadow_edge=where(shadow[i,j,*] lt b2_mean-(B_shadow+1.0)*b2_sd and shadow[i,j,*] lt dn_max*0.5 and mask2[i,j,*] eq 99, num_shadow)  ;edge pixels using less strict threshold     
      if (num_shadow gt 0) then begin
        temp=mask[i,j,*]
        temp[ind_shadow_edge]=0
        mask[i,j,*]=temp
      endif
    endif else begin
      mask[i,j,*]=mask_shadow_ini[i,j,*]
    endelse
  endfor
endfor

print,'finish final shadow detection!'
print, 'time used', floor((systime(1)-t0)/3600), 'h',floor(((systime(1)-t0) mod 3600)/60),'m',(systime(1)-t0) mod 60,'s'
mask_shadow_ini=0

;correct isolated shadow
for ii=0,n_image-1, 1 do begin
  diff=1000
  itime=0
  while (diff ge 5 and itime le 5) do begin
    mask0=mask[*,*,ii]
    for i=0, ns-1, 1 do begin
      for j=0, nl-1, 1 do begin
        ;moving window
        if (mask[i,j,ii] eq 0) then begin
          a1=max([0, i-1])
          a2=min([ns-1, i+1])
          b1=max([0, j-1])
          b2=min([nl-1, j+1])
          mask_win=mask0[a1:a2,b1:b2]
          ind_c=where(mask_win eq 0, num_c)
          if (num_c le 3 ) then mask[i,j,ii]=1        ;missmarked if isolate
        endif
      endfor
    endfor
    diff=total(abs(mask[*,*,ii]- mask0))
    itime=itime+1
  endwhile
endfor


;buffer shadow by moving window
shadow1=mask
for i=0,ns-1,1 do begin
  for j=0,nl-1,1 do begin
    for ii=0,n_image-1, 1 do begin

      ;get the buffer zone
      if (mask[i,j,ii] eq 0) then begin
        a1=max([0, i-buffer])
        a2=min([ns-1, i+buffer])
        b1=max([0, j-buffer])
        b2=min([nl-1, j+buffer])
        ind_nonback=where(mask[a1:a2,b1:b2,ii] ne 3 and mask[a1:a2,b1:b2,ii] ne 2)
        temp=shadow1[a1:a2,b1:b2,ii]
        temp[ind_nonback]=0
        shadow1[a1:a2,b1:b2,ii]=temp
      endif

    endfor
  endfor
endfor
mask=shadow1

print,'Obtain the final cloud and shadow mask!'

;;output the results
FileName =FileName0+'_cloud_mask_ATSA'
Envi_Write_Envi_File,mask,Out_Name = FileName,Map_info = map_Info




print, 'time used', floor((systime(1)-t0)/3600), 'h',floor(((systime(1)-t0) mod 3600)/60),'m',(systime(1)-t0) mod 60,'s'


end