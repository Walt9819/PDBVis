from django.shortcuts import render
from django.http import HttpResponse, FileResponse, JsonResponse
import os
import io

from .ReadPDB import PDBConverter

def modelAvailable(modelID, modelsPath="models/"):
    """
    Return if model with `modelID` is available as `fbx` or `pdb`.
    """
    for type in ["fbx", "pdb"]:
        files = os.listdir(f'{modelsPath}/{type}')
        for fl in files:
            fSplit = fl.split('.')
            if modelID == fSplit[0] and fSplit[-1] == type:
                return type
    return None


def getModel(request, modelID=None):
    if request.method == "GET":
        if len(modelID) != 4:
            return JsonResponse({'Error': 'Invalid model ID, must be 4 characters long.'}, status=404)
        pdbs = os.listdir('models/pdb')

        # get if model is available as fbx, pdb or None
        availableType = modelAvailable(modelID)
        # if not available, download from DB
        if availableType == "pdb":
            raise NotImplementedError("TODO: convert from PDB to FBX")
        if not availableType:
            raise NotImplementedError("TODO: download PDB file from RCSB DB")


        # convert from PDB into FBX
        PDBConverter(input='models/pdb/'+modelID+'.pdb', output='models/fbx/'+modelID+'.fbx')

        buffer = io.open(f'models/fbx/{modelID}.fbx', 'rb')
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='hello.fbx')
        #return JsonResponse({'Message': f'Valid ID {modelID}'}, status=201)
    else:
        return JsonResponse({'Error': 'Invalid method'}, status=404)
