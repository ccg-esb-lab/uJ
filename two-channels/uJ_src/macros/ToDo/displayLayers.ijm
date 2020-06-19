print("\n> displayLayers");

args=split(getArgument(),",");
Array.print(args);
setupFile=args[0];
print("setupFile:"+setupFile);
currentPos=args[1]; 
print("currentPos:"+currentPos);

thisVariable="relativeIntensity";

/********************************************************************/
//					PARSE PARAMETERS
/********************************************************************/

//Parse user-defined Parameters
expeLabel=getParam(setupFile, "expeLabel");
drugLabel=getParam(setupFile, "drugLabel");
list_pos=split(getParam(setupFile, "list_pos"),',');
list_frames=getParam(setupFile, "list_frames");
list_channel=split(getParam(setupFile, "list_channel"),',');
str_channel=split(getParam(setupFile, "str_channel"),',');
numPos=list_pos.length;
if(indexOf(list_frames,"-")>0){
    from_frame=substring(list_frames, 0, indexOf(list_frames,"-"));
    to_frame=substring(list_frames, indexOf(list_frames,"-")+1);
    list_frames=""+from_frame;
    for(i=from_frame;i<=to_frame; i++){
	  if(i>from_frame)
        list_frames=list_frames+","+i;
    }
}
list_frames=split(list_frames,",");
print("Loading: "+list_pos.length+" positions/"+list_channel.length+" channels/"+list_frames.length+" frames");

/********************************************************************/
//					CREATE DIRECTORY STRUCTURE
/********************************************************************/

pathDATA=getParam(setupFile, "pathDATA");
dirTIF=pathDATA+getParam(setupFile, "dirTIF"); //Input
dirROIS=pathDATA+getParam(setupFile, "dirROIS"); //Input
dirOVERLAY=pathDATA+getParam(setupFile, "dirOVERLAY"); //Input
dirFIGURES=pathDATA+getParam(setupFile, "dirFIGURES"); //Input
dirLAYERS=pathDATA+getParam(setupFile, "dirLAYERS"); //Output

File.makeDirectory(dirLAYERS);  //Create output directory (level1)

/********************************************************************/
//							MACRO
/********************************************************************/

setBatchMode(true); 

if(currentPos!=""){
	str_rois=getROIFiles(""+dirROIS+""+currentPos+"/", "");
}else{
	str_rois=getROIFiles(dirROIS, "");
}

list_rois=split(str_rois,",");
print("Loading "+list_rois.length+" Images from "+dirROIS);


for(i=1; i<list_rois.length; i++){
	thisPos=substring(list_rois[i],indexOf(list_rois[i], "_xy")+1,indexOf(list_rois[i], "_xy")+5);
	thisFrame=substring(list_rois[i],indexOf(list_rois[i], ".zip")-3,indexOf(list_rois[i], ".zip"));	
	print(i+": Displaying "+" pos="+thisPos+", frame="+thisFrame);

	File.makeDirectory(dirLAYERS+"/"+thisPos);  //Create output directory (level3)

	//Open images to extract fluorescence intensity
	
	

	
	fileNameDIC=expeLabel+"_"+thisPos+"_DIC_"+thisFrame+".tif";
	open(dirTIF+""+thisPos+"/DIC/"+fileNameDIC);
	rename("DIC");
	
	fileNameOverlay=expeLabel+"_"+thisVariable+"_"+thisPos+"_"+thisFrame+".tif";
	open(dirOVERLAY+""+thisVariable+"/"+thisPos+"/"+fileNameOverlay);
		
	fileNameGFP=expeLabel+"_"+thisPos+"_GFP_"+thisFrame+".tif";
	open(dirTIF+""+thisPos+"/GFP/"+fileNameGFP);
	rename("GFP");
	run("Merge Channels...", "c2=GFP");
	rename("GFP");
	
	fileNameDsRed=expeLabel+"_"+thisPos+"_DsRed_"+thisFrame+".tif";
	open(dirTIF+""+thisPos+"/DsRed/"+fileNameDsRed);
	rename("DsRed");
	run("Merge Channels...", "c1=DsRed");	
		
	setBackgroundColor(255,255,255);
	run("Images to Stack", "name=Stack title=[] use");
	makeRectangle(12, 115, 580, 360);  //AMP:50 not 94
	run("Crop");
	setBackgroundColor(255,255,255);
	run("Canvas Size...", "width=600 height=400 position=Bottom-Center");
	
	setFont("Serif", 24, "antiliased");
	setColor(0,0,0);
	setJustification("center");
	
	setSlice(1);
	drawString("DIC", getWidth()/2, 35);
	
	setSlice(2);
	drawString("Deviation from mean relative intensity", getWidth()/2, 35);
	
	setSlice(3);
	drawString("GFP", getWidth()/2, 35);

	setSlice(4);
	drawString("DsRed", getWidth()/2, 35);
	
	
	/*
	fileName1Dhist=expeLabel+"_1Dhist_t"+parseInt(thisFrame)+".tif";
	fileName2Dhist=expeLabel+"_2Dhist_t"+parseInt(thisFrame)+".tif";
	
	exist1Dhist=File.exists(dirFIGURES+"1Dhist/"+fileName1Dhist);
	exist2Dhist=File.exists(dirFIGURES+"2Dhist/"+fileName2Dhist);

	if((exist1Dhist*exist2Dhist)==1){
		
	
		open(dirFIGURES+"1Dhist/"+fileName1Dhist);
		rename("1Dhist");
	
	
		open(dirFIGURES+"2Dhist/"+fileName2Dhist);
		rename("2Dhist");
	
		run("Concatenate...", "  title=[] image1=Stack image2=1Dhist image3=2Dhist image4=[-- None --]");
	
		run("Make Montage...", "columns=3 rows=2 scale=1");
		print("Saving ");
		fileNameLayers=expeLabel+"_"+thisVariable+"_"+thisPos+"_"+thisFrame+".tif";
		saveAs("Tiff",dirLAYERS+"/"+thisVariable+"/"+thisPos+"/"+fileNameLayers);
		
		
		print("Saving "+dirLAYERS+"/"+thisVariable+"/"+thisPos+"/"+fileNameLayers);	
	}
	*/
	run("Make Montage...", "columns=2 rows=2 scale=1");
	print("Saving ");
		
	fileNameLayers=expeLabel+"_"+thisPos+"_"+thisFrame+".tif";
	saveAs("Tiff",dirLAYERS+"/"+thisPos+"/"+fileNameLayers);
	print("Saving "+dirLAYERS+"/"+thisPos+"/"+fileNameLayers);	

	close("*");
	
	
}


setBatchMode(false); 

/********************************************************************/
//						uJ_functions
/********************************************************************/
function getParam(setupFile, varName){
	filestring=File.openAsString(setupFile);
	rows=split(filestring, "\n"); 
	ret="";
	for(i=0; i<rows.length; i++){ 
		columns=split(rows[i],"="); 
		if(columns[0]==varName)
			ret=columns[1];
	} 
	return ret;
}

function getROIFiles(dirROI, str_rois) {
     list = getFileList(dirROI);
     for (i=0; i<list.length; i++) {
        if (endsWith(list[i], "/"))
           str_rois=str_rois+getROIFiles(""+dirROI+list[i], str_rois);
        else{
        	if (endsWith(list[i], ".zip")){
  				str_rois = str_rois+","+list[i];
  				//print(">"+list[i]);
  			}
        }
     }
     
     return str_rois;
  }
print("Exit");
exit;