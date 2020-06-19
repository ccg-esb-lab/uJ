print("> Macro");

setupFile=getArgument();
print("setupFile:"+setupFile);

/********************************************************************/
//					PARSE PARAMETERS
/********************************************************************/

// Directory structure
pathDATA=getParam(setupFile, "pathDATA");

dirECLIPSE=pathDATA+getParam(setupFile, "dirECLIPSE");

//(Un-comment as appropriate)
//dirRAW=pathDATA+getParam(setupFile, "dirRAW");
//dirTIF=pathDATA+getParam(setupFile, "dirTIF");
//dirSEGMENTABLE=pathDATA+getParam(setupFile, "dirSEGMENTABLE");
//dirDEEPCELL=pathDATA+getParam(setupFile, "dirDEEPCELL");
//dirRAWMASKS=pathDATA+getParam(setupFile, "dirRAWMASKS");
//dirROIS=pathDATA+getParam(setupFile, "dirROIS");
//dirMASKS=pathDATA+getParam(setupFile, "dirMASKS");
//dirDATA=pathDATA+getParam(setupFile, "dirDATA");

//exec("mkdir "+dirRAW);  //Create output directory

//User-defined Parameters
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
//							MACRO
/********************************************************************/




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

exit;