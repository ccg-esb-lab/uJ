//requires("1.51");
print("\\Clear"); 

/*******************/
// User-defined parameters

//working_dir="/home/charly/Lab/Image_processing/uJ/";
working_dir="/home/esb/Projects/uJ/local/current/";

pathDATA="/home/esb/Projects/uJ/uJ_data/HT-Ramps/HT13-CAZ/";  // CAZ

pathUJ=working_dir+"uJ_src_pHT/macros/"; //Path to uJ_src
setupFile=pathDATA+"setupCAZ.txt"; //Path to setup file



/****Auxiliar***/
// Run this macro if you have slpitted time-lapses with different set of traps
// Requires a position file defining absolute postitions for each time-lapse
//runMacro(pathUJ+"Pos-filler_2_N-Eclipses.ijm", setupFile);



/****Auxiliar***/
//  Run this macro if you have a splitted time-lapses
//  It merges them into one based on the signal file
//  *requires the signal file
//runMacro(pathUJ+"N_Eclipses_2_Raw.ijm", setupFile);


/*******************/
//Run Macro: Eclipse_2_Raw
//runMacro(pathUJ+"Eclipse_2_Raw.ijm", setupFile);

/*******************/
//Run Macro: Raw_2_TIF  
//runMacro(pathUJ+"Raw_2_TIF.ijm", setupFile);
//exec("ln -s "+pathDATA+"data_raw/ "+pathDATA+"data_tif");
/*******************/
//Run Macro: TIF_2_Montage  (DsRed+GFP)
//runMacro(pathUJ+"TIF_2_Montage.ijm", setupFile);
//runMacro(pathUJ+"TIF_2_Montage-SingleChan.ijm", setupFile);

/*******************/

/*******************/
//Run Macro: TIF_2_Segmentable
//runMacro(pathUJ+"TIF_2_Segmentable.ijm", setupFile);

/****************/
//Run Macro: Segmentable_2_DeepCell
//runMacro(pathUJ+"Segmentable_2_DeepCell.ijm", setupFile);

/*******************/


//Here we run DeepCell

/**************************/
//Run Macro: DeepCell_to_Raw_Maks
//runMacro(pathUJ+"DeepCell_2_RawMasks.ijm", setupFile);

/**************************/




/*******************/
//Run Macro: RawMasks_2_Masks (AUTO)

	
//runMacro(pathUJ+"RawMask_2_Masks.ijm", setupFile);


/*******************/
//Run Macro: TIF_2_Data

//runMacro(pathUJ+"TIF_2_Data.ijm", setupFile);



/*******************/
//Python: analyze_uJ_HT13.ipynb


/*******************/
//Run Macro: Data_2_Overlay
/*
thisVariable="relativeIntensity";
maskChannel="DsRed+GFP";
bgChannel="DIC";  
lutFile="RdYlBu.lut";
args=setupFile+","+thisVariable+","+maskChannel+","+bgChannel+","+lutFile;
runMacro(pathUJ+"Data_2_Overlay.ijm", args);
*/


/*******************/
//Run Macro: Mask_2_Overlay
/*
bgChannel="DIC";  
maskChannel="DsRed+GFP";
lutFile="RdYlBu.lut";
args=setupFile+","+maskChannel+","+bgChannel+","+lutFile;
runMacro(pathUJ+"Mask_2_Overlay.ijm", args);
*/

/*******************/
//Run Macro: TIF_2_Composite  (DsRed+GFP)
//runMacro(pathUJ+"TIF_2_Composite.ijm", setupFile);


/*******************/
//Run Macro: makeMovie
/*
list_pos=split("xy07"); //,xy08,xy09,xy12,xy13,xy17,xy26,xy27,xy32,xy34",",");  //Should be from setup.txt
thisChannel="relativeIntensity";
for(i=0; i<list_pos.length; i++){
	thisPos=list_pos[i];
	args=setupFile+","+thisPos+","+thisChannel;
	runMacro(pathUJ+"makeMovie.ijm", args);
}
*/

