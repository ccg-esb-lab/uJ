print("\n> TIF_2_Data");

args=split(getArgument(),",");
Array.print(args);
setupFile=args[0];
print("setupFile:"+setupFile);
/*
currentPos=args[1]; 
print("currentPos:"+currentPos);
currentChannel=args[2]; 
print("currentChannel:"+currentChannel);
*/
/********************************************************************/
//					PARSE PARAMETERS
/********************************************************************/

//Parse user-defined Parameters
expeLabel=getParam(setupFile, "expeLabel");
drugLabel=getParam(setupFile, "drugLabel");
list_pos=split(getParam(setupFile, "list_pos"),',');
list_frames=getParam(setupFile, "list_frames");
//list_channel=split(getParam(setupFile, "list_channel"),',');
str_channel=split(getParam(setupFile, "str_channel"),',');
segmentable_channel=getParam(setupFile, "segmentable_channel");
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

currentChannel=segmentable_channel;
print("Loading: "+list_pos.length+" positions/"+list_frames.length+" channels/"+str_channel.length+" frames");




/********************************************************************/
//					Setup Run
/********************************************************************/

	
	currentPos="All";
	
	
	labMode=newArray("All","By trap");
  
	Dialog.create("Procedure mode");
	Dialog.addRadioButtonGroup("Mode", labMode, 1, 2, "By trap");
	//Dialog.show();
	//pMode=Dialog.getRadioButton;
	
	pMode="All";
	
	print("Mode: "+pMode);

  	
	if(pMode!="All"){
		//doAll=0;	
		Dialog.create("Select trap");
		columns = 4;
		rows =-floor(-list_pos.length/columns );
	
		Dialog.addRadioButtonGroup("Trap",list_pos,rows,columns,list_pos[0]);
		Dialog.show();
		currentPos=Dialog.getRadioButton;
		list_pos=newArray(currentPos);
		
		
		}


print("currentPos:"+currentPos);

print("currentChannel:"+currentChannel);




/********************************************************************/
//					CREATE DIRECTORY STRUCTURE
/********************************************************************/

pathDATA=getParam(setupFile, "pathDATA");
dirTIF=pathDATA+getParam(setupFile, "dirTIF"); //Input
dirROIS=pathDATA+getParam(setupFile, "dirROIS"); //Input
dirDATA=pathDATA+getParam(setupFile, "dirDATA"); //Output
File.makeDirectory(dirDATA);  //Create output directory (level1)
dirDATA=dirDATA+""+currentChannel+"/";  //???

File.makeDirectory(dirDATA);  //Create output directory (level1)
for(i=0; i<list_pos.length; i++){
	File.makeDirectory(dirDATA+list_pos[i]);  //Create output directory (level2)
}






/********************************************************************/
//							MACRO
/********************************************************************/

setBatchMode(true); 

for(pos=0;pos<list_pos.length;pos++){	

	currentPos=list_pos[pos];

	
	if(currentPos!=""){
		str_rois=getROIFiles(dirROIS+currentPos+"/", "");
	}else{
		str_rois=getROIFiles(dirROIS, "");
	}
	
	
	list_rois=split(str_rois,",");
	print("Loading "+list_rois.length+" Images from "+dirROIS);
	
	
	for(i=1; i<list_rois.length; i++){
		run("Clear Results");
	
		thisPos=substring(list_rois[i],indexOf(list_rois[i], "_xy")+1,indexOf(list_rois[i], "_xy")+5);
		thisFrame=substring(list_rois[i],indexOf(list_rois[i], ".zip")-3,indexOf(list_rois[i], ".zip"));	
		print(i+": Analyzing "+" pos="+thisPos+", frame="+thisFrame);
	
		//Open images to extract fluorescence intensity
		fileNameGFP=expeLabel+"_"+thisPos+"_GFP_"+thisFrame+".tif";
		open(dirTIF+""+thisPos+"/GFP/"+fileNameGFP);
		rename("GFP");
		
		fileNameDsRed=expeLabel+"_"+thisPos+"_DsRed_"+thisFrame+".tif";
		open(dirTIF+""+thisPos+"/DsRed/"+fileNameDsRed);
		rename("DsRed");
		
		//Loads ROI Manager
		roiManager("reset");
		thisChannel="DsRed+GFP";  //TMP
		
		roiManager("Open",dirROIS+""+currentPos+"/"+thisChannel+"/"+list_rois[i]);
		//roiManager("Open",dirROIS+""+thisPos+"/"+thisChannel+"/"+list_rois[i]);
		
		//Now exports data
		fileNameData=expeLabel+"_"+currentPos+"_"+thisFrame+".txt";
		numRois = roiManager("count");
		print("   Exporting "+numRois+" cells from pos:"+currentPos+" frame:"+thisFrame+"");
		run("Clear Results"); 
		for (j=0; j<numRois; j++) {
		
			selectWindow("GFP");
			roiManager("select", j);
			label=call("ij.plugin.frame.RoiManager.getName", j);
	  
			getStatistics(area, mean);
			setResult("id",j, ""+j);
			//setResult("imageDIC", j, fileNameDIC);
			setResult("imageGFP", j, fileNameGFP);
			setResult("imageDsRed", j, fileNameDsRed);
			setResult("pos",j, currentPos);
			setResult("frame",j, thisFrame);
			setResult("roi_label",j, label);
			setResult("GFP", j, mean);
	
			selectWindow("DsRed");
			roiManager("select", j);
			label=call("ij.plugin.frame.RoiManager.getName", j);
	
			getStatistics(area, mean);
			setResult("DsRed", j, mean);	
	  
			updateResults();
			saveAs("Results", dirDATA+""+currentPos+"/"+fileNameData);
			//print("   Exporting "+numRois+" cells from pos:"+thisPos+" frame:"+thisFrame+"");
			
		}  //for rois
		run("Clear Results"); 
		run("Close All");
		roiManager("reset");
		
		
	} //for list_rois
} // for list_pos

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
  				print(">"+list[i]);
  			}
        }
     }
     
     return str_rois;
  }
print("Exit");
exit;